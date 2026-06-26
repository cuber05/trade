"""
CryptoTerminal — Reddit Sentiment Service
Fetches and analyzes r/CryptoCurrency, r/Solana, r/memecoins discussions.
Requires Reddit API credentials (optional — gracefully degrades).
"""

from __future__ import annotations

import httpx
import logging
import re
from typing import Any

from app.config import get_settings
from app.cache import cache

logger = logging.getLogger(__name__)

_token_cache: dict[str, Any] = {"access_token": None, "expires_at": 0}


async def _get_access_token() -> str | None:
    """Get Reddit OAuth2 access token using client credentials."""
    import time
    settings = get_settings()

    if not settings.has_reddit:
        return None

    now = time.time()
    if _token_cache["access_token"] and now < _token_cache["expires_at"]:
        return _token_cache["access_token"]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                settings.reddit_token_url,
                data={"grant_type": "client_credentials"},
                auth=(settings.reddit_client_id, settings.reddit_client_secret),
                headers={"User-Agent": settings.reddit_user_agent},
            )
            resp.raise_for_status()
            data = resp.json()
            _token_cache["access_token"] = data["access_token"]
            _token_cache["expires_at"] = now + data.get("expires_in", 3600) - 60
            return data["access_token"]
    except Exception as e:
        logger.error(f"Reddit auth failed: {e}")
        return None


async def _request(endpoint: str, params: dict | None = None) -> Any:
    """Make an authenticated request to the Reddit API."""
    settings = get_settings()
    token = await _get_access_token()
    if not token:
        return None

    url = f"{settings.reddit_oauth_url}{endpoint}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                url,
                params=params or {},
                headers={
                    "Authorization": f"Bearer {token}",
                    "User-Agent": settings.reddit_user_agent,
                },
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error(f"Reddit API failed: {endpoint} — {e}")
        return None


async def get_subreddit_hot(subreddit: str, limit: int = 25) -> list[dict] | None:
    """Get hot posts from a subreddit."""
    settings = get_settings()
    cache_key = f"reddit_hot_{subreddit}_{limit}"

    async def _fetch():
        data = await _request(f"/r/{subreddit}/hot", {"limit": limit})
        if not data or "data" not in data:
            return None

        posts = []
        for child in data["data"].get("children", []):
            post = child.get("data", {})
            posts.append({
                "title": post.get("title", ""),
                "selftext": post.get("selftext", "")[:500],
                "score": post.get("score", 0),
                "upvote_ratio": post.get("upvote_ratio", 0),
                "num_comments": post.get("num_comments", 0),
                "url": post.get("url", ""),
                "permalink": f"https://reddit.com{post.get('permalink', '')}",
                "created_utc": post.get("created_utc", 0),
                "author": post.get("author", ""),
                "flair": post.get("link_flair_text", ""),
                "subreddit": subreddit,
            })
        return posts

    return await cache.get_or_fetch(cache_key, _fetch, ttl=settings.cache_ttl_reddit)


async def search_subreddit(subreddit: str, query: str, limit: int = 15) -> list[dict] | None:
    """Search for posts mentioning a specific coin in a subreddit."""
    settings = get_settings()
    cache_key = f"reddit_search_{subreddit}_{query.lower()}_{limit}"

    async def _fetch():
        data = await _request(
            f"/r/{subreddit}/search",
            {"q": query, "restrict_sr": "true", "sort": "new", "limit": limit, "t": "week"}
        )
        if not data or "data" not in data:
            return None

        posts = []
        for child in data["data"].get("children", []):
            post = child.get("data", {})
            posts.append({
                "title": post.get("title", ""),
                "score": post.get("score", 0),
                "upvote_ratio": post.get("upvote_ratio", 0),
                "num_comments": post.get("num_comments", 0),
                "permalink": f"https://reddit.com{post.get('permalink', '')}",
                "created_utc": post.get("created_utc", 0),
                "subreddit": subreddit,
            })
        return posts

    return await cache.get_or_fetch(cache_key, _fetch, ttl=settings.cache_ttl_reddit)


async def get_coin_sentiment(coin_name: str, coin_symbol: str) -> dict:
    """
    Analyze Reddit sentiment for a specific coin.
    Searches multiple subreddits and aggregates metrics.
    """
    settings = get_settings()
    cache_key = f"reddit_sentiment_{coin_symbol.lower()}"

    async def _fetch():
        subreddits = ["CryptoCurrency", "CryptoMarkets"]

        # Add coin-specific subreddit if it's a major coin
        coin_subs = {
            "btc": "Bitcoin", "eth": "ethereum", "sol": "solana",
            "doge": "dogecoin", "shib": "SHIBArmy", "xrp": "XRP",
            "ada": "cardano", "matic": "maticnetwork", "dot": "Polkadot",
            "avax": "Avax", "link": "Chainlink", "uni": "UniSwap",
            "pepe": "pepecoin",
        }
        sym_lower = coin_symbol.lower()
        if sym_lower in coin_subs:
            subreddits.append(coin_subs[sym_lower])

        all_posts = []
        for sub in subreddits:
            posts = await search_subreddit(sub, f"{coin_name} OR {coin_symbol}", limit=10)
            if posts:
                all_posts.extend(posts)

        if not all_posts:
            return {
                "available": False,
                "message": "No Reddit data available. Add Reddit API credentials to .env",
                "posts_analyzed": 0,
            }

        # Simple sentiment analysis
        total_score = sum(p["score"] for p in all_posts)
        total_comments = sum(p["num_comments"] for p in all_posts)
        avg_upvote_ratio = sum(p["upvote_ratio"] for p in all_posts) / len(all_posts) if all_posts else 0

        # Keyword-based sentiment
        positive_words = ["bullish", "moon", "buy", "pump", "undervalued", "gem", "hodl", "long", "breakout", "up"]
        negative_words = ["bearish", "dump", "sell", "crash", "overvalued", "short", "scam", "rug", "down", "dead"]

        positive_count = 0
        negative_count = 0
        for post in all_posts:
            text = (post["title"] + " " + post.get("selftext", "")).lower()
            positive_count += sum(1 for w in positive_words if w in text)
            negative_count += sum(1 for w in negative_words if w in text)

        total_signals = positive_count + negative_count
        if total_signals > 0:
            sentiment_score = ((positive_count - negative_count) / total_signals) * 50 + 50
        else:
            sentiment_score = 50  # Neutral

        sentiment_score = max(0, min(100, sentiment_score))

        if sentiment_score >= 65:
            label = "Bullish"
        elif sentiment_score <= 35:
            label = "Bearish"
        else:
            label = "Neutral"

        return {
            "available": True,
            "sentiment_score": round(sentiment_score),
            "sentiment_label": label,
            "posts_analyzed": len(all_posts),
            "total_score": total_score,
            "total_comments": total_comments,
            "avg_upvote_ratio": round(avg_upvote_ratio, 2),
            "positive_signals": positive_count,
            "negative_signals": negative_count,
            "top_posts": sorted(all_posts, key=lambda x: x["score"], reverse=True)[:5],
        }

    return await cache.get_or_fetch(cache_key, _fetch, ttl=settings.cache_ttl_reddit)
