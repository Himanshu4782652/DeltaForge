"""
DeltaForge Options Greeks & Pricing Analytics
Vectorized Black-Scholes formulas and Greeks estimation for intraday risk control.
"""

import math
from typing import Dict, Any


def norm_cdf(x: float) -> float:
    """Standard normal cumulative distribution function."""
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0


def norm_pdf(x: float) -> float:
    """Standard normal probability density function."""
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def calculate_black_scholes_greeks(
    spot: float,
    strike: float,
    time_to_expiry_years: float,
    risk_free_rate: float = 0.07,  # ~7% RBI repo rate
    iv: float = 0.15,               # 15% Implied Volatility default
    option_type: str = "CE",
) -> Dict[str, float]:
    """
    Computes option theoretical price and primary Greeks (Delta, Gamma, Theta, Vega).
    """
    if time_to_expiry_years <= 0 or iv <= 0 or spot <= 0 or strike <= 0:
        # Expiry intrinsic calculation
        if option_type.upper() == "CE":
            intrinsic = max(0.0, spot - strike)
            delta = 1.0 if spot > strike else 0.0
        else:
            intrinsic = max(0.0, strike - spot)
            delta = -1.0 if spot < strike else 0.0
        return {
            "price": intrinsic,
            "delta": delta,
            "gamma": 0.0,
            "theta_day": 0.0,
            "vega": 0.0,
        }

    sqrt_t = math.sqrt(time_to_expiry_years)
    d1 = (math.log(spot / strike) + (risk_free_rate + 0.5 * iv * iv) * time_to_expiry_years) / (iv * sqrt_t)
    d2 = d1 - iv * sqrt_t

    pdf_d1 = norm_pdf(d1)
    gamma = pdf_d1 / (spot * iv * sqrt_t)
    vega = spot * pdf_d1 * sqrt_t / 100.0  # per 1% change in IV

    if option_type.upper() == "CE":
        price = spot * norm_cdf(d1) - strike * math.exp(-risk_free_rate * time_to_expiry_years) * norm_cdf(d2)
        delta = norm_cdf(d1)
        theta_annual = -(spot * pdf_d1 * iv) / (2.0 * sqrt_t) - risk_free_rate * strike * math.exp(
            -risk_free_rate * time_to_expiry_years
        ) * norm_cdf(d2)
    else:
        price = strike * math.exp(-risk_free_rate * time_to_expiry_years) * norm_cdf(-d2) - spot * norm_cdf(-d1)
        delta = norm_cdf(d1) - 1.0
        theta_annual = -(spot * pdf_d1 * iv) / (2.0 * sqrt_t) + risk_free_rate * strike * math.exp(
            -risk_free_rate * time_to_expiry_years
        ) * norm_cdf(-d2)

    theta_day = theta_annual / 365.0

    return {
        "price": round(price, 2),
        "delta": round(delta, 3),
        "gamma": round(gamma, 5),
        "theta_day": round(theta_day, 2),
        "vega": round(vega, 2),
    }
