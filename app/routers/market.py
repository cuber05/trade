"""
CryptoTerminal — Market Data Routes
Global market stats, fear & greed, trending, gainers/losers.
"""

from fastapi import APIRouter, Query
from typing import Optional

from app.services import coingecko, fear_greed

router = APIRouter(prefix="/api/v1/market", tags=["market"])


@router.get("/global")
async def global_market_data():
    """Get global crypto market data — market cap, dominance, volume."""
    data = await coingecko.get_global_data()
    if not data:
        return {"error": "Failed to fetch global market data"}
    return data


@router.get("/fear-greed")
async def fear_greed_index(limit: int = Query(default=30, le=365)):
    """Get Fear & Greed Index — current + historical."""
    data = await fear_greed.get_fear_greed_index(limit=limit)
    if not data:
        return {"error": "Failed to fetch Fear & Greed data"}
    return data


@router.get("/trending")
async def trending_coins():
    """Get trending coins on CoinGecko."""
    data = await coingecko.get_trending()
    if not data:
        return {"error": "Failed to fetch trending data"}
    return data


@router.get("/coins")
async def coins_list(
    vs_currency: str = "usd",
    order: str = "market_cap_desc",
    per_page: int = Query(default=100, le=250),
    page: int = Query(default=1, ge=1),
    sparkline: bool = True,
    category: Optional[str] = None,
):
    """
    Get paginated coin market data.
    Supports ordering, categories, and sparkline data.
    """
    data = await coingecko.get_coins_markets(
        vs_currency=vs_currency,
        order=order,
        per_page=per_page,
        page=page,
        sparkline=sparkline,
        category=category or "",
    )
    if data is None:
        return {"error": "Failed to fetch coin market data"}
    return data


@router.get("/gainers-losers")
async def gainers_and_losers(
    vs_currency: str = "usd",
    limit: int = Query(default=10, le=50),
):
    """Get top gainers and losers by 24h price change."""
    # Fetch top 250 by market cap, then sort
    data = await coingecko.get_coins_markets(
        vs_currency=vs_currency,
        order="market_cap_desc",
        per_page=250,
        page=1,
        sparkline=False,
    )
    if not data:
        return {"error": "Failed to fetch market data"}

    # Filter out coins without valid price change
    valid = [c for c in data if c.get("price_change_percentage_24h") is not None]

    gainers = sorted(valid, key=lambda x: x["price_change_percentage_24h"], reverse=True)[:limit]
    losers = sorted(valid, key=lambda x: x["price_change_percentage_24h"])[:limit]

    return {
        "gainers": gainers,
        "losers": losers,
    }


@router.get("/categories")
async def market_categories():
    """Get all coin categories with market data."""
    data = await coingecko.get_categories()
    if not data:
        return {"error": "Failed to fetch categories"}
    return data


@router.get("/search")
async def search(q: str = Query(min_length=1)):
    """Search for coins by name or symbol."""
    data = await coingecko.search_coins(q)
    if not data:
        return {"error": "Search failed"}
    return data
