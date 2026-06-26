"""
CryptoTerminal — In-Memory TTL Cache
Simple async-friendly cache with per-key TTL expiration.
"""

from __future__ import annotations

import time
import asyncio
from typing import Any, Optional, Callable, Awaitable


class TTLCache:
    """Thread-safe in-memory cache with per-key TTL."""

    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Get value if key exists and hasn't expired."""
        async with self._lock:
            if key in self._store:
                value, expires_at = self._store[key]
                if time.time() < expires_at:
                    return value
                else:
                    del self._store[key]
        return None

    async def set(self, key: str, value: Any, ttl: int = 60) -> None:
        """Set a value with TTL in seconds."""
        async with self._lock:
            self._store[key] = (value, time.time() + ttl)

    async def delete(self, key: str) -> None:
        """Remove a key."""
        async with self._lock:
            self._store.pop(key, None)

    async def clear(self) -> None:
        """Clear all cached entries."""
        async with self._lock:
            self._store.clear()

    async def cleanup(self) -> int:
        """Remove all expired entries. Returns count of removed items."""
        async with self._lock:
            now = time.time()
            expired = [k for k, (_, exp) in self._store.items() if now >= exp]
            for k in expired:
                del self._store[k]
            return len(expired)

    async def get_or_fetch(
        self,
        key: str,
        fetcher: Callable[[], Awaitable[Any]],
        ttl: int = 60,
    ) -> Any:
        """Get from cache or fetch using the provided async function."""
        cached = await self.get(key)
        if cached is not None:
            return cached

        value = await fetcher()
        if value is not None:
            await self.set(key, value, ttl)
        return value

    @property
    def size(self) -> int:
        return len(self._store)


# Global cache instance
cache = TTLCache()
