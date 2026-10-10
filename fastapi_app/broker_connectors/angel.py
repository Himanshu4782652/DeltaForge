"""
DeltaForge Angel One SmartAPI Connector
Handles Angel One SmartAPI order dispatching.
"""

from typing import Dict, Any
import httpx
from .base import BaseBrokerConnector


class AngelOneConnector(BaseBrokerConnector):
    def __init__(self, client_id: str, api_key: str, access_token: str, base_url: str = "https://apiconnect.angelone.in"):
        super().__init__(client_id, api_key, access_token, base_url)

    def get_auth_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": "127.0.0.1",
            "X-ClientPublicIP": "127.0.0.1",
            "X-MACAddress": "fe80::1",
            "X-PrivateKey": self.api_key,
        }

    def build_order_payload(self, leg: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "variety": "NORMAL",
            "tradingsymbol": leg.get("tradingsymbol", ""),
            "symboltoken": leg.get("symbol_token", ""),
            "transactiontype": leg.get("action", "BUY").upper(),
            "exchange": leg.get("exchange", "NFO"),
            "ordertype": "MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "quantity": str(leg.get("quantity", 25)),
        }

    async def place_order(self, client: httpx.AsyncClient, leg: Dict[str, Any]) -> Dict[str, Any]:
        payload = self.build_order_payload(leg)
        headers = self.get_auth_headers()
        try:
            response = await client.post(
                f"{self.base_url}/rest/secure/angelbroking/order/v1/placeOrder",
                json=payload,
                headers=headers,
                timeout=2.0,
            )
            return {
                "broker": "angelone",
                "client_id": self.client_id,
                "status_code": response.status_code,
                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            }
        except Exception as exc:
            return {
                "broker": "angelone",
                "client_id": self.client_id,
                "status": "FAILED",
                "error": str(exc),
            }
