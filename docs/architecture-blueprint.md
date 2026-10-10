# System Architecture Blueprint: Automated Options Trading Platform
**Architecture Choice:** Option C – The Hybrid Python Powerhouse (Django + FastAPI + HTMX)

---

## 1. System Overview & Technology Stack

The platform is designed as a **full-stack Python automated options trading system** combining the administrative robustness of **Django** with the ultra-low latency async performance of **FastAPI**.

* **Web Portal & Admin (Django @ Port 8000):**
  * **Framework:** Django 5.x + HTMX
  * **Responsibilities:** User authentication, Role-Based Access Control (RBAC), Django Admin Panel (for strategy overrides and audit logs), database ORM, and HTMX-powered responsive server-rendered UI.
* **Execution & Pricing Engine (FastAPI @ Port 8001):**
  * **Framework:** FastAPI + `asyncio` + `httpx`
  * **Responsibilities:** Real-time ATM/ITM strike pricing calculation, parallel multi-broker API order dispatching (Zerodha, Dhan, Angel One), WebSocket live ticker streams, and background risk/square-off triggers.
* **Database & Persistence:**
  * **Database:** PostgreSQL (Shared ORM access between Django & FastAPI)
  * **Security:** AES-256 Symmetric Encryption (`cryptography.fernet`) for storing broker API secrets and access tokens.
* **Task Queue & Scheduler:**
  * **Worker System:** Celery / Redis or Async Background Tasks for strict 3:00 PM / 3:15 PM automated position square-off.

---

## 2. High-Level Architecture Diagram

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      1. Pure Python Frontend (HTMX)                    │
 │  - Sensibull-style Strategy Hub (Neutral, Bullish, Bearish Cards)      │
 │  - Index Selector Header (Nifty, Sensex, BankNifty)                    │
 │  - Leg Breakdown Modal & 1-Click "Trade All" Execution                 │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                        (HTMX / Async REST Requests)
                                     │
 ┌───────────────────────────────────▼────────────────────────────────────┐
 │                  2. Django Web Portal (Port 8000)                      │
 │  - Session / JWT Authentication & Security                             │
 │  - Built-in Django Admin (User, Broker Accounts, Audit Logs)          │
 │  - Strategy Configuration Management                                   │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                             (Shared PostgreSQL DB)
                                     │
 ┌───────────────────────────────────┴────────────────────────────────────┐
 │               3. FastAPI Execution Engine (Port 8001)                  │
 │  - /api/v1/strikes/calculate  ➔ Real-Time ATM/ITM Option Formulas     │
 │  - /api/v1/trade/execute      ➔ Concurrent Multi-Broker Order Router   │
 │  - /ws/live-tickers           ➔ High-Frequency Market Data Stream      │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
┌───────────────────┐       ┌───────────────────┐       ┌───────────────────┐
│ Zerodha Kite API  │       │     DhanHQ API    │       │  Angel SmartAPI   │
└───────────────────┘       └───────────────────┘       └───────────────────┘
```

---

## 3. Frontend & Landing Page Architecture (Sensibull-Style)

### Layout Components:
1. **Header & Index Selector:**
   * Index selector toggles: **Nifty, Sensex, BankNifty**.
   * Selecting an index updates the underlying expiry calendar engine (e.g., Tuesday: Nifty, Wednesday: Sensex, Thursday: BankNifty).
2. **Strategy Catalog Grid:**
   * Categorized cards based on market outlook: **Neutral (Straddles/Strangles), Bullish (Call Spreads), Bearish (Put Spreads)**.
   * Built using HTMX for zero-JS dynamic updates: `hx-get="/api/v1/strategies?index=NIFTY"`.
3. **Strategy Detail Modal / Drawer:**
   * Dynamic Leg breakdown showing option strike prices generated dynamically using real-time market spot rates.
   * Displays Max Profit, Max Loss, Margin Requirement, and a **1-Click "Trade All"** button.
4. **External Tool Redirect Portal:**
   * Direct hyperlinks to external screening tools (e.g., Chartink, official NSE stock filters) allowing frictionless analysis.

---

## 4. Authentication, User Roles & Encrypted Broker Vault

### User Roles:
* **Admin / Developer:** System status monitoring, server management, and deployment controls.
* **Analyst / Strategy Creator (Aditya):** Strategy logic publishing, strike bucket offsets, and SEBI/NISM compliance configurations.
* **Client / Family User:** Linking Demat accounts, viewing strategies, and executing trades across assigned accounts.

### Multi-Demat Broker Vault Architecture:
* **Credential Encryption:** API keys and access tokens for Zerodha, Dhan, and Angel One are encrypted at rest using AES-256 before database insertion.
* **Daily OAuth Onboarding:** Users complete a single-click daily login redirect in account settings to refresh session tokens.

---

## 5. Database Schema (Django ORM Models)

```python
# database/models.py
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=20, 
        choices=[('admin', 'Admin'), ('analyst', 'Analyst'), ('client', 'Client')],
        default='client'
    )

