"""
CryptoTerminal — AI Analysis Engine
Generates bullish/bearish scores and "Explain Why" narratives
using available market data (no external AI API required).
"""

from __future__ import annotations

import math
import logging
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


def analyze_coin(coin_data: dict, global_data: dict | None = None, fear_greed: dict | None = None) -> dict:
    """
    Generate a comprehensive AI analysis for a coin.
    Returns score (0-100), sentiment, reasons, risks, and explanation.
    """
    score = 50  # Start neutral
    reasons = []
    risks = []
    bullish_factors = []
    bearish_factors = []

    md = coin_data.get("market_data", {})
    community = coin_data.get("community_data", {})
    developer = coin_data.get("developer_data", {})

    # ── 1. Price Action (weight: 25) ──
    pct_24h = md.get("price_change_percentage_24h", 0) or 0
    pct_7d = md.get("price_change_percentage_7d", 0) or 0
    pct_30d = md.get("price_change_percentage_30d", 0) or 0

    # Short-term momentum
    if pct_24h > 10:
        score += 8
        bullish_factors.append(f"Strong 24h gain of {pct_24h:+.1f}%")
    elif pct_24h > 3:
        score += 4
        bullish_factors.append(f"Positive 24h movement of {pct_24h:+.1f}%")
    elif pct_24h < -10:
        score -= 8
        bearish_factors.append(f"Sharp 24h decline of {pct_24h:+.1f}%")
    elif pct_24h < -3:
        score -= 4
        bearish_factors.append(f"Negative 24h movement of {pct_24h:+.1f}%")

    # Weekly trend
    if pct_7d > 20:
        score += 6
        bullish_factors.append(f"Strong weekly rally of {pct_7d:+.1f}%")
    elif pct_7d > 5:
        score += 3
        bullish_factors.append(f"Positive weekly trend of {pct_7d:+.1f}%")
    elif pct_7d < -20:
        score -= 6
        bearish_factors.append(f"Severe weekly decline of {pct_7d:+.1f}%")
    elif pct_7d < -5:
        score -= 3
        bearish_factors.append(f"Negative weekly trend of {pct_7d:+.1f}%")

    # Monthly trend
    if pct_30d > 30:
        score += 5
        bullish_factors.append(f"Strong monthly performance of {pct_30d:+.1f}%")
    elif pct_30d < -30:
        score -= 5
        bearish_factors.append(f"Poor monthly performance of {pct_30d:+.1f}%")

    # ── 2. Volume Analysis (weight: 20) ──
    volume = md.get("total_volume", {}).get("usd", 0) or 0
    mcap = md.get("market_cap", {}).get("usd", 0) or 0

    if mcap > 0 and volume > 0:
        vol_mcap_ratio = volume / mcap
        if vol_mcap_ratio > 0.3:
            score += 6
            bullish_factors.append(f"Very high volume/market cap ratio ({vol_mcap_ratio:.1%})")
        elif vol_mcap_ratio > 0.1:
            score += 3
            bullish_factors.append(f"Healthy trading volume")
        elif vol_mcap_ratio < 0.02:
            score -= 4
            bearish_factors.append(f"Low trading volume relative to market cap")
            risks.append("Low liquidity — large orders may cause significant price impact")

    # ── 3. Market Cap & Rank (weight: 10) ──
    rank = md.get("market_cap_rank", 999) or 999
    if rank <= 10:
        score += 5
        bullish_factors.append(f"Top 10 cryptocurrency by market cap (#{rank})")
    elif rank <= 50:
        score += 3
        bullish_factors.append(f"Top 50 cryptocurrency (#{rank})")
    elif rank <= 100:
        score += 1
    elif rank > 500:
        score -= 3
        risks.append(f"Low market cap ranking (#{rank}) — higher volatility risk")

    # ── 4. ATH Distance (weight: 10) ──
    ath = md.get("ath", {}).get("usd", 0) or 0
    current_price = md.get("current_price", {}).get("usd", 0) or 0
    if ath > 0 and current_price > 0:
        ath_pct = md.get("ath_change_percentage", {}).get("usd", 0) or 0
        if ath_pct > -10:
            score += 4
            bullish_factors.append(f"Near all-time high ({ath_pct:+.1f}% from ATH)")
        elif ath_pct < -80:
            score -= 3
            bearish_factors.append(f"Down {abs(ath_pct):.0f}% from all-time high")
            risks.append("Significant distance from ATH — may indicate declining interest")
        elif ath_pct < -50:
            # Could be a buying opportunity
            score += 1
            bullish_factors.append(f"Potential recovery play — down {abs(ath_pct):.0f}% from ATH")

    # ── 5. Supply Metrics (weight: 10) ──
    circulating = md.get("circulating_supply", 0) or 0
    total_supply = md.get("total_supply", 0)
    max_supply = md.get("max_supply", 0)

    if max_supply and circulating:
        supply_ratio = circulating / max_supply
        if supply_ratio > 0.9:
            score += 3
            bullish_factors.append(f"High circulating supply ratio ({supply_ratio:.0%}) — low dilution risk")
        elif supply_ratio < 0.3:
            score -= 2
            risks.append(f"Only {supply_ratio:.0%} of max supply in circulation — potential future dilution")

    # ── 6. Community & Developer (weight: 15) ──
    if community:
        twitter_followers = community.get("twitter_followers", 0) or 0
        reddit_subs = community.get("reddit_subscribers", 0) or 0

        if twitter_followers > 1_000_000:
            score += 4
            bullish_factors.append(f"Large social following ({twitter_followers:,} Twitter followers)")
        elif twitter_followers > 100_000:
            score += 2
            bullish_factors.append(f"Active social presence ({twitter_followers:,} followers)")

        if reddit_subs > 100_000:
            score += 2
            bullish_factors.append(f"Strong Reddit community ({reddit_subs:,} subscribers)")

    if developer:
        commits_4w = developer.get("commit_count_4_weeks", 0) or 0
        if commits_4w > 100:
            score += 5
            bullish_factors.append(f"Very active development ({commits_4w} commits in 4 weeks)")
        elif commits_4w > 20:
            score += 3
            bullish_factors.append(f"Active development ({commits_4w} commits in 4 weeks)")
        elif commits_4w == 0:
            score -= 3
            bearish_factors.append("No development activity in the last 4 weeks")
            risks.append("Inactive development — potential abandoned project")

        stars = developer.get("stars", 0) or 0
        if stars > 5000:
            score += 2
            bullish_factors.append(f"Popular open-source project ({stars:,} GitHub stars)")

    # ── 7. Fear & Greed Context (weight: 10) ──
    if fear_greed and fear_greed.get("current"):
        fg_value = fear_greed["current"]["value"]
        fg_class = fear_greed["current"]["classification"]

        if fg_value < 25:
            score += 3  # Contrarian — extreme fear is buying opportunity
            bullish_factors.append(f"Market in Extreme Fear ({fg_value}/100) — contrarian buy signal")
        elif fg_value < 40:
            score += 1
            bullish_factors.append(f"Market Fear ({fg_value}/100) — potential accumulation zone")
        elif fg_value > 80:
            score -= 3
            bearish_factors.append(f"Market in Extreme Greed ({fg_value}/100) — increased correction risk")
            risks.append("Extreme Greed often precedes market corrections")
        elif fg_value > 65:
            score -= 1
            bearish_factors.append(f"Market Greed ({fg_value}/100) — exercise caution")

    # ── 8. Bitcoin Correlation (weight: 5) ──
    if global_data and global_data.get("data"):
        btc_dom = global_data["data"].get("market_cap_percentage", {}).get("btc", 0)
        market_change = global_data["data"].get("market_cap_change_percentage_24h_usd", 0) or 0

        if market_change > 3:
            score += 2
            bullish_factors.append(f"Overall crypto market is up {market_change:.1f}% today")
        elif market_change < -3:
            score -= 2
            bearish_factors.append(f"Overall crypto market is down {abs(market_change):.1f}% today")

    # ── Clamp score ──
    score = max(0, min(100, score))

    # ── Determine sentiment ──
    if score >= 75:
        sentiment = "Strong Buy"
        sentiment_color = "#00ff88"
    elif score >= 60:
        sentiment = "Bullish"
        sentiment_color = "#00cc6a"
    elif score >= 45:
        sentiment = "Neutral"
        sentiment_color = "#ffd60a"
    elif score >= 30:
        sentiment = "Bearish"
        sentiment_color = "#ff9500"
    else:
        sentiment = "Strong Sell"
        sentiment_color = "#ff3b5c"

    # ── Risk level ──
    if rank <= 20 and score >= 50:
        risk_level = "Low"
    elif rank <= 100 and score >= 40:
        risk_level = "Medium"
    elif rank > 200 or score < 30:
        risk_level = "Very High"
    else:
        risk_level = "High"

    # ── Generate Explanation ("Explain Why") ──
    explanation = _generate_explanation(
        coin_data, pct_24h, pct_7d, bullish_factors, bearish_factors,
        fear_greed, global_data
    )

    return {
        "score": score,
        "sentiment": sentiment,
        "sentiment_color": sentiment_color,
        "risk_level": risk_level,
        "bullish_factors": bullish_factors,
        "bearish_factors": bearish_factors,
        "risks": risks,
        "explanation": explanation,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _generate_explanation(
    coin_data: dict,
    pct_24h: float,
    pct_7d: float,
    bullish: list[str],
    bearish: list[str],
    fear_greed: dict | None,
    global_data: dict | None,
) -> str:
    """Generate a natural-language 'Explain Why' narrative."""
    name = coin_data.get("name", "This coin")
    symbol = coin_data.get("symbol", "").upper()

    parts = []

    # Price context
    if pct_24h >= 0:
        parts.append(f"{name} ({symbol}) is up {pct_24h:.1f}% today")
    else:
        parts.append(f"{name} ({symbol}) is down {abs(pct_24h):.1f}% today")

    # Add main drivers
    drivers = []
    if global_data and global_data.get("data"):
        market_change = global_data["data"].get("market_cap_change_percentage_24h_usd", 0) or 0
        if abs(market_change) > 1:
            direction = "up" if market_change > 0 else "down"
            drivers.append(f"the overall crypto market is {direction} {abs(market_change):.1f}%")

    if fear_greed and fear_greed.get("current"):
        fg = fear_greed["current"]
        if fg["value"] < 30:
            drivers.append(f"market sentiment is fearful ({fg['classification']}, {fg['value']}/100)")
        elif fg["value"] > 70:
            drivers.append(f"market sentiment is greedy ({fg['classification']}, {fg['value']}/100)")

    # Volume context
    md = coin_data.get("market_data", {})
    vol_change = md.get("volume_change_percentage_24h") if md else None
    if vol_change and abs(vol_change) > 10:
        direction = "increased" if vol_change > 0 else "decreased"
        drivers.append(f"trading volume has {direction} {abs(vol_change):.0f}%")

    # 7d trend context
    if abs(pct_7d) > 5:
        trend = "uptrend" if pct_7d > 0 else "downtrend"
        drivers.append(f"it has been in a {trend} over the past week ({pct_7d:+.1f}%)")

    if drivers:
        parts.append("because " + ", ".join(drivers[:-1]))
        if len(drivers) > 1:
            parts[-1] += f", and {drivers[-1]}"
        elif drivers:
            parts[-1] = parts[0] + " because " + drivers[0]

    # Catalyst check
    dev = coin_data.get("developer_data", {})
    commits = dev.get("commit_count_4_weeks", 0) if dev else 0
    if commits > 50:
        parts.append(f"Active development ({commits} commits recently) shows the project is being maintained.")
    elif commits == 0 and coin_data.get("market_data", {}).get("market_cap_rank", 999) > 100:
        parts.append("There is no recent development activity, which may concern long-term holders.")

    result = ". ".join(parts) + "."
    return result


def generate_quick_summary(coin_data: dict) -> dict:
    """Generate a quick one-line summary for a coin."""
    md = coin_data.get("market_data", {})
    pct_24h = md.get("price_change_percentage_24h", 0) or 0
    price = md.get("current_price", {}).get("usd", 0) or 0
    mcap = md.get("market_cap", {}).get("usd", 0) or 0
    rank = md.get("market_cap_rank", 0) or 0

    return {
        "price": price,
        "change_24h": pct_24h,
        "market_cap": mcap,
        "rank": rank,
        "direction": "up" if pct_24h >= 0 else "down",
    }
