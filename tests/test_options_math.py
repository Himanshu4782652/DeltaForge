"""
Unit Tests for DeltaForge Options Math & Strike Calculation Engine
"""

import pytest
from fastapi_app.options_math.strike_calculator import calculate_strike_buckets
from fastapi_app.options_math.greeks import calculate_black_scholes_greeks


def test_nifty_atm_rounding():
    # Spot 25024 -> Closest 50-strike is 25000
    res1 = calculate_strike_buckets("NIFTY", 25024.0)
    assert res1["atm_strike"] == 25000
    assert res1["calls"]["itm_1"] == 24950
    assert res1["calls"]["otm_1"] == 25050
    assert res1["puts"]["itm_1"] == 25050
    assert res1["puts"]["otm_1"] == 24950

    # Spot 25026 -> Closest 50-strike is 25050
    res2 = calculate_strike_buckets("NIFTY", 25026.0)
    assert res2["atm_strike"] == 25050


def test_banknifty_strike_intervals():
    # BankNifty uses 100-point strike spacing
    res = calculate_strike_buckets("BANKNIFTY", 51240.0)
    assert res["strike_interval"] == 100
    assert res["atm_strike"] == 51200
    assert res["calls"]["itm_1"] == 51100
    assert res["calls"]["otm_1"] == 51300


def test_black_scholes_call_put_greeks():
    # Call option should have positive delta (0 to 1)
    call_greeks = calculate_black_scholes_greeks(
        spot=25000, strike=25000, time_to_expiry_years=5 / 365, iv=0.15, option_type="CE"
    )
    assert 0.45 <= call_greeks["delta"] <= 0.55
    assert call_greeks["theta_day"] < 0  # Options lose value with time

    # Put option should have negative delta (-1 to 0)
    put_greeks = calculate_black_scholes_greeks(
        spot=25000, strike=25000, time_to_expiry_years=5 / 365, iv=0.15, option_type="PE"
    )
    assert -0.55 <= put_greeks["delta"] <= -0.45

    # Net delta of ATM straddle (long call + long put) should be approximately 0.0
    net_straddle_delta = round(call_greeks["delta"] + put_greeks["delta"], 2)
    assert abs(net_straddle_delta) <= 0.05
