"""
CryptoTerminal — Application Configuration
Reads from .env file and provides typed settings.
"""

from __future__ import annotations

from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field

import os

BASE_DIR = Path(__file__).resolve().parent.parent
IS_VERCEL = os.environ.get("VERCEL") == "1" or os.environ.get("VERCEL_ENV") is not None


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    # ── API Keys ──
    coingecko_api_key: str = Field(default="", alias="COINGECKO_API_KEY")
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama3-8b-8192", alias="GROQ_MODEL")
    reddit_client_id: str = Field(default="", alias="REDDIT_CLIENT_ID")
    reddit_client_secret: str = Field(default="", alias="REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = Field(default="CryptoTerminal/1.0", alias="REDDIT_USER_AGENT")

    # ── Server ──
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # ── Paths ──
    static_dir: Path = BASE_DIR / "static"
    data_dir: Path = Path("/tmp") if IS_VERCEL else BASE_DIR / "data"
    db_path: Path = Path("/tmp/cryptoterminal.db") if IS_VERCEL else BASE_DIR / "data" / "cryptoterminal.db"

    # ── Cache TTL (seconds) ──
    cache_ttl_market: int = 60
    cache_ttl_coin: int = 30
    cache_ttl_chart: int = 120
    cache_ttl_news: int = 300
    cache_ttl_fear_greed: int = 600
    cache_ttl_trending: int = 120
    cache_ttl_search: int = 600
    cache_ttl_dex: int = 60
    cache_ttl_defi: int = 120
    cache_ttl_reddit: int = 300

    # ── CoinGecko ──
    coingecko_base_url: str = "https://api.coingecko.com/api/v3"
    coingecko_pro_url: str = "https://pro-api.coingecko.com/api/v3"

    # ── GeckoTerminal ──
    gecko_terminal_base_url: str = "https://api.geckoterminal.com/api/v2"

    # ── DexScreener ──
    dexscreener_base_url: str = "https://api.dexscreener.com"

    # ── DefiLlama ──
    defillama_base_url: str = "https://api.llama.fi"
    defillama_coins_url: str = "https://coins.llama.fi"
    defillama_stablecoins_url: str = "https://stablecoins.llama.fi"

    # ── Fear & Greed ──
    fear_greed_url: str = "https://api.alternative.me/fng/"

    # ── Reddit ──
    reddit_oauth_url: str = "https://oauth.reddit.com"
    reddit_token_url: str = "https://www.reddit.com/api/v1/access_token"

    @property
    def coingecko_url(self) -> str:
        """Use pro URL if API key is set, otherwise free tier."""
        if self.coingecko_api_key:
            return self.coingecko_pro_url
        return self.coingecko_base_url

    @property
    def has_groq(self) -> bool:
        return bool(self.groq_api_key)

    @property
    def has_reddit(self) -> bool:
        return bool(self.reddit_client_id and self.reddit_client_secret)

    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Singleton settings instance."""
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return settings
