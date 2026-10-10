import uuid
from django.db import models
from django.utils import timezone
from django_app.apps.authentication.models import User
from .encryption import encrypt_secret, decrypt_secret


class BrokerAccount(models.Model):
    BROKER_CHOICES = [
        ('zerodha', 'Zerodha KiteConnect'),
        ('dhan', 'DhanHQ'),
        ('angelone', 'Angel One SmartAPI'),
        ('firstock', 'Firstock'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='broker_accounts')
    account_alias = models.CharField(max_length=100, default='Family Account', help_text="e.g. Aditya Demat 01")
    broker_name = models.CharField(max_length=20, choices=BROKER_CHOICES)
    client_id = models.CharField(max_length=50)
    api_key = models.CharField(max_length=255)
    encrypted_api_secret = models.TextField(blank=True, default='', help_text="AES-256 encrypted")
    encrypted_access_token = models.TextField(blank=True, default='', help_text="AES-256 encrypted daily session token")
    token_expiry = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_api_secret(self, plain_secret: str):
        self.encrypted_api_secret = encrypt_secret(plain_secret)

    def get_api_secret(self) -> str:
        return decrypt_secret(self.encrypted_api_secret)

    def set_access_token(self, plain_token: str, expiry_datetime=None):
        self.encrypted_access_token = encrypt_secret(plain_token)
        if expiry_datetime:
            self.token_expiry = expiry_datetime
        else:
            # Default to end of trading day (23:59:59)
            now = timezone.now()
            self.token_expiry = now.replace(hour=23, minute=59, second=59)

    def get_access_token(self) -> str:
        return decrypt_secret(self.encrypted_access_token)

    def is_token_valid(self) -> bool:
        if not self.encrypted_access_token:
            return False
        if not self.token_expiry:
            return True
        return timezone.now() < self.token_expiry

    def __str__(self):
        return f"{self.account_alias} ({self.get_broker_name_display()} - {self.client_id})"
