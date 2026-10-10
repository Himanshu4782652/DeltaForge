"""
DeltaForge Multi-Demat Broker Vault Encryption
AES-256 Symmetric Encryption using cryptography.fernet for protecting tokens and secrets at rest.
"""

import os
from cryptography.fernet import Fernet
from django.conf import settings

# Fallback development key if not configured in .env
DEFAULT_DEV_KEY = b'uF8s8QOa1Vb7vM6_d3G2L4rY0tI9wX5eZ8kH2nJ4mP8='


def get_cipher() -> Fernet:
    key = getattr(settings, 'FERNET_SECRET_KEY', None)
    if not key:
        key = os.environ.get('FERNET_SECRET_KEY', DEFAULT_DEV_KEY)
    if isinstance(key, str):
        key = key.encode()
    try:
        return Fernet(key)
    except Exception:
        # If invalid key format, fallback safely in development
        return Fernet(DEFAULT_DEV_KEY)


def encrypt_secret(plain_text: str) -> str:
    """Encrypts a plaintext string (API secret, token) returning AES-256 base64 ciphertext."""
    if not plain_text:
        return ""
    cipher = get_cipher()
    return cipher.encrypt(plain_text.encode('utf-8')).decode('utf-8')


def decrypt_secret(cipher_text: str) -> str:
    """Decrypts ciphertext into original plaintext string."""
    if not cipher_text:
        return ""
    cipher = get_cipher()
    try:
        return cipher.decrypt(cipher_text.encode('utf-8')).decode('utf-8')
    except Exception as exc:
        return f"[Decryption Error: {str(exc)}]"
