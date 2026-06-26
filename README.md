<p align="center">
  <img src="https://img.shields.io/badge/CryptoTerminal-v1.0-00ff88?style=for-the-badge&logo=bitcoin&logoColor=white" alt="Version" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License" />
</p>

# 📊 CryptoTerminal

**AI-Powered Bloomberg Terminal for Retail Crypto Traders**

A professional-grade cryptocurrency intelligence dashboard that goes beyond basic price tracking. Built with a dark Bloomberg Terminal aesthetic, glassmorphism, and neon green accents — CryptoTerminal gives retail traders the same caliber of analysis tools that institutions use.

---

## ✨ Features

### 🏠 Dashboard
- **Global Market Overview** — Total crypto market cap, 24h volume, BTC dominance
- **Fear & Greed Index** — Real-time gauge with 30-day history
- **Trending Coins** — What's hot on CoinGecko right now
- **Top Gainers & Losers** — Biggest 24h movers
- **Market Heatmap** — Visual grid of market performance
- **Bitcoin Price Chart** — TradingView-style interactive chart
- **Market Dominance** — Pie chart of BTC/ETH/altcoin dominance

### 🔍 Coin Analysis
- **Live Price & Charts** — Interactive candlestick charts (TradingView Lightweight Charts)
- **Market Data** — Price, volume, market cap, ATH/ATL, circulating supply
- **Exchange Listings** — Where to trade
- **Developer Activity** — GitHub commits, stars, contributors
- **Community Metrics** — Twitter followers, Reddit subscribers

### 🤖 AI Rating System
- **Score 0–100** — Multi-factor algorithmic analysis
- **Bullish/Bearish Sentiment** — Clear directional signal
- **Risk Assessment** — Low / Medium / High / Very High
- **Factor Breakdown** — See exactly what's driving the score
- **"Explain Why" Button** — Natural-language explanation of why a coin is moving

### 💼 Portfolio Tracking
- **Add Holdings** — Track buy price, amount, date
- **Real-time P&L** — Profit/loss with current market prices
- **Allocation Chart** — Visual breakdown of your portfolio
- **Performance History** — Track your portfolio over time

### ⭐ Watchlist
- **Quick Add** — Add any coin to your watchlist
- **Live Prices** — Real-time price updates
- **Quick Actions** — Jump to analysis from watchlist

### 🔔 Alerts
- **Price Alerts** — Above/below thresholds
- **Volume Spike Alerts** — Catch unusual activity
- **Fear & Greed Alerts** — Market sentiment shifts
- **Alert History** — Review triggered alerts

### 📚 Crypto Academy
- **Market Cap** — What it means and why it matters
- **Volume** — Reading trading volume
- **RSI & MACD** — Technical indicators explained
- **Candlestick Patterns** — Reading charts like a pro
- **Support & Resistance** — Key price levels
- **Trading Psychology** — Managing emotions

---

## 🏗️ Architecture

```
CryptoTerminal/
├── app/                          # Python FastAPI Backend
│   ├── main.py                   # App entry point + static file serving
│   ├── config.py                 # Settings & environment variables
│   ├── cache.py                  # In-memory TTL cache
│   ├── database.py               # SQLite persistence (portfolio, alerts)
│   ├── routers/                  # API route handlers
│   │   ├── market.py             # /api/v1/market/* endpoints
│   │   ├── coins.py              # /api/v1/coins/* endpoints
│   │   ├── portfolio.py          # /api/v1/portfolio/* & watchlist
│   │   └── alerts.py             # /api/v1/alerts/* endpoints
│   └── services/                 # External API integrations
│       ├── coingecko.py          # CoinGecko API (prices, charts, etc.)
│       ├── fear_greed.py         # Alternative.me Fear & Greed Index
│       └── ai_engine.py          # Built-in AI analysis engine
├── static/                       # Frontend (served by FastAPI)
│   ├── index.html                # Single-page app shell
│   ├── css/                      # Stylesheets
│   │   ├── variables.css         # Design tokens
│   │   ├── base.css              # Reset & utilities
│   │   ├── layout.css            # App shell layout
│   │   ├── components.css        # Reusable components
│   │   ├── dashboard.css         # Dashboard grid
│   │   ├── coin-detail.css       # Coin analysis page
│   │   ├── portfolio.css         # Portfolio page
│   │   ├── alerts.css            # Alerts page
│   │   └── animations.css        # Micro-animations
│   └── js/                       # JavaScript modules
│       ├── app.js                # Main app controller & routing
│       ├── api.js                # Backend API client
│       ├── utils.js              # Formatting & helpers
│       ├── store.js              # Client-side state management
│       ├── charts.js             # Chart rendering (TradingView + Chart.js)
│       ├── dashboard.js          # Dashboard logic
│       ├── markets.js            # Markets table
│       ├── coin-detail.js        # Coin analysis page
│       ├── portfolio.js          # Portfolio management
│       ├── watchlist.js          # Watchlist management
│       ├── alerts.js             # Alert management
│       └── learn.js              # Crypto Academy content
├── data/                         # SQLite database (auto-created)
├── venv/                         # Python virtual environment
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container deployment
├── render.yaml                   # Render.com deployment
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore rules
└── README.md                     # You are here
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** installed
- **Git** (optional, for cloning)

### 1. Clone & Enter

```bash
git clone https://github.com/yourusername/cryptoterminal.git
cd cryptoterminal
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your API keys (optional — works without them)
```

### 5. Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 6. Open in Browser

Navigate to **[http://localhost:8000](http://localhost:8000)** 🎉

---

## 🔑 API Keys (Optional)

CryptoTerminal works out of the box with **no API keys** — using CoinGecko's free tier and Alternative.me's public API. Add keys to increase rate limits:

| API | Purpose | Free Tier | Get Key |
|-----|---------|-----------|---------|
| **CoinGecko** | Price, market, chart data | 10-30 calls/min | [coingecko.com/api](https://www.coingecko.com/en/api) |
| **CryptoPanic** | Crypto news feed | 5 calls/min | [cryptopanic.com/developers](https://cryptopanic.com/developers/api/) |

Add keys to your `.env` file:

```env
COINGECKO_API_KEY=your_key_here
CRYPTOPANIC_API_KEY=your_key_here
```

---

## 🌐 Deployment

### Deploy to Render.com (Recommended)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render will auto-detect the `render.yaml` config
5. Add your API keys as environment variables
6. Click **Deploy** ✅

### Deploy with Docker

```bash
# Build the image
docker build -t cryptoterminal .

