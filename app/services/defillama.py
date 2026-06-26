"""
CryptoTerminal — DefiLlama API Service
TVL, chains, stablecoins, protocol statistics.
Free API, no key required.
"""

from __future__ import annotations

import httpx
import logging
from typing import Any

from app.config import get_settings
from app.cache import cache

logger = logging.getLogger(__name__)


async def _request(base_url: str, endpoint: str, params: dict | None = None) -> Any:
    """Make a request to the DefiLlama API."""
    url = f"{base_url}{endpoint}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params or {}, headers={"accept": "application/json"})
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error(f"DefiLlama request failed: {endpoint} — {e}")
        return None


# ── TVL ──

async def get_protocols() -> list | None:
    """Get all DeFi protocols with TVL data."""
    settings = get_settings()
    return await cache.get_or_fetch(
        "defi_protocols",
        lambda: _request(settings.defillama_base_url, "/protocols"),
        ttl=settings.cache_ttl_defi
    )


async def get_protocol(slug: str) -> dict | None:
    """Get detailed protocol data including historical TVL."""
    settings = get_settings()
    cache_key = f"defi_protocol_{slug}"
    return await cache.get_or_fetch(
        cache_key,
        lambda: _request(settings.defillama_base_url, f"/protocol/{slug}"),
        ttl=settings.cache_ttl_defi
    )


async def get_tvl_history() -> list | None:
    """Get historical total TVL across all chains."""
    settings = get_settings()
    return await cache.get_or_fetch(
        "defi_tvl_history",
        lambda: _request(settings.defillama_base_url, "/v2/historicalChainTvl"),
        ttl=settings.cache_ttl_defi
    )


# ── Chains ──

async def get_chains() -> list | None:
    """Get TVL per chain."""
    settings = get_settings()
    return await cache.get_or_fetch(
        "defi_chains",
        lambda: _request(settings.defillama_base_url, "/v2/chains"),
        ttl=settings.cache_ttl_defi
    )


async def get_chain_tvl(chain: str) -> list | None:
    """Get historical TVL for a specific chain."""
    settings = get_settings()
    cache_key = f"defi_chain_tvl_{chain}"
    return await cache.get_or_fetch(
        cache_key,
        lambda: _request(settings.defillama_base_url, f"/v2/historicalChainTvl/{chain}"),
        ttl=settings.cache_ttl_defi
    )


# ── Stablecoins ──

async def get_stablecoins() -> dict | None:
    """Get all stablecoins with market cap and chain distribution."""
    settings = get_settings()
    return await cache.get_or_fetch(
        "defi_stablecoins",
        lambda: _request(settings.defillama_stablecoins_url, "/stablecoins", {"includePrices": "true"}),
        ttl=settings.cache_ttl_defi
    )


async def get_stablecoin_charts() -> list | None:
    """Get historical stablecoin market cap charts."""
    settings = get_settings()
    return await cache.get_or_fetch(
        "defi_stablecoin_charts",
        lambda: _request(settings.defillama_stablecoins_url, "/stablecoincharts/all", {"stablecoin": "1"}),
        ttl=settings.cache_ttl_defi
    )


# ── Yields / Pools ──

async def get_yields() -> dict | None:
    """Get yield/APY data for DeFi pools."""
    settings = get_settings()
    return await cache.get_or_fetch(
        "defi_yields",
        lambda: _request("https://yields.llama.fi", "/pools"),
        ttl=settings.cache_ttl_defi
    )


# ── Coin Prices ──

async def get_current_prices(coins: list[str]) -> dict | None:
    """Get current prices from DefiLlama for coins (format: 'chain:address')."""
    settings = get_settings()
    coins_str = ",".join(coins)
    cache_key = f"defi_prices_{coins_str[:50]}"
    return await cache.get_or_fetch(
        cache_key,
        lambda: _request(settings.defillama_coins_url, f"/prices/current/{coins_str}"),
        ttl=60
    )


# ── Summary Stats ──

async def get_defi_summary() -> dict | None:
    """Get a summary of DeFi metrics — total TVL, top chains, top protocols."""
    settings = get_settings()
    cache_key = "defi_summary"

    async def _fetch():
        chains = await get_chains()
        if not chains:
            return None

        total_tvl = sum(c.get("tvl", 0) for c in chains if isinstance(c, dict))
        top_chains = sorted(
            [c for c in chains if isinstance(c, dict) and c.get("tvl", 0) > 0],
            key=lambda x: x.get("tvl", 0),
            reverse=True
        )[:10]

        return {
            "total_tvl": total_tvl,
            "chain_count": len(chains),
            "top_chains": [
                {
                    "name": c.get("name", ""),
                    "gecko_id": c.get("gecko_id", ""),
                    "tvl": c.get("tvl", 0),
                    "tokenSymbol": c.get("tokenSymbol", ""),
                }
                for c in top_chains
            ],
        }

    return await cache.get_or_fetch(cache_key, _fetch, ttl=settings.cache_ttl_defi)
