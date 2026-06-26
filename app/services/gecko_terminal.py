"""
CryptoTerminal — GeckoTerminal API Service
DEX analytics, pools, liquidity, swaps.
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
    """Make a request to the GeckoTerminal API."""
    settings = get_settings()
    url = f"{settings.gecko_terminal_base_url}{endpoint}"
    headers = {"accept": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params or {}, headers=headers)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error(f"GeckoTerminal request failed: {endpoint} — {e}")
        return None


# ── Networks (Chains) ──

async def get_networks() -> dict | None:
    """Get all supported blockchain networks."""
    return await cache.get_or_fetch(
        "gt_networks",
        lambda: _request("/networks"),
        ttl=3600
    )


# ── Trending Pools ──

async def get_trending_pools(network: str = "", duration: str = "24h") -> dict | None:
    """Get trending pools globally or on a specific network."""
    settings = get_settings()
    cache_key = f"gt_trending_{network or 'all'}_{duration}"

    async def _fetch():
        if network:
            return await _request(f"/networks/{network}/trending_pools", {"duration": duration})
        return await _request("/networks/trending_pools", {"duration": duration})

    return await cache.get_or_fetch(cache_key, _fetch, ttl=settings.cache_ttl_dex)


# ── New Pools ──

async def get_new_pools(network: str = "") -> dict | None:
    """Get newly created pools globally or on a specific network."""
    settings = get_settings()
    cache_key = f"gt_new_pools_{network or 'all'}"

    async def _fetch():
        if network:
            return await _request(f"/networks/{network}/new_pools")
        return await _request("/networks/new_pools")

    return await cache.get_or_fetch(cache_key, _fetch, ttl=settings.cache_ttl_dex)


# ── Pool Detail ──

async def get_pool(network: str, pool_address: str) -> dict | None:
    """Get detailed pool data."""
    settings = get_settings()
    cache_key = f"gt_pool_{network}_{pool_address[:10]}"

    return await cache.get_or_fetch(
        cache_key,
        lambda: _request(f"/networks/{network}/pools/{pool_address}"),
        ttl=settings.cache_ttl_dex
    )


# ── Pool OHLCV ──

async def get_pool_ohlcv(
    network: str,
    pool_address: str,
    timeframe: str = "hour",
    aggregate: int = 1,
    limit: int = 100,
) -> dict | None:
    """Get OHLCV candlestick data for a pool."""
    settings = get_settings()
    cache_key = f"gt_ohlcv_{network}_{pool_address[:10]}_{timeframe}_{aggregate}"

    params = {"aggregate": aggregate, "limit": limit}
    return await cache.get_or_fetch(
        cache_key,
        lambda: _request(f"/networks/{network}/pools/{pool_address}/ohlcv/{timeframe}", params),
        ttl=settings.cache_ttl_dex
    )


# ── Token Data ──

async def get_token_info(network: str, token_address: str) -> dict | None:
    """Get token info including top pools."""
    settings = get_settings()
    cache_key = f"gt_token_{network}_{token_address[:10]}"

    return await cache.get_or_fetch(
        cache_key,
        lambda: _request(f"/networks/{network}/tokens/{token_address}"),
        ttl=settings.cache_ttl_dex
    )


async def get_token_pools(network: str, token_address: str) -> dict | None:
    """Get all pools for a token on a network."""
    settings = get_settings()
    cache_key = f"gt_token_pools_{network}_{token_address[:10]}"

    return await cache.get_or_fetch(
        cache_key,
        lambda: _request(f"/networks/{network}/tokens/{token_address}/pools"),
        ttl=settings.cache_ttl_dex
    )


# ── DEX Data ──

async def get_dexes(network: str) -> dict | None:
    """Get all DEXes on a specific network."""
    return await cache.get_or_fetch(
        f"gt_dexes_{network}",
        lambda: _request(f"/networks/{network}/dexes"),
        ttl=3600
    )


# ── Trades ──

async def get_pool_trades(network: str, pool_address: str) -> dict | None:
    """Get recent trades for a pool."""
    settings = get_settings()
    cache_key = f"gt_trades_{network}_{pool_address[:10]}"

    return await cache.get_or_fetch(
        cache_key,
        lambda: _request(f"/networks/{network}/pools/{pool_address}/trades"),
        ttl=30  # Very short TTL for trade data
    )
