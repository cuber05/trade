"""
CryptoTerminal — Groq AI Service
Powers the advanced AI analysis and "Explain Why" feature.
Uses the user's professional system prompt for Bloomberg-grade analysis.
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

# ── System Prompt ──────────────────────────────────────────────────
SYSTEM_PROMPT = """You are CryptoTerminal AI, a crypto analyst.
Analyze the provided market data. DO NOT predict the future or recommend buying.

CRITICAL ANALYSIS:
1. Overall Market: Bullish/bearish/neutral? How does BTC affect this coin?
2. Sector Comparison: Compare against provided sector peers. Is this a sector rally or coin-specific move? Name specific peers and numbers.
3. Momentum/Liquidity: High Volume/MCap ratio (>10%) means high activity. Compare volume to typical.
4. Community/Dev: Summarize Reddit sentiment and dev activity.
5. Risks & Opportunities: List key risks, warning signs, and catalysts.
6. Explain Why: WHY is the price moving? (e.g., sector rally, exchange listing, whale, following BTC).

Scoring:
90-100: Exceptional, strong fundamentals.
75-89: Strong setup, manageable risks.
60-74: Mixed outlook.
40-59: Weak setup.
20-39: Very weak.
0-19: Extremely risky.
Confidence: High if data agrees, Low if conflicting/missing.

Respond ONLY with valid JSON."""


async def generate_ai_analysis(
    coin_data: dict,
    market_context: dict | None = None,
    fear_greed: dict | None = None,
    reddit_sentiment: dict | None = None,
    defi_data: dict | None = None,
    sector_peers: list[dict] | None = None,
    trending_data: dict | None = None,
) -> dict | None:
    """
    Generate an advanced AI analysis using Groq.
    Returns None if Groq is not configured (caller should use built-in engine).
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
    ath = md.get("ath", {}).get("usd", 0)
    ath_pct = md.get("ath_change_percentage", {}).get("usd", 0) or 0
    circulating = md.get("circulating_supply", "N/A")
    max_supply = md.get("max_supply", "N/A")
    fdv = md.get("fully_diluted_valuation", {}).get("usd", 0)
    vol_mcap_ratio = (volume / mcap * 100) if mcap else 0

    context_parts.append(f"""
COIN: {coin_name} ({coin_symbol})
Price: ${price:,.8g}
24h Change: {pct_24h:+.2f}%
7d Change: {pct_7d:+.2f}%
30d Change: {pct_30d:+.2f}%
Market Cap: ${mcap:,.0f} (Rank #{rank})
24h Volume: ${volume:,.0f}
Volume/MCap Ratio: {vol_mcap_ratio:.2f}%
All Time High: ${ath:,.8g}
Distance from ATH: {ath_pct:.1f}%
Fully Diluted Valuation: ${fdv:,.0f}
Circulating Supply: {circulating}
Max Supply: {max_supply}
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
        total_mcap = gd.get("total_market_cap", {}).get("usd", 0)
        context_parts.append(f"""
GLOBAL MARKET CONTEXT:
Total Crypto Market Cap: ${total_mcap:,.0f}
Market Cap Change 24h: {gd.get('market_cap_change_percentage_24h_usd', 0):.2f}%
BTC Dominance: {gd.get('market_cap_percentage', {}).get('btc', 0):.1f}%
ETH Dominance: {gd.get('market_cap_percentage', {}).get('eth', 0):.1f}%
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

    # Sector peers comparison — critical for answering "Is this a sector rally?"
    # Sector peers comparison
    if sector_peers and isinstance(sector_peers, list) and len(sector_peers) > 0:
        coin_id = coin_data.get("id", "")
        peers_lines = []
        for p in sector_peers[:4]:
            if p.get("id") == coin_id:
                continue
            if len(peers_lines) >= 3:
                break
            p_name = p.get("name", "?")
            p_symbol = (p.get("symbol", "?")).upper()
            p_pct24 = p.get("price_change_percentage_24h", 0) or 0
            peers_lines.append(f"- {p_name} ({p_symbol}): 24h {p_pct24:+.1f}%")
        if peers_lines:
            context_parts.append(f"""
SECTOR PEERS (Compare to detect sector rally):
{chr(10).join(peers_lines)}
""")

    # Trending coins
    if trending_data and trending_data.get("coins"):
        trending_lines = []
        for item in trending_data["coins"][:3]:
            tc = item.get("item", {})
            t_name = tc.get("name", "?")
            t_pct24 = tc.get("data", {}).get("price_change_percentage_24h", {}).get("usd", 0) or 0
            trending_lines.append(f"- {t_name}: {t_pct24:+.1f}%")
        if trending_lines:
            context_parts.append(f"""
TRENDING:
{chr(10).join(trending_lines)}
""")

    context = "\n".join(context_parts)

    user_prompt = f"""Analyze the following cryptocurrency using only the supplied data.

DATA:
{context}

Respond in this exact JSON format only, no markdown, no extra text:
{{
  "score": <number 0-100>,
  "confidence": <number 0-100>,
  "market_sentiment": "<Bullish | Neutral | Bearish>",
  "risk": "<Low | Medium | High | Very High>",
  "investment_style": "<Long Term | Swing Trade | Momentum Trade | High Risk Speculation>",
  "summary": "<2-3 sentence professional summary>",
  "bullish_factors": ["<string>", ...],
  "bearish_factors": ["<string>", ...],
  "opportunities": ["<string>", ...],
  "risks": ["<string>", ...],
  "market_context": "<1-2 sentences on how the overall market and BTC dominance affect this coin>",
  "sector_comparison": "<1-2 sentences comparing this coin's performance to its sector peers. Is this a sector rally or coin-specific? Name specific peers and their numbers.>",
  "explain_why": "<3-5 sentence natural language explanation answering: WHY is this coin moving today? Reference sector peer data, volume patterns, trending status, and BTC correlation. Written for a beginner trader.>",
  "what_to_watch_next": ["<string>", ...],
  "verdict": "<Avoid | Watch | Consider | Strong Momentum>"
}}"""

    cache_key = f"groq_analysis_{coin_symbol.lower()}"

    async def _fetch():
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                resp = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.groq_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.groq_model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.3,
                        "max_tokens": 800,
                        "response_format": {"type": "json_object"},
                    },
                )
                resp.raise_for_status()
                result = resp.json()

                content = result["choices"][0]["message"]["content"]
                analysis = json.loads(content)

                # Normalize field names for backwards compat with frontend
                if "market_sentiment" in analysis and "sentiment" not in analysis:
                    analysis["sentiment"] = analysis["market_sentiment"]
                if "risk" in analysis and "risk_level" not in analysis:
                    analysis["risk_level"] = analysis["risk"]
                if "explain_why" in analysis and "explanation" not in analysis:
                    analysis["explanation"] = analysis["explain_why"]

                analysis["source"] = "groq"
                analysis["model"] = settings.groq_model
                return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Groq response parse error: {e}")
            return None
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return None

    return await cache.get_or_fetch(cache_key, _fetch, ttl=300)  # Cache for 5 min
