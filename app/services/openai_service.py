"""
CryptoTerminal — OpenAI Service
Powers the advanced AI analysis and "Explain Why" feature.
Falls back to the built-in ai_engine if no API key is set.
"""

from __future__ import annotations

import httpx
import json
import logging
from typing import Any

from app.config import get_settings
from app.cache import cache

logger = logging.getLogger(__name__)


async def generate_ai_analysis(
    coin_data: dict,
    market_context: dict | None = None,
    fear_greed: dict | None = None,
    reddit_sentiment: dict | None = None,
    defi_data: dict | None = None,
) -> dict | None:
    """
    Generate an advanced AI analysis using OpenAI.
    Returns None if OpenAI is not configured (caller should use built-in engine).
    """
    settings = get_settings()
    if not settings.has_groq:
        return None

    coin_name = coin_data.get("name", "Unknown")
    coin_symbol = coin_data.get("symbol", "").upper()
    md = coin_data.get("market_data", {})

    # Build context for the LLM
    context_parts = []

    # Price & market data
    price = md.get("current_price", {}).get("usd", 0)
    pct_24h = md.get("price_change_percentage_24h", 0) or 0
    pct_7d = md.get("price_change_percentage_7d", 0) or 0
    pct_30d = md.get("price_change_percentage_30d", 0) or 0
    mcap = md.get("market_cap", {}).get("usd", 0)
    volume = md.get("total_volume", {}).get("usd", 0)
    rank = md.get("market_cap_rank", 0)
    ath_pct = md.get("ath_change_percentage", {}).get("usd", 0) or 0

    context_parts.append(f"""
COIN: {coin_name} ({coin_symbol})
Price: ${price}
24h Change: {pct_24h:+.2f}%
7d Change: {pct_7d:+.2f}%
30d Change: {pct_30d:+.2f}%
Market Cap: ${mcap:,.0f} (Rank #{rank})
24h Volume: ${volume:,.0f}
Distance from ATH: {ath_pct:.1f}%
Circulating Supply: {md.get('circulating_supply', 'N/A')}
Max Supply: {md.get('max_supply', 'N/A')}
""")

    # Community data
    community = coin_data.get("community_data", {})
    if community:
        context_parts.append(f"""
COMMUNITY:
Twitter Followers: {community.get('twitter_followers', 'N/A')}
Reddit Subscribers: {community.get('reddit_subscribers', 'N/A')}
""")

    # Developer data
    dev = coin_data.get("developer_data", {})
    if dev:
        context_parts.append(f"""
DEVELOPER ACTIVITY:
GitHub Commits (4 weeks): {dev.get('commit_count_4_weeks', 'N/A')}
Stars: {dev.get('stars', 'N/A')}
Forks: {dev.get('forks', 'N/A')}
""")

    # Market context
    if market_context and market_context.get("data"):
        gd = market_context["data"]
        context_parts.append(f"""
MARKET CONTEXT:
Total Crypto Market Cap Change 24h: {gd.get('market_cap_change_percentage_24h_usd', 0):.2f}%
BTC Dominance: {gd.get('market_cap_percentage', {}).get('btc', 0):.1f}%
""")

    # Fear & Greed
    if fear_greed and fear_greed.get("current"):
        fg = fear_greed["current"]
        context_parts.append(f"""
FEAR & GREED INDEX: {fg['value']}/100 ({fg['classification']})
""")

    # Reddit sentiment
    if reddit_sentiment and reddit_sentiment.get("available"):
        context_parts.append(f"""
REDDIT SENTIMENT:
Score: {reddit_sentiment['sentiment_score']}/100 ({reddit_sentiment['sentiment_label']})
Posts Analyzed: {reddit_sentiment['posts_analyzed']}
Positive Signals: {reddit_sentiment['positive_signals']}
Negative Signals: {reddit_sentiment['negative_signals']}
""")

    context = "\n".join(context_parts)

    prompt = f"""You are a professional crypto analyst at a Bloomberg-style terminal.
Analyze the following cryptocurrency data and provide:

1. An overall score from 0-100 (0=Strong Sell, 100=Strong Buy)
2. A sentiment label (Strong Sell / Bearish / Neutral / Bullish / Strong Buy)
3. A risk level (Low / Medium / High / Very High)
4. 3-5 bullish factors (brief, specific)
5. 3-5 bearish factors or risks (brief, specific)
6. A natural-language "Explain Why" paragraph (2-4 sentences) that explains why the coin is moving today in plain English, suitable for a beginner trader. Focus on the most impactful factors.

DATA:
{context}

Respond in this exact JSON format:
{{
  "score": <number 0-100>,
  "sentiment": "<string>",
  "risk_level": "<string>",
  "bullish_factors": ["<string>", ...],
  "bearish_factors": ["<string>", ...],
  "risks": ["<string>", ...],
  "explanation": "<string>"
}}
"""

    cache_key = f"openai_analysis_{coin_symbol.lower()}"

    async def _fetch():
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.groq_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.groq_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 800,
                        "response_format": {"type": "json_object"},
                    },
                )
                resp.raise_for_status()
                result = resp.json()

                content = result["choices"][0]["message"]["content"]
                analysis = json.loads(content)
                analysis["source"] = "groq"
                analysis["model"] = settings.groq_model
                return analysis

        except json.JSONDecodeError as e:
            logger.error(f"OpenAI response parse error: {e}")
            return None
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None

    return await cache.get_or_fetch(cache_key, _fetch, ttl=300)  # Cache for 5 min
