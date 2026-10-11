"""
DeltaForge Initial Seed Script
Populates initial Admin, Analyst, 5 Family Demat Accounts, and Core Quantitative Strategies.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')
django.setup()

from django_app.apps.authentication.models import User
from django_app.apps.broker_vault.models import BrokerAccount
from django_app.apps.strategy_manager.models import StrategyConfig


def seed_data():
    print("Seeding DeltaForge initial quantitative configuration...")

    # 1. Create or get Admin & Analyst users
    admin_user, _ = User.objects.get_or_create(
        username="himanshu",
        defaults={
            "email": "himanshusriwastava111@gmail.com",
            "role": "admin",
            "is_staff": True,
            "is_superuser": True,
        }
    )
    admin_user.set_password("deltaforge2026")
    admin_user.save()

    analyst_user, _ = User.objects.get_or_create(
        username="aditya",
        defaults={
            "email": "aditya@deltaforge.local",
            "role": "analyst",
            "is_staff": True,
        }
    )
    analyst_user.set_password("adityaquant2026")
    analyst_user.save()

    print(f"-> Users initialized: {admin_user.username} (Admin), {analyst_user.username} (Analyst)")

    # 2. Seed 5 Family Demat Accounts
    accounts_info = [
        ("ACC_01 (Aditya Demat)", "zerodha", "AB1234", "kite_key_01", "kite_token_mock_01"),
        ("ACC_02 (Family Demat)", "dhan", "DH9876", "dhan_key_02", "dhan_token_mock_02"),
        ("ACC_03 (Family Demat)", "angelone", "AG5432", "angel_key_03", "angel_token_mock_03"),
        ("ACC_04 (Family Demat)", "zerodha", "CD5678", "kite_key_04", "kite_token_mock_04"),
        ("ACC_05 (Family Demat)", "dhan", "DH1122", "dhan_key_05", "dhan_token_mock_05"),
    ]

    for alias, broker, client_id, key, token in accounts_info:
        acc, created = BrokerAccount.objects.get_or_create(
            user=admin_user,
            client_id=client_id,
            defaults={
                "account_alias": alias,
                "broker_name": broker,
                "api_key": key,
                "is_active": True,
            }
        )
        acc.set_api_secret(f"secret_{client_id}")
        acc.set_access_token(token)
        acc.save()
        print(f"-> Broker Account vaulted: {alias} [{broker.upper()} - {client_id}]")

    # 3. Seed Core Quantitative Strategies
    strategies = [
        {
            "name": "Intraday Delta-Neutral Straddle",
            "category": "neutral",
            "target_index": "NIFTY",
            "description": "Systematic delta-neutral options harvesting. Sells ATM CE and ATM PE simultaneously to capture high intraday Theta decay with strict 3:15 PM hard square-off.",
            "legs_formula": [
                {"type": "CE", "action": "SELL", "offset": "ATM", "lots": 1},
                {"type": "PE", "action": "SELL", "offset": "ATM", "lots": 1},
            ],
            "square_off_time": "15:15:00",
        },
        {
            "name": "Nifty Bull Call Debit Spread",
            "category": "bullish",
            "target_index": "NIFTY",
            "description": "Defined risk directional strategy. Buys ATM Call and sells OTM1 Call to reduce net debit and achieve high risk-to-reward ratio.",
            "legs_formula": [
                {"type": "CE", "action": "BUY", "offset": "ATM", "lots": 1},
                {"type": "CE", "action": "SELL", "offset": "OTM1", "lots": 1},
            ],
            "square_off_time": "15:15:00",
        },
        {
            "name": "Nifty Bear Put Debit Spread",
            "category": "bearish",
            "target_index": "NIFTY",
            "description": "Capital protection strategy for market corrections. Buys ATM Put and finances premium by selling OTM1 Put.",
            "legs_formula": [
                {"type": "PE", "action": "BUY", "offset": "ATM", "lots": 1},
                {"type": "PE", "action": "SELL", "offset": "OTM1", "lots": 1},
            ],
            "square_off_time": "15:15:00",
        },
        {
            "name": "BankNifty High-Volatility Straddle",
            "category": "neutral",
            "target_index": "BANKNIFTY",
            "description": "High-premium harvesting for Bank Nifty weekly cycle (Thursday expiry) with dynamic 100-point strike boundaries.",
            "legs_formula": [
                {"type": "CE", "action": "SELL", "offset": "ATM", "lots": 1},
                {"type": "PE", "action": "SELL", "offset": "ATM", "lots": 1},
            ],
            "square_off_time": "15:15:00",
        },
        {
            "name": "Crude Oil Mid-Month Theta Decay",
            "category": "neutral",
            "target_index": "CRUDEOIL",
            "description": "Commodity options theta harvester targeting mid-month expiry cycles with low margin requirements (~₹8,000/lot).",
            "legs_formula": [
                {"type": "CE", "action": "SELL", "offset": "OTM1", "lots": 1},
                {"type": "PE", "action": "SELL", "offset": "OTM1", "lots": 1},
            ],
            "square_off_time": "23:15:00",
        },
    ]

    for item in strategies:
        strat, created = StrategyConfig.objects.get_or_create(
            name=item["name"],
            defaults={
                "category": item["category"],
                "target_index": item["target_index"],
                "description": item["description"],
                "legs_formula": item["legs_formula"],
                "square_off_time": item["square_off_time"],
                "created_by": analyst_user,
            }
        )
        print(f"-> Strategy Configured: {strat.name} [{strat.target_index}]")

    print("\nDeltaForge pilot database successfully seeded!")


if __name__ == "__main__":
    seed_data()
