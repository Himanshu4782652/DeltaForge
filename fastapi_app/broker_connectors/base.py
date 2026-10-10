"""
DeltaForge Abstract Broker Connector
Standardized interface for dispatching orders and querying margins across Indian brokers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import httpx


class BaseBrokerConnector(ABC):
    def __init__(self, client_id: str, api_key: str, access_token: str, base_url: str):
        self.client_id = client_id
        self.api_key = api_key
        self.access_token = access_token
        self.base_url = base_url

    @abstractmethod
    def build_order_payload(self, leg: Dict[str, Any]) -> Dict[str, Any]:
        """Convert standard strategy leg format to broker-specific API schema."""
        pass

    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """Return authorization headers required by the broker."""
        pass

    @abstractmethod
    async def place_order(self, client: httpx.AsyncClient, leg: Dict[str, Any]) -> Dict[str, Any]:
        """Execute order asynchronously using httpx."""
        pass
