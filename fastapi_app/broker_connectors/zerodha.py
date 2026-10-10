"""
DeltaForge Zerodha Kite Connect Connector
Handles KiteConnect API order routing and payload transformations.
"""

from typing import Dict, Any
import httpx
from .base import BaseBrokerConnector


class ZerodhaConnector(BaseBrokerConnector):
    def __init__(self, client_id: str, api_key: str, access_token: str, base_url: str = "https://api.kite.trade"):
        super().__init__(client_id, api_key, access_token, base_url)

    def get_auth_headers(self) -> Dict[str, str]:
        return {
            "X-Kite-Version": "3",
            "Authorization": f"token {self.api_key}:{self.access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def build_order_payload(self, leg: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "tradingsymbol": leg.get("tradingsymbol"),
            "exchange": leg.get("exchange", "NFO"),
            "transaction_type": leg.get("action", "BUY").upper(),  # BUY or SELL
            "order_type": leg.get("order_type", "MARKET").upper(),
            "quantity": leg.get("quantity", 25),
            "product": leg.get("product", "MIS").upper(),  # Intraday MIS
            "validity": "DAY",
        }

    async def place_order(self, client: httpx.AsyncClient, leg: Dict[str, Any]) -> Dict[str, Any]:
        payload = self.build_order_payload(leg)
        headers = self.get_auth_headers()
        try:
            response = await client.post(
                f"{self.base_url}/orders/regular",
                data=payload,
                headers=headers,
                timeout=2.0,
            )
            return {
                "broker": "zerodha",
                "client_id": self.client_id,
                "status_code": response.status_code,
                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            }
        except Exception as exc:
            return {
                "broker": "zerodha",
                "client_id": self.client_id,
                "status": "FAILED",
                "error": str(exc),
            }
