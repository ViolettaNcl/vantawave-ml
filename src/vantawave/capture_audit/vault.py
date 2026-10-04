from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import secrets
import threading


@dataclass
class SecretEntry:
    secret: str
    ssid: str
    security: str
    expires_at: datetime


class EphemeralSecretVault:
    def __init__(self, ttl_minutes: int = 10):
        self.ttl = timedelta(minutes=ttl_minutes)
        self._items: dict[str, SecretEntry] = {}
        self._lock = threading.Lock()

    def _purge(self):
        now = datetime.now(timezone.utc)
        expired = [
            token for token, item in self._items.items()
            if item.expires_at <= now
        ]
        for token in expired:
            self._items.pop(token, None)

    def put(self, *, secret: str, ssid: str, security: str) -> str:
        token = secrets.token_urlsafe(24)
        with self._lock:
            self._purge()
            self._items[token] = SecretEntry(
                secret=secret,
                ssid=ssid,
                security=security,
                expires_at=datetime.now(timezone.utc) + self.ttl,
            )
        return token

    def get(self, token: str) -> SecretEntry:
        with self._lock:
            self._purge()
            item = self._items.get(token)
            if item is None:
                raise KeyError(token)
            return item

    def consume(self, token: str) -> SecretEntry:
        with self._lock:
            self._purge()
            item = self._items.pop(token, None)
            if item is None:
                raise KeyError(token)
            return item

    def masked(self, token: str) -> str:
        item = self.get(token)
        return "•" * max(8, min(len(item.secret), 24))


vault = EphemeralSecretVault()
