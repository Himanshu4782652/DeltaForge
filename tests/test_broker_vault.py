"""
Unit Tests for DeltaForge AES-256 Multi-Demat Broker Vault & Connectors
"""

import pytest
from django_app.apps.broker_vault.encryption import encrypt_secret, decrypt_secret
from fastapi_app.broker_connectors.zerodha import ZerodhaConnector
from fastapi_app.broker_connectors.dhan import DhanConnector
from fastapi_app.broker_connectors.angel import AngelOneConnector


def test_aes_256_symmetric_encryption():
    secret_token = "sess_kite_9948274_secure_alpha"
    encrypted = encrypt_secret(secret_token)

    # Must be encrypted ciphertext, not plaintext
    assert encrypted != secret_token
    assert len(encrypted) > 20

    # Decryption must restore identical original token
    decrypted = decrypt_secret(encrypted)
    assert decrypted == secret_token


def test_zerodha_payload_builder():
    connector = ZerodhaConnector("AB1234", "my_api_key", "my_token")
    leg = {
        "tradingsymbol": "NIFTY 25000 CE",
        "action": "SELL",
        "quantity": 25,
        "exchange": "NFO",
    }
    payload = connector.build_order_payload(leg)
    assert payload["tradingsymbol"] == "NIFTY 25000 CE"
    assert payload["transaction_type"] == "SELL"
    assert payload["product"] == "MIS"
    assert payload["quantity"] == 25


def test_dhan_payload_builder():
    connector = DhanConnector("DH9876", "my_api_key", "my_token")
    leg = {
        "security_id": "49500",
        "action": "BUY",
        "quantity": 50,
    }
    payload = connector.build_order_payload(leg)
    assert payload["dhanClientId"] == "DH9876"
    assert payload["transactionType"] == "BUY"
    assert payload["productType"] == "INTRADAY"
    assert payload["quantity"] == 50


def test_angel_one_payload_builder():
    connector = AngelOneConnector("AG5432", "my_api_key", "my_token")
    leg = {
        "tradingsymbol": "BANKNIFTY 51200 PE",
        "symbol_token": "99120",
        "action": "SELL",
        "quantity": 15,
    }
    payload = connector.build_order_payload(leg)
    assert payload["tradingsymbol"] == "BANKNIFTY 51200 PE"
    assert payload["transactiontype"] == "SELL"
    assert payload["variety"] == "NORMAL"
    assert payload["quantity"] == "15"
