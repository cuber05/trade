"""
CryptoTerminal — Fear & Greed Index Service
Fetches data from Alternative.me API.
"""

from __future__ import annotations

import httpx
import logging
from typing import Any

from app.config import get_settings
from app.cache import cache

logger = logging.getLogger(__name__)


async def get_fear_greed_index(limit: int = 30) -> dict | None:
    """
    Get Fear & Greed Index data.
    Returns current value + historical data.
    """
    settings = get_settings()
    cache_key = f"fear_greed_{limit}"

    async def _fetch():
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    settings.fear_greed_url,
                    params={"limit": limit, "format": "json"}
                )
                resp.raise_for_status()
                data = resp.json()

                if "data" not in data:
                    return None

                entries = data["data"]
                current = entries[0] if entries else None

                return {
                    "current": {
                        "value": int(current["value"]),
                        "classification": current["value_classification"],
                        "timestamp": current["timestamp"],
                    } if current else None,
                    "history": [
                        {
                            "value": int(e["value"]),
                            "classification": e["value_classification"],
                            "timestamp": e["timestamp"],
                        }
                        for e in entries
                    ]
                }
        except Exception as e:
            logger.error(f"Fear & Greed API error: {e}")
            return None

    return await cache.get_or_fetch(
        cache_key, _fetch, ttl=settings.cache_ttl_fear_greed
    )


def get_fg_color(value: int) -> str:
    """Get the appropriate color hex for a Fear & Greed value."""
    if value <= 20:
        return "#ff3b5c"   # Extreme Fear
    elif value <= 40:
        return "#ff9500"   # Fear
    elif value <= 60:
        return "#ffd60a"   # Neutral
    elif value <= 80:
        return "#00cc6a"   # Greed
    else:
        return "#00ff88"   # Extreme Greed


def get_fg_label(value: int) -> str:
    """Get the label for a Fear & Greed value."""
    if value <= 20:
        return "Extreme Fear"
    elif value <= 40:
        return "Fear"
    elif value <= 60:
        return "Neutral"
    elif value <= 80:
        return "Greed"
    else:
        return "Extreme Greed"
