"""
CryptoTerminal — CoinGecko API Service
Handles all CoinGecko free-tier API interactions with rate limiting.
"""

from __future__ import annotations

import httpx
import asyncio
import logging
from typing import Optional, Any

from app.config import get_settings
from app.cache import cache

logger = logging.getLogger(__name__)

# Rate limit: free tier = 10-30 calls/min. We use a semaphore.
_semaphore = asyncio.Semaphore(5)


async def _request(endpoint: str, params: dict | None = None, ttl_key: str = "") -> Any:
    """Make a rate-limited request to CoinGecko API."""
    settings = get_settings()
    url = f"{settings.coingecko_url}{endpoint}"

    headers = {"accept": "application/json"}
    if settings.coingecko_api_key:
        headers["x-cg-pro-api-key"] = settings.coingecko_api_key

    async with _semaphore:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, params=params or {}, headers=headers)
                if resp.status_code == 429:
                    logger.warning("CoinGecko rate limit hit, waiting 60s...")
                    await asyncio.sleep(60)
                    resp = await client.get(url, params=params or {}, headers=headers)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"CoinGecko HTTP error {e.response.status_code}: {endpoint}")
            return None
        except Exception as e:
            logger.error(f"CoinGecko request failed: {e}")
            return None


# ── Global Market Data ──

async def get_global_data() -> dict | None:
    """Get global crypto market data (market cap, dominance, etc.)."""
    settings = get_settings()
    return await cache.get_or_fetch(
        "global_data",
        lambda: _request("/global"),
        ttl=settings.cache_ttl_market
    )


async def get_global_defi_data() -> dict | None:
    """Get global DeFi market data."""
    settings = get_settings()
    return await cache.get_or_fetch(
        "global_defi",
        lambda: _request("/global/decentralized_finance_defi"),
        ttl=settings.cache_ttl_market
    )


# ── Coin Listings ──

async def get_coins_markets(
    vs_currency: str = "usd",
    order: str = "market_cap_desc",
    per_page: int = 100,
    page: int = 1,
    sparkline: bool = True,
    price_change: str = "1h,24h,7d",
    category: str = "",
) -> list[dict] | None:
    """Get coin market data with prices, market cap, volume, etc."""
    settings = get_settings()
    cache_key = f"coins_markets_{vs_currency}_{order}_{per_page}_{page}_{category}"

    params = {
        "vs_currency": vs_currency,
        "order": order,
        "per_page": per_page,
        "page": page,
        "sparkline": str(sparkline).lower(),
        "price_change_percentage": price_change,
    }
    if category:
        params["category"] = category

    return await cache.get_or_fetch(
        cache_key,
        lambda: _request("/coins/markets", params),
        ttl=settings.cache_ttl_market
    )


# ── Trending ──

async def get_trending() -> dict | None:
    """Get trending coins, NFTs, and categories."""
    settings = get_settings()
    return await cache.get_or_fetch(
        "trending",
        lambda: _request("/search/trending"),
        ttl=settings.cache_ttl_trending
    )


# ── Search ──

async def search_coins(query: str) -> dict | None:
    """Search for coins by name or symbol."""
    settings = get_settings()
    cache_key = f"search_{query.lower()}"
    return await cache.get_or_fetch(
        cache_key,
        lambda: _request("/search", {"query": query}),
        ttl=settings.cache_ttl_search
    )


# ── Coin Detail ──

async def get_coin_detail(coin_id: str) -> dict | None:
    """Get comprehensive coin data."""
    settings = get_settings()
    cache_key = f"coin_detail_{coin_id}"

    params = {
        "localization": "false",
        "tickers": "true",
        "market_data": "true",
        "community_data": "true",
        "developer_data": "true",
        "sparkline": "true",
    }

    return await cache.get_or_fetch(
        cache_key,
        lambda: _request(f"/coins/{coin_id}", params),
        ttl=settings.cache_ttl_coin
    )


# ── Market Chart ──

async def get_coin_market_chart(
    coin_id: str,
    vs_currency: str = "usd",
    days: int | str = 7,
) -> dict | None:
    """Get historical price, market cap, and volume data."""
    settings = get_settings()
    cache_key = f"chart_{coin_id}_{vs_currency}_{days}"

    params = {
        "vs_currency": vs_currency,
        "days": str(days),
    }

    return await cache.get_or_fetch(
        cache_key,
        lambda: _request(f"/coins/{coin_id}/market_chart", params),
        ttl=settings.cache_ttl_chart
    )


async def get_coin_ohlc(
    coin_id: str,
    vs_currency: str = "usd",
    days: int = 7,
) -> list | None:
    """Get OHLC candlestick data."""
    settings = get_settings()
    cache_key = f"ohlc_{coin_id}_{vs_currency}_{days}"

    params = {
        "vs_currency": vs_currency,
        "days": str(days),
    }

    return await cache.get_or_fetch(
        cache_key,
        lambda: _request(f"/coins/{coin_id}/ohlc", params),
        ttl=settings.cache_ttl_chart
    )


# ── Categories ──

async def get_categories() -> list[dict] | None:
    """Get all coin categories with market data."""
    settings = get_settings()
    return await cache.get_or_fetch(
        "categories",
        lambda: _request("/coins/categories"),
        ttl=settings.cache_ttl_market * 5
    )


# ── Exchanges ──

async def get_exchanges(per_page: int = 20, page: int = 1) -> list[dict] | None:
    """Get exchange data."""
    settings = get_settings()
    cache_key = f"exchanges_{per_page}_{page}"
    return await cache.get_or_fetch(
        cache_key,
        lambda: _request("/exchanges", {"per_page": per_page, "page": page}),
        ttl=settings.cache_ttl_market * 3
    )


# ── Simple Price ──

async def get_simple_price(
    coin_ids: list[str],
    vs_currencies: str = "usd",
    include_change: bool = True,
    include_market_cap: bool = True,
    include_vol: bool = True,
) -> dict | None:
    """Get simple price data for multiple coins."""
    ids_str = ",".join(coin_ids)
    cache_key = f"simple_price_{ids_str}"
    settings = get_settings()

    params = {
        "ids": ids_str,
        "vs_currencies": vs_currencies,
        "include_24hr_change": str(include_change).lower(),
        "include_market_cap": str(include_market_cap).lower(),
        "include_24hr_vol": str(include_vol).lower(),
    }

    return await cache.get_or_fetch(
        cache_key,
        lambda: _request("/simple/price", params),
        ttl=settings.cache_ttl_coin
    )


# ── Coin Price History ──

async def get_coin_history(coin_id: str, date: str) -> dict | None:
    """Get coin data at a specific date (dd-mm-yyyy)."""
    cache_key = f"history_{coin_id}_{date}"
    return await cache.get_or_fetch(
        cache_key,
        lambda: _request(f"/coins/{coin_id}/history", {"date": date, "localization": "false"}),
        ttl=3600  # 1 hour for historical data
    )
