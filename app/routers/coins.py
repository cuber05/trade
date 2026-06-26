"""
CryptoTerminal — Coin Detail & AI Analysis Routes
Individual coin data, charts, OHLC, AI scoring, and Reddit sentiment.
"""

from fastapi import APIRouter, Path, Query

from app.services import coingecko, fear_greed, reddit
from app.services.ai_engine import analyze_coin
from app.services.openai_service import generate_ai_analysis

router = APIRouter(prefix="/api/v1/coins", tags=["coins"])


@router.get("/{coin_id}")
async def coin_detail(coin_id: str = Path(min_length=1)):
    """Get comprehensive coin detail data."""
    data = await coingecko.get_coin_detail(coin_id)
    if not data:
        return {"error": f"Failed to fetch data for '{coin_id}'"}
    return data


@router.get("/{coin_id}/chart")
async def coin_chart(
    coin_id: str = Path(min_length=1),
    vs_currency: str = "usd",
    days: str = "7",
):
    """Get historical price/volume chart data."""
    data = await coingecko.get_coin_market_chart(
        coin_id=coin_id,
        vs_currency=vs_currency,
        days=days,
    )
    if not data:
        return {"error": f"Failed to fetch chart for '{coin_id}'"}
    return data


@router.get("/{coin_id}/ohlc")
async def coin_ohlc(
    coin_id: str = Path(min_length=1),
    vs_currency: str = "usd",
    days: int = Query(default=7, ge=1, le=365),
):
    """Get OHLC candlestick data."""
    data = await coingecko.get_coin_ohlc(
        coin_id=coin_id,
        vs_currency=vs_currency,
        days=days,
    )
    if not data:
        return {"error": f"Failed to fetch OHLC for '{coin_id}'"}
    return data


@router.get("/{coin_id}/ai-analysis")
async def coin_ai_analysis(coin_id: str = Path(min_length=1)):
    """
    Get AI-generated analysis for a coin.
    Uses Groq if configured, otherwise falls back to built-in engine.
    Feeds sector peers + trending context for comparative analysis.
    """
    # Fetch all data concurrently
    coin_data = await coingecko.get_coin_detail(coin_id)
    if not coin_data:
        return {"error": f"Failed to fetch data for '{coin_id}'"}

    global_data = await coingecko.get_global_data()
    fg_data = await fear_greed.get_fear_greed_index(limit=1)

    # Reddit sentiment (non-blocking, may return empty)
    coin_name = coin_data.get("name", coin_id)
    coin_symbol = coin_data.get("symbol", "")
    reddit_sentiment = await reddit.get_coin_sentiment(coin_name, coin_symbol)

    # Fetch sector peers: grab coins from the same category for comparison
    sector_peers = None
    categories = coin_data.get("categories", [])
    if categories:
        # Pick the most specific category (skip generic ones)
        skip = {"Cryptocurrency", "Coins", "Token"}
        category_slug = None
        for cat in categories:
            if cat and cat not in skip:
                category_slug = cat.lower().replace(" ", "-").replace("'", "")
                break
        if category_slug:
            sector_peers = await coingecko.get_coins_markets(
                per_page=10, sparkline=False, category=category_slug
            )

    # Fetch trending coins for additional context
    trending_data = await coingecko.get_trending()

    # Try Groq first
    groq_analysis = await generate_ai_analysis(
        coin_data, global_data, fg_data, reddit_sentiment,
        sector_peers=sector_peers, trending_data=trending_data
    )

    if groq_analysis:
        analysis = groq_analysis
    else:
        # Fall back to built-in engine
        analysis = analyze_coin(coin_data, global_data, fg_data)

    analysis["coin_id"] = coin_id
    analysis["coin_name"] = coin_name
    analysis["coin_symbol"] = coin_symbol.upper()

    # Attach Reddit sentiment
    if reddit_sentiment:
        analysis["reddit_sentiment"] = reddit_sentiment

    return analysis


@router.get("/{coin_id}/reddit")
async def coin_reddit_sentiment(coin_id: str = Path(min_length=1)):
    """Get Reddit sentiment for a specific coin."""
    coin_data = await coingecko.get_coin_detail(coin_id)
    if not coin_data:
        return {"error": f"Coin '{coin_id}' not found"}

    name = coin_data.get("name", coin_id)
    symbol = coin_data.get("symbol", coin_id)
    data = await reddit.get_coin_sentiment(name, symbol)
    return data


@router.get("/{coin_id}/price")
async def coin_simple_price(coin_id: str = Path(min_length=1)):
    """Get simple price data for a single coin."""
    data = await coingecko.get_simple_price([coin_id])
    if not data:
        return {"error": f"Failed to fetch price for '{coin_id}'"}
    return data


@router.post("/prices")
async def multi_coin_prices(coin_ids: list[str]):
    """Get prices for multiple coins at once."""
    if not coin_ids:
        return {}
    data = await coingecko.get_simple_price(coin_ids)
    if not data:
        return {"error": "Failed to fetch prices"}
    return data
