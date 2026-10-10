"""
DeltaForge Async Multi-Broker Concurrent Order Dispatcher
Orchestrates parallel non-blocking orders across accounts using asyncio.gather.
"""

import asyncio
from typing import List, Dict, Any
import httpx
from ..broker_connectors.zerodha import ZerodhaConnector
from ..broker_connectors.dhan import DhanConnector
from ..broker_connectors.angel import AngelOneConnector


def get_broker_connector(account: Dict[str, Any]):
    broker = account.get("broker_name", "").lower()
    client_id = account.get("client_id", "")
    api_key = account.get("api_key", "")
    access_token = account.get("access_token", "")

    if broker == "zerodha":
        return ZerodhaConnector(client_id, api_key, access_token)
    elif broker == "dhan":
        return DhanConnector(client_id, api_key, access_token)
    elif broker == "angelone":
        return AngelOneConnector(client_id, api_key, access_token)
    else:
        raise ValueError(f"Unsupported broker: {broker}")


async def dispatch_account_strategy(
    client: httpx.AsyncClient,
    account: Dict[str, Any],
    strategy_legs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Executes all strategy legs sequentially or concurrently for a single broker account.
    """
    try:
        connector = get_broker_connector(account)
        results = []
        for leg in strategy_legs:
            leg_res = await connector.place_order(client, leg)
            results.append(leg_res)
        
        return {
            "account_id": account.get("id"),
            "broker": account.get("broker_name"),
            "client_id": account.get("client_id"),
            "status": "SUCCESS",
            "legs": results,
        }
    except Exception as exc:
        return {
            "account_id": account.get("id"),
            "broker": account.get("broker_name"),
            "client_id": account.get("client_id"),
            "status": "FAILED",
            "error": str(exc),
        }


async def dispatch_multi_account_broadcast(
    accounts: List[Dict[str, Any]],
    strategy_legs: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Broadcasts orders concurrently across ALL linked accounts using asyncio.gather.
    """
    async with httpx.AsyncClient() as client:
        tasks = [
            dispatch_account_strategy(client, acc, strategy_legs)
            for acc in accounts
            if acc.get("is_active", True)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        formatted_results = []
        for res in results:
            if isinstance(res, Exception):
                formatted_results.append({"status": "EXCEPTION", "error": str(res)})
            else:
                formatted_results.append(res)

        return formatted_results
