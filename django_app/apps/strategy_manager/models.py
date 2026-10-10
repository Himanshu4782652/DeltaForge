import uuid
from django.db import models
from django_app.apps.authentication.models import User
from django_app.apps.broker_vault.models import BrokerAccount


class StrategyConfig(models.Model):
    CATEGORY_CHOICES = [
        ('neutral', 'Market Neutral (Straddles / Strangles)'),
        ('bullish', 'Bullish (Call Debit / Put Credit Spreads)'),
        ('bearish', 'Bearish (Put Debit / Call Credit Spreads)'),
    ]

    INDEX_CHOICES = [
        ('NIFTY', 'Nifty 50'),
        ('BANKNIFTY', 'Bank Nifty'),
        ('SENSEX', 'BSE Sensex'),
        ('CRUDEOIL', 'MCX Crude Oil'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="e.g. Intraday Delta-Neutral Straddle")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='neutral')
    target_index = models.CharField(max_length=20, choices=INDEX_CHOICES, default='NIFTY')
    description = models.TextField(blank=True, default='')
    legs_formula = models.JSONField(
        default=list,
        help_text="JSON structure defining legs (e.g. [{'type': 'CE', 'action': 'SELL', 'offset': 'ATM', 'lots': 1}])"
    )
    square_off_time = models.TimeField(default="15:15:00", help_text="3:15 PM mandatory hard exit risk trigger")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} [{self.target_index}]"


class TradeExecutionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='execution_logs')
    strategy = models.ForeignKey(StrategyConfig, on_delete=models.SET_NULL, null=True, blank=True)
    broker_account = models.ForeignKey(BrokerAccount, on_delete=models.CASCADE, related_name='trades')
    order_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=30)  # "SUCCESS", "FAILED", "PARTIAL"
    response_payload = models.JSONField(default=dict)
    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.broker_account.account_alias} - {self.status} @ {self.executed_at.strftime('%H:%M:%S')}"