# Run the container
docker run -p 8000:8000 --env-file .env cryptoterminal
```

### Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Deploy to Fly.io

```bash
fly launch
fly secrets set COINGECKO_API_KEY=your_key
fly deploy
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/market/global` | Global market data |
| `GET` | `/api/v1/market/fear-greed` | Fear & Greed Index |
| `GET` | `/api/v1/market/trending` | Trending coins |
| `GET` | `/api/v1/market/coins` | Coin listings (paginated) |
| `GET` | `/api/v1/market/gainers-losers` | Top gainers & losers |
| `GET` | `/api/v1/market/search?q=` | Search coins |
| `GET` | `/api/v1/coins/{id}` | Coin detail data |
| `GET` | `/api/v1/coins/{id}/chart` | Price chart data |
| `GET` | `/api/v1/coins/{id}/ohlc` | Candlestick data |
| `GET` | `/api/v1/coins/{id}/ai-analysis` | AI analysis & score |
| `GET` | `/api/v1/portfolio` | Get portfolio holdings |
| `POST` | `/api/v1/portfolio` | Add holding |
| `PUT` | `/api/v1/portfolio/{id}` | Update holding |
| `DELETE` | `/api/v1/portfolio/{id}` | Delete holding |
| `GET` | `/api/v1/watchlist` | Get watchlist |
| `POST` | `/api/v1/watchlist` | Add to watchlist |
| `DELETE` | `/api/v1/watchlist/{coin_id}` | Remove from watchlist |
| `GET` | `/api/v1/alerts` | Get alerts |
| `POST` | `/api/v1/alerts` | Create alert |
| `DELETE` | `/api/v1/alerts/{id}` | Delete alert |
| `PUT` | `/api/v1/alerts/{id}/toggle` | Toggle alert on/off |
| `GET` | `/api/health` | Health check |

Interactive API docs available at **`/docs`** (Swagger UI).

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11+, FastAPI, uvicorn |
| **Database** | SQLite (via aiosqlite) |
| **Caching** | In-memory TTL cache |
| **HTTP Client** | httpx (async) |
| **Frontend** | Vanilla HTML/CSS/JS |
| **Charts** | TradingView Lightweight Charts, Chart.js |
| **Icons** | Font Awesome 6 |
| **Fonts** | Inter, JetBrains Mono (Google Fonts) |

---

## 🗺️ Roadmap

- [ ] WebSocket support for real-time price streaming
- [ ] CryptoPanic news integration
- [ ] GeckoTerminal DEX/meme coin data
- [ ] Reddit sentiment analysis
- [ ] X (Twitter) sentiment tracking
- [ ] OpenAI-powered advanced AI analysis
- [ ] Push notifications (browser + mobile)
- [ ] Multi-currency support (EUR, GBP, INR)
- [ ] Export portfolio to CSV/PDF
- [ ] Dark/light theme toggle

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with ❤️ and ☕ for crypto traders who deserve better tools.
</p>
