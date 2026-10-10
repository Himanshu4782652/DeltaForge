"""
DeltaForge Strike Calculation Engine
Computes dynamic ATM (At-The-Money), ITM (In-The-Money), and OTM (Out-Of-The-Money) strikes
based on live index spot rate, index lot intervals, and weekly expiry rules.
"""

from typing import Dict, Any
from enum import Enum


class IndexSymbol(str, Enum):
    NIFTY = "NIFTY"
    BANKNIFTY = "BANKNIFTY"
    SENSEX = "SENSEX"
    FINNIFTY = "FINNIFTY"


INDEX_CONFIGS: Dict[str, Dict[str, Any]] = {
    "NIFTY": {
        "strike_interval": 50,
        "lot_size": 25,
        "default_expiry_day": "Tuesday",
        "exchange": "NFO",
    },
    "BANKNIFTY": {
        "strike_interval": 100,
        "lot_size": 15,
        "default_expiry_day": "Thursday",
        "exchange": "NFO",
    },
    "SENSEX": {
        "strike_interval": 100,
        "lot_size": 10,
        "default_expiry_day": "Wednesday",
        "exchange": "BFO",
    },
    "FINNIFTY": {
        "strike_interval": 50,
        "lot_size": 25,
        "default_expiry_day": "Tuesday",
        "exchange": "NFO",
    },
}


def calculate_strike_buckets(index_name: str, spot_price: float, steps: int = 3) -> Dict[str, Any]:
    """
    Computes ATM, ITM, and OTM strike ladders.
    
    Args:
        index_name: e.g. "NIFTY", "BANKNIFTY", "SENSEX"
        spot_price: current real-time market spot price
        steps: number of strikes above and below ATM to generate
    """
    symbol = index_name.upper()
    config = INDEX_CONFIGS.get(symbol, {"strike_interval": 50, "lot_size": 25, "exchange": "NFO"})
    interval = config["strike_interval"]

    # Calculate closest ATM
    atm_strike = round(spot_price / interval) * interval

    # Generate Call / Put strike buckets
    itm_calls = [atm_strike - (i * interval) for i in range(1, steps + 1)]
    otm_calls = [atm_strike + (i * interval) for i in range(1, steps + 1)]
    itm_puts = [atm_strike + (i * interval) for i in range(1, steps + 1)]
    otm_puts = [atm_strike - (i * interval) for i in range(1, steps + 1)]

    return {
        "index": symbol,
        "spot_price": spot_price,
        "strike_interval": interval,
        "lot_size": config["lot_size"],
        "atm_strike": atm_strike,
        "calls": {
            "itm_1": atm_strike - interval,
            "itm_ladder": itm_calls,
            "atm": atm_strike,
            "otm_1": atm_strike + interval,
            "otm_ladder": otm_calls,
        },
        "puts": {
            "itm_1": atm_strike + interval,
            "itm_ladder": itm_puts,
            "atm": atm_strike,
            "otm_1": atm_strike - interval,
            "otm_ladder": otm_puts,
        },
    }
