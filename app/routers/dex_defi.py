"""
CryptoTerminal — DEX, DeFi & Sentiment Routes
DexScreener, GeckoTerminal, DefiLlama, Reddit integration.
"""

from fastapi import APIRouter, Path, Query
from typing import Optional

from app.services import dexscreener, gecko_terminal, defillama, reddit

router = APIRouter(prefix="/api/v1", tags=["dex", "defi", "sentiment"])


# ── DexScreener ──

@router.get("/dex/trending")
async def dex_trending():
    """Get trending tokens from DexScreener."""
    data = await dexscreener.get_trending_tokens()
    return data or []


@router.get("/dex/latest")
async def dex_latest_tokens():
    """Get latest new tokens listed on DEXes."""
    data = await dexscreener.get_latest_tokens()
    return data or []


@router.get("/dex/search")
async def dex_search(q: str = Query(min_length=1)):
    """Search for pairs on DexScreener."""
    data = await dexscreener.search_pairs(q)
    return data or {"pairs": []}


@router.get("/dex/pairs/{chain}/{pair_address}")
async def dex_pair_detail(chain: str, pair_address: str):
    """Get detail for a specific DEX pair."""
    data = await dexscreener.get_pair_detail(chain, pair_address)
    return data or {"pair": None}


# ── GeckoTerminal ──

@router.get("/gecko-terminal/trending-pools")
async def gt_trending_pools(network: Optional[str] = None, duration: str = "24h"):
    """Get trending pools from GeckoTerminal."""
    data = await gecko_terminal.get_trending_pools(network or "", duration)
    return data or {"data": []}


@router.get("/gecko-terminal/new-pools")
async def gt_new_pools(network: Optional[str] = None):
    """Get newly created pools."""
    data = await gecko_terminal.get_new_pools(network or "")
    return data or {"data": []}


@router.get("/gecko-terminal/pool/{network}/{pool_address}")
async def gt_pool_detail(network: str, pool_address: str):
    """Get pool detail data."""
    data = await gecko_terminal.get_pool(network, pool_address)
    return data or {"data": None}


@router.get("/gecko-terminal/pool/{network}/{pool_address}/ohlcv")
async def gt_pool_ohlcv(
    network: str,
    pool_address: str,
    timeframe: str = "hour",
    aggregate: int = 1,
):
    """Get OHLCV data for a pool."""
    data = await gecko_terminal.get_pool_ohlcv(network, pool_address, timeframe, aggregate)
    return data or {"data": None}


@router.get("/gecko-terminal/pool/{network}/{pool_address}/trades")
async def gt_pool_trades(network: str, pool_address: str):
    """Get recent trades for a pool."""
    data = await gecko_terminal.get_pool_trades(network, pool_address)
    return data or {"data": []}


@router.get("/gecko-terminal/networks")
async def gt_networks():
    """Get all supported networks."""
    data = await gecko_terminal.get_networks()
    return data or {"data": []}


# ── DefiLlama ──

@router.get("/defi/summary")
async def defi_summary():
    """Get DeFi summary — total TVL, top chains, top protocols."""
    data = await defillama.get_defi_summary()
    return data or {"total_tvl": 0, "chain_count": 0, "top_chains": []}


@router.get("/defi/chains")
async def defi_chains():
    """Get TVL per chain."""
    data = await defillama.get_chains()
    return data or []


@router.get("/defi/protocols")
async def defi_protocols():
    """Get all DeFi protocols with TVL."""
    data = await defillama.get_protocols()
    if not data:
        return []
    # Return top 100 by TVL
    sorted_data = sorted(data, key=lambda x: x.get("tvl", 0) or 0, reverse=True)
    return sorted_data[:100]


@router.get("/defi/protocol/{slug}")
async def defi_protocol_detail(slug: str):
    """Get detailed protocol data."""
    data = await defillama.get_protocol(slug)
    return data or {"error": "Protocol not found"}


@router.get("/defi/stablecoins")
async def defi_stablecoins():
    """Get stablecoin data."""
    data = await defillama.get_stablecoins()
    return data or {"peggedAssets": []}


@router.get("/defi/tvl-history")
async def defi_tvl_history():
    """Get historical total TVL."""
    data = await defillama.get_tvl_history()
    return data or []


# ── Reddit Sentiment ──

@router.get("/reddit/sentiment/{coin_symbol}")
async def reddit_sentiment(
    coin_symbol: str = Path(min_length=1),
    coin_name: str = Query(default=""),
):
    """Get Reddit sentiment analysis for a coin."""
    name = coin_name or coin_symbol
    data = await reddit.get_coin_sentiment(name, coin_symbol)
    return data


@router.get("/reddit/hot/{subreddit}")
async def reddit_hot_posts(
    subreddit: str = Path(min_length=1),
    limit: int = Query(default=25, le=100),
):
    """Get hot posts from a crypto subreddit."""
    data = await reddit.get_subreddit_hot(subreddit, limit)
    return data or []
