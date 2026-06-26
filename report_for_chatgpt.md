# CryptoTerminal Architecture & Feature Report

*This document is a comprehensive breakdown of the CryptoTerminal application, its folder structure, features, APIs, and AI integrations.*

## 1. Folder Structure & Files

The application follows a clean decoupling of a FastAPI Python backend serving a Vanilla JavaScript Single Page Application (SPA).

```text
Trade/
├── app/                        # Backend (FastAPI)
│   ├── routers/                # API Endpoints
│   │   ├── alerts.py           # CRUD for price/volume alerts
│   │   ├── coins.py            # Deep coin analysis & AI routes
│   │   ├── dex_defi.py         # DexScreener & DefiLlama endpoints
│   │   └── market.py           # Dashboard feeds (Trending, global, heatmaps)
│   ├── services/               # External API integrations
│   │   ├── coingecko.py        # Core market data
│   │   ├── defillama.py        # TVL and stablecoin data
│   │   ├── dexscreener.py      # Trending DEX tokens
│   │   ├── gecko_terminal.py   # Liquidity pool stats
│   │   ├── openai_service.py   # AI Analysis Engine (Now using Groq API)
│   │   └── reddit.py           # Community sentiment
│   ├── cache.py                # Asynchronous TTL Cache (in-memory)
│   ├── config.py               # Environment variables & Vercel pathing logic
│   ├── database.py             # SQLite setup for local persistence
│   └── main.py                 # FastAPI application entry point
├── data/                       # Local SQLite Database (falls back to /tmp on Vercel)
│   └── cryptoterminal.db
├── static/                     # Frontend (SPA)
│   ├── css/                    # Custom styling (No frameworks)
│   │   ├── alerts.css, animations.css, base.css, coin-detail.css, 
│   │   ├── components.css, dashboard.css, layout.css, variables.css
│   ├── js/                     # Vanilla JS Modules
│   │   ├── alerts.js           # Alert management logic
│   │   ├── api.js              # Fetch wrappers for backend calls
│   │   ├── app.js              # Main SPA router & event listeners (Ctrl+K)
│   │   ├── charts.js           # Chart.js & TradingView abstractions
│   │   ├── coin-detail.js      # Deep analysis UI controller
│   │   ├── dashboard.js        # Home page feed controller
│   │   ├── learn.js            # Academy logic
│   │   ├── markets.js          # Top 100 table logic
│   │   ├── store.js            # Global state management
│   │   └── utils.js            # DOM helpers, formatters, toasts
│   └── index.html              # Main App Shell
├── .env                        # Secret keys
├── requirements.txt            # Python dependencies
└── vercel.json                 # Vercel deployment config
```

---

## 2. API & Data Resources Used

We aggregated a massive amount of data to build a true "Bloomberg Terminal" experience.

1. **CoinGecko API (Free Tier):** Used for core pricing, market caps, 24h volume, historical charts, circulating supplies, and global market state.
2. **DexScreener API (Free):** Pulls trending newly-launched meme coins and DEX pairs.
3. **GeckoTerminal API (Free):** Supplements DEX data with deep liquidity pool statistics.
4. **DefiLlama API (Free):** Fetches Total Value Locked (TVL) metrics and stablecoin supply data.
5. **Alternative.me (Free):** Used to fetch the daily "Fear & Greed Index."
6. **Reddit API:** Pulls recent posts from subreddits like `r/CryptoCurrency` to perform sentiment analysis on retail chatter.
7. **Groq API (`llama3-8b-8192`):** Powers the advanced "Explain Why" feature and algorithmic grading.

---

## 3. Where is Groq (Llama) Used?

The Groq API (using the `llama3-8b-8192` model) serves as the core intelligence engine for the **Coin Analysis Page**.

When a user clicks on a specific coin and clicks **"Explain Why"**, the backend (`app/services/openai_service.py`, repurposed for Groq's OpenAI-compatible endpoint) aggregates:

- Price action & distance from All-Time High
- GitHub commits and developer stars
- Reddit community sentiment scores
- Fear & Greed Index

This massive data payload is injected into a strict prompt. The Llama 3 model processes the context and returns a highly structured JSON response containing:

1. An overall score (0-100).
2. A Risk Level classification.
3. Specific Bullish/Bearish technical & social factors.
4. A natural language summary explaining *why* the token's price is moving today.

---

## 4. Pages & Feature Breakdown

### A. Dashboard

The main command center.

- **Top Metrics:** Total market cap, 24h volume, BTC dominance.
- **Fear & Greed:** A live visual gauge of market psychology.
- **Trending/Gainers/Losers:** Real-time feeds of tokens experiencing high volatility.
- **Market Heatmap:** A visual block representation of the market (green/red blocks based on 24h or 7d performance).

### B. Markets

A deep-dive data table.

- Displays the top 100-250 coins by market cap.
- Sortable by 1h, 24h, and 7d price changes.
- Features mini 7-day sparkline charts generated dynamically for every row.
- Filterable by categories (DeFi, Layer 1s, Meme tokens).

### C. Coin Analysis

Accessed by clicking any coin (or using global `Ctrl+K` search).

- **Interactive Charts:** Users can toggle between TradingView Candlestick charts and Line/Area charts (1D up to Max historical data).
- **Market Stats:** Detailed metrics including FDV (Fully Diluted Valuation) and volume-to-mcap ratios.
- **AI Analysis:** Where the Groq Llama model analyzes the coin and generates the "Explain Why" narrative.

### D. Watchlist

- **What it is:** A personalized tracking board for tokens you care about.
- **Usage:** Users click the "Star" or "Add to Watchlist" button on any coin. The coin is saved to their local database and appears on this page with live price feeds. Perfect for keeping an eye on highly volatile tokens without losing them in the main market table.

### E. Alerts

- Users can set programmatic triggers for specific coins.
- **Supported conditions:** Notify if a coin goes *above/below* a specific price, if trading volume spikes by X%, or if the global Fear & Greed index shifts dramatically.
- Background tasks in the backend evaluate these conditions against live data.

### F. Learn (Crypto Academy)

- **What it is:** A built-in educational wiki for beginner retail traders.
- **Usage:** Currently contains interactive cards explaining foundational trading concepts like "Understanding Market Cap," "Reading Trading Volume," and "RSI & MACD Basics." When a user clicks a card, a modal opens with a detailed lesson and "Pro Tips." This ensures the terminal isn't just a tool, but an educational platform.
