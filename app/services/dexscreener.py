"""
CryptoTerminal — DexScreener API Service
Trending meme coins, pairs, liquidity, new tokens, buys/sells.
Free API, no key required.
"""

from __future__ import annotations

import httpx
import logging
from typing import Any

from app.config import get_settings
from app.cache import cache

logger = logging.getLogger(__name__)


async def _request(endpoint: str, params: dict | None = None) -> Any:
    """Make a request to the DexScreener API."""
    settings = get_settings()
    url = f"{settings.dexscreener_base_url}{endpoint}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params or {}, headers={"accept": "application/json"})
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error(f"DexScreener request failed: {endpoint} — {e}")
        return None


async def get_trending_tokens(chain: str = "") -> dict | None:
    """Get trending tokens across all chains or a specific chain."""
    settings = get_settings()
    cache_key = f"dex_trending_{chain or 'all'}"

    async def _fetch():
        if chain:
            return await _request(f"/token-boosts/top/v1")
        return await _request(f"/token-boosts/top/v1")

    return await cache.get_or_fetch(cache_key, _fetch, ttl=settings.cache_ttl_dex)


async def get_latest_tokens() -> dict | None:
    """Get the latest new tokens listed on DEXes."""
    settings = get_settings()

    async def _fetch():
        return await _request("/token-profiles/latest/v1")

    return await cache.get_or_fetch("dex_latest_tokens", _fetch, ttl=settings.cache_ttl_dex)


async def search_pairs(query: str) -> dict | None:
    """Search for trading pairs across all DEXes."""
    settings = get_settings()
    cache_key = f"dex_search_{query.lower()}"

    async def _fetch():
        return await _request(f"/latest/dex/search", {"q": query})

    return await cache.get_or_fetch(cache_key, _fetch, ttl=settings.cache_ttl_dex)


async def get_pairs_by_token(chain: str, token_address: str) -> dict | None:
    """Get all pairs for a specific token on a chain."""
    settings = get_settings()
    cache_key = f"dex_pairs_{chain}_{token_address[:10]}"

    async def _fetch():
        return await _request(f"/latest/dex/tokens/{token_address}")

    return await cache.get_or_fetch(cache_key, _fetch, ttl=settings.cache_ttl_dex)


async def get_pair_detail(chain: str, pair_address: str) -> dict | None:
    """Get detailed data for a specific trading pair."""
    settings = get_settings()
    cache_key = f"dex_pair_{chain}_{pair_address[:10]}"

    async def _fetch():
        return await _request(f"/latest/dex/pairs/{chain}/{pair_address}")

    return await cache.get_or_fetch(cache_key, _fetch, ttl=settings.cache_ttl_dex)


async def get_token_orders(chain: str, token_address: str) -> dict | None:
    """Get recent orders / buys & sells for a token."""
    settings = get_settings()
    cache_key = f"dex_orders_{chain}_{token_address[:10]}"

    async def _fetch():
        return await _request(f"/orders/v1/{chain}/{token_address}")

    return await cache.get_or_fetch(cache_key, _fetch, ttl=settings.cache_ttl_dex)
