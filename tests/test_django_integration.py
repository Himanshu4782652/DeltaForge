"""
Integration Tests for DeltaForge Django Application
"""

import os
import django
import pytest

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')
django.setup()

from django.test import Client
from django_app.apps.authentication.models import User
from django_app.apps.broker_vault.models import BrokerAccount
from django_app.apps.strategy_manager.models import StrategyConfig, TradeExecutionLog


@pytest.mark.django_db
def test_user_roles():
    admin = User.objects.filter(role="admin").first()
    assert admin is not None
    assert admin.is_admin_lead() is True

    analyst = User.objects.filter(role="analyst").first()
    assert analyst is not None
    assert analyst.is_analyst() is True


@pytest.mark.django_db
def test_seeded_accounts_vault():
    accounts = BrokerAccount.objects.filter(is_active=True)
    assert accounts.count() >= 5
    for acc in accounts:
        assert acc.is_token_valid() is True
        assert len(acc.get_access_token()) > 0


@pytest.mark.django_db
def test_dashboard_view():
    client = Client()
    response = client.get("/")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "DELTAFORGE" in content
    assert "Strategy Hub" in content
    assert "Broker Vault" in content


@pytest.mark.django_db
def test_strategy_legs_htmx_partial():
    strategy = StrategyConfig.objects.first()
    assert strategy is not None

    client = Client()
    response = client.get(f"/strategy/{strategy.id}/legs/?spot=25000.0")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "TRADE ALL EXECUTE" in content
    assert strategy.name in content
