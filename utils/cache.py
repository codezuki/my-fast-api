import logging
import threading
import time
from collections.abc import Callable
from typing import Any, Optional

logger = logging.getLogger(__name__)

class InMemoryCache:
    def __init__(self, default_ttl: int = 120):
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if expires_at and time.time() > expires_at:
                del self._store[key]
                return None
            return value

    def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[int] = None,
    ) -> Any:
        cached = self.get(key)
        if cached is not None:
            logger.info("Cache hit: %s", key)
            return cached

        logger.info("Cache miss: %s", key)
        value = factory()
        if value is not None:
            self.set(key, value, ttl)
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = self.default_ttl if ttl is None else ttl
        expires_at = time.time() + ttl if ttl and ttl > 0 else 0.0
        with self._lock:
            self._store[key] = (value, expires_at)

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def delete_prefix(self, prefix: str) -> None:
        with self._lock:
            keys = [key for key in self._store if key.startswith(prefix)]
            for key in keys:
                del self._store[key]

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


# Shared instance
cache = InMemoryCache()
