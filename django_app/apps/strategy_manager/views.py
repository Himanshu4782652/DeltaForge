import json
import httpx
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import StrategyConfig, TradeExecutionLog
from django_app.apps.broker_vault.models import BrokerAccount

FASTAPI_URL = getattr(settings, 'FASTAPI_URL', 'http://127.0.0.1:8001')

# Default mock spot prices for pilot rendering
INDEX_DEFAULT_SPOTS = {
    "NIFTY": 25000.0,
    "BANKNIFTY": 51200.0,
    "SENSEX": 81500.0,
    "CRUDEOIL": 6400.0,
}


def dashboard_view(request):
    """
    Main Sensibull-style Strategy Hub.
    """
    selected_index = request.GET.get('index', 'NIFTY').upper()
    active_strategies = StrategyConfig.objects.filter(is_active=True)
    
    # Filter strategies by index if matching, else show all
    index_strategies = active_strategies.filter(target_index=selected_index)
    if not index_strategies.exists():
        index_strategies = active_strategies

    # Accounts linked to current user or active family accounts
    if request.user.is_authenticated:
        accounts = BrokerAccount.objects.filter(user=request.user, is_active=True)
    else:
        accounts = BrokerAccount.objects.filter(is_active=True)[:5]

    context = {
        "selected_index": selected_index,
        "spot_price": INDEX_DEFAULT_SPOTS.get(selected_index, 25000.0),
        "strategies": index_strategies,
        "accounts": accounts,
        "fastapi_url": FASTAPI_URL,
    }
    return render(request, "landing.html", context)


def strategy_legs_partial(request, strategy_id):
    """
    HTMX partial endpoint: dynamically computes strike prices via FastAPI
    and renders the Strategy Breakdown / 1-Click 'Trade All' confirmation modal.
    """
    strategy = get_object_or_404(StrategyConfig, id=strategy_id)
    spot_price = float(request.GET.get('spot', INDEX_DEFAULT_SPOTS.get(strategy.target_index, 25000.0)))

    # Fetch dynamic strikes from FastAPI engine
    strikes_data = None
    try:
        with httpx.Client(timeout=2.0) as client:
            res = client.get(f"{FASTAPI_URL}/api/v1/strikes/calculate", params={"index": strategy.target_index, "spot": spot_price})
            if res.status_code == 200:
                strikes_data = res.json().get("data")
    except Exception:
        # Fallback local calculation
        interval = 50 if strategy.target_index == "NIFTY" else 100
        atm = round(spot_price / interval) * interval
        strikes_data = {
            "atm_strike": atm,
            "calls": {"atm": atm, "itm_1": atm - interval, "otm_1": atm + interval},
            "puts": {"atm": atm, "itm_1": atm + interval, "otm_1": atm - interval},
            "lot_size": 25 if strategy.target_index == "NIFTY" else 15,
        }

    # Build concrete trade legs based on strategy formula
    atm_strike = strikes_data.get("atm_strike", spot_price)
    lot_size = strikes_data.get("lot_size", 25)
    resolved_legs = []

    for item in strategy.legs_formula:
        opt_type = item.get("type", "CE").upper()
        action = item.get("action", "SELL").upper()
        offset = item.get("offset", "ATM").upper()
        lots = item.get("lots", 1)

        if offset == "ATM":
            leg_strike = atm_strike
        elif offset == "ITM1":
            leg_strike = strikes_data["calls"]["itm_1"] if opt_type == "CE" else strikes_data["puts"]["itm_1"]
        elif offset == "OTM1":
            leg_strike = strikes_data["calls"]["otm_1"] if opt_type == "CE" else strikes_data["puts"]["otm_1"]
        else:
            leg_strike = atm_strike

        tradingsymbol = f"{strategy.target_index} {leg_strike} {opt_type}"
        resolved_legs.append({
            "action": action,
            "strike": leg_strike,
            "type": opt_type,
            "lots": lots,
            "quantity": lots * lot_size,
            "tradingsymbol": tradingsymbol,
            "delta_est": 0.50 if opt_type == "CE" else -0.50,
            "theta_est": "+₹450/day" if action == "SELL" else "-₹450/day",
        })

    # Get accounts
    if request.user.is_authenticated:
        accounts = BrokerAccount.objects.filter(user=request.user, is_active=True)
    else:
        accounts = BrokerAccount.objects.filter(is_active=True)

    context = {
        "strategy": strategy,
        "spot_price": spot_price,
        "legs": resolved_legs,
        "accounts": accounts,
        "margin_est": len(resolved_legs) * 60000,
        "legs_json": json.dumps(resolved_legs),
    }
    return render(request, "components/trade_modal.html", context)


@csrf_exempt
def execute_trade_all_view(request):
    """
    HTMX trigger: Dispatches parallel orders via FastAPI and logs execution records.
    """
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    strategy_id = request.POST.get("strategy_id")
    strategy = get_object_or_404(StrategyConfig, id=strategy_id)
    legs_json = request.POST.get("legs_json", "[]")
    legs = json.loads(legs_json)

    # Gather accounts to trade
    if request.user.is_authenticated:
        accounts = BrokerAccount.objects.filter(user=request.user, is_active=True)
    else:
        accounts = BrokerAccount.objects.filter(is_active=True)

    accounts_payload = []
    for acc in accounts:
        accounts_payload.append({
            "id": str(acc.id),
            "broker_name": acc.broker_name,
            "client_id": acc.client_id,
            "api_key": acc.api_key,
            "access_token": acc.get_access_token() or "MOCK_TOKEN",
            "is_active": acc.is_active,
        })

    execution_payload = {
        "user_id": str(request.user.id) if request.user.is_authenticated else "pilot-admin",
        "strategy_name": strategy.name,
        "target_index": strategy.target_index,
        "accounts": accounts_payload,
        "strategy_legs": legs,
    }

    try:
        with httpx.Client(timeout=4.0) as client:
            res = client.post(f"{FASTAPI_URL}/api/v1/trade/execute", json=execution_payload)
            response_data = res.json()
    except Exception as exc:
        response_data = {
            "status": "ENGINE_OFFLINE",
            "error": f"Could not reach FastAPI engine @ {FASTAPI_URL}: {str(exc)}",
            "execution_time_ms": 0,
            "results": [],
        }

    # Log execution in database
    for acc in accounts:
        TradeExecutionLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            strategy=strategy,
            broker_account=acc,
            status=response_data.get("status", "EXECUTED"),
            response_payload=response_data,
        )

    return render(request, "components/execution_result.html", {
        "response": response_data,
        "strategy": strategy,
        "accounts_count": len(accounts),
    })