class BrokerAccount(models.Model):
    BROKER_CHOICES = [
        ('zerodha', 'Zerodha KiteConnect'),
        ('dhan', 'DhanHQ'),
        ('angelone', 'Angel One SmartAPI'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='broker_accounts')
    broker_name = models.CharField(max_length=20, choices=BROKER_CHOICES)
    client_id = models.CharField(max_length=50)
    api_key = models.CharField(max_length=255)
    encrypted_access_token = models.TextField()  # AES-256 encrypted
    token_expiry = models.DateTimeField()
    is_active = models.BooleanField(default=True)

class StrategyConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100) # e.g. "Nifty Short Straddle"
    target_index = models.CharField(max_length=20) # "NIFTY", "BANKNIFTY", "SENSEX"
    legs_json = models.JSONField() # Formula parameters for strike selection
    square_off_time = models.TimeField(default="15:00:00") # 3:00 PM auto square-off
    is_active = models.BooleanField(default=True)

class TradeExecutionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    strategy = models.ForeignKey(StrategyConfig, on_delete=models.SET_NULL, null=True)
    broker_account = models.ForeignKey(BrokerAccount, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=30) # "SUCCESS", "FAILED", "PARTIAL"
    response_payload = models.JSONField()
    executed_at = models.DateTimeField(auto_now_add=True)
```

---

## 6. FastAPI Execution Engine Blueprint

```python
# execution_engine/main.py
from fastapi import FastAPI, HTTPException
import asyncio
import httpx
from typing import List, Dict

app = FastAPI(title="Options Execution & Calculation Engine")

# --- 1. Strike Price Calculation Engine ---
@app.get("/api/v1/strikes/calculate")
async def calculate_strikes(index_name: str, spot_price: float):
    """
    Computes ATM and ITM/OTM strike buckets dynamically based on spot price.
    """
    strike_gap = 50 if index_name == "NIFTY" else 100
    atm_strike = round(spot_price / strike_gap) * strike_gap
    
    return {
        "index": index_name,
        "spot_price": spot_price,
        "atm_strike": atm_strike,
        "itm_call": atm_strike - strike_gap,
        "itm_put": atm_strike + strike_gap,
        "otm_call": atm_strike + strike_gap,
        "otm_put": atm_strike - strike_gap,
    }

# --- 2. Async Multi-Broker Parallel Order Router ---
async def dispatch_single_order(client: httpx.AsyncClient, account: Dict, order_payload: Dict) -> Dict:
    """Dispatches order to individual broker API in parallel."""
    headers = {"Authorization": f"Bearer {account['access_token']}"}
    try:
        response = await client.post(
            f"{account['api_endpoint']}/orders",
            json=order_payload,
            headers=headers,
            timeout=2.0  # 2-second timeout
        )
        return {"account_id": account['id'], "broker": account['broker_name'], "status": response.status_code, "data": response.json()}
    except Exception as e:
        return {"account_id": account['id'], "broker": account['broker_name'], "status": "FAILED", "error": str(e)}

@app.post("/api/v1/trade/execute")
async def execute_trade_all(user_id: str, strategy_id: str, broker_accounts: List[Dict], strategy_legs: List[Dict]):
    """
    Executes strategy legs concurrently across all active broker accounts for the user.
    """
    async with httpx.AsyncClient() as client:
        tasks = [
            dispatch_single_order(client, acc, {"legs": strategy_legs})
            for acc in broker_accounts
        ]
        execution_results = await asyncio.gather(*tasks)

    return {"status": "COMPLETED", "summary": execution_results}
```

---

## 7. Recommended Directory Structure

```text
trading_platform/
├── manage.py                   # Django management script
├── django_app/                 # Django Core (Port 8000)
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── apps/
│       ├── authentication/     # Login, Signup, RBAC
│       ├── broker_vault/       # Encrypted token storage & OAuth
│       └── strategy_manager/   # Django Admin & Strategy Models
├── fastapi_app/                # FastAPI Engine (Port 8001)
│   ├── main.py
│   ├── options_math/           # Strike selection & formula logic
│   ├── broker_connectors/      # Zerodha, Dhan, Angel One SDK handlers
│   └── execution_router/       # Async parallel order dispatcher
├── templates/                  # Jinja2 / HTMX Server-Rendered UI
│   ├── landing.html            # Sensibull-style hub
│   ├── auth/                   # Login & Signup views
│   └── components/             # HTMX modals & strategy cards
├── requirements.txt            # Dependencies (django, fastapi, httpx, cryptography, etc.)
└── docker-compose.yml          # Container configuration for PostgreSQL, Django, FastAPI
```
