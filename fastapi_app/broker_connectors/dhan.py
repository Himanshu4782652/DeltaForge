"""
DeltaForge DhanHQ Connector
Handles DhanHQ API order dispatching and JSON payloads.
"""

from typing import Dict, Any
import httpx
from .base import BaseBrokerConnector


class DhanConnector(BaseBrokerConnector):
    def __init__(self, client_id: str, api_key: str, access_token: str, base_url: str = "https://api.dhan.co/v2"):
        super().__init__(client_id, api_key, access_token, base_url)

    def get_auth_headers(self) -> Dict[str, str]:
        return {
            "access-token": self.access_token,
            "client-id": self.client_id,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def build_order_payload(self, leg: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "dhanClientId": self.client_id,
            "correlationId": leg.get("correlation_id", "deltaforge-order"),
            "transactionType": leg.get("action", "BUY").upper(),
            "exchangeSegment": leg.get("exchange_segment", "NSE_FNO"),
            "productType": "INTRADAY",
            "orderType": "MARKET",
            "validity": "DAY",
            "securityId": leg.get("security_id", ""),
            "quantity": leg.get("quantity", 25),
        }

    async def place_order(self, client: httpx.AsyncClient, leg: Dict[str, Any]) -> Dict[str, Any]:
        payload = self.build_order_payload(leg)
        headers = self.get_auth_headers()
        try:
            response = await client.post(
                f"{self.base_url}/orders",
                json=payload,
                headers=headers,
                timeout=2.0,
            )
            return {
                "broker": "dhan",
                "client_id": self.client_id,
                "status_code": response.status_code,
                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            }
        except Exception as exc:
            return {
                "broker": "dhan",
                "client_id": self.client_id,
                "status": "FAILED",
                "error": str(exc),
            }
