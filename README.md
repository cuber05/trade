# CryptoTerminal

CryptoTerminal is a professional-grade cryptocurrency intelligence dashboard designed for retail crypto traders. Built with a dark, Bloomberg Terminal-style aesthetic, it provides traders with the same caliber of analysis tools that institutions use, including real-time market data, AI-driven sentiment analysis, and portfolio tracking.

## Overview

CryptoTerminal goes beyond basic price tracking by aggregating data from multiple decentralized and centralized sources. It features a built-in AI engine that analyzes market sentiment, technical indicators, and community metrics to provide a comprehensive "Explain Why" narrative for any coin's price movement.

## Key Features

### 1. Market Dashboard
- Global Market Metrics: Track total crypto market cap, 24-hour volume, and Bitcoin/Ethereum dominance.
- Fear & Greed Index: Real-time gauge with a 30-day historical view to measure overall market sentiment.
- Trending Coins: Live feed of what is currently hot across major aggregators.
- Top Gainers & Losers: Quickly identify the biggest 24-hour market movers.
- Market Heatmap: Visual grid of market performance categorized by 24h or 7d price changes.
- Market Dominance: Interactive pie chart of BTC, ETH, and altcoin dominance.

### 2. Deep Coin Analysis
- Interactive Charts: View TradingView-style interactive candlestick and area charts for any cryptocurrency.
- Comprehensive Market Data: Access price, volume, market cap, ATH/ATL, and circulating/max supply.
- Developer & Community Activity: Track GitHub commits, stars, Twitter followers, and Reddit subscribers to gauge project health.
- Reddit Sentiment: Pulls live discussions from subreddits like r/CryptoCurrency to determine if retail sentiment is bullish or bearish.

### 3. AI-Powered Rating System
- Score (0-100): Multi-factor algorithmic analysis scoring coins from Strong Sell to Strong Buy.
- Risk Assessment: Classifies investments as Low, Medium, High, or Very High risk based on volatility and market cap.
- Factor Breakdown: Explicit lists of bullish and bearish signals driving the AI's score.
- "Explain Why" Button: Generates a natural-language explanation of why a coin is moving today, combining price action, news, and sentiment into a digestible summary.

### 4. Portfolio Management
- Add Holdings: Input your buy price, amount, and date.
- Real-time P&L: Automatically calculates profit and loss based on current market prices.
- Allocation Chart: Visual breakdown of your portfolio distribution.

### 5. Watchlist & Alerts
- Custom Watchlist: Save and monitor your favorite coins in one place.
- Advanced Alerts: Set custom triggers for price thresholds (above/below), volume spikes, percentage changes, or shifts in the Fear & Greed index.

### 6. Crypto Academy (Learn)
- Built-in educational resources explaining core concepts like Market Cap, Trading Volume, RSI, and MACD to help beginner traders make informed decisions.

## Architecture & Tech Stack

CryptoTerminal is a modern Single Page Application (SPA) powered by a fast, asynchronous backend.

- Backend: Python 3.11+, FastAPI, Uvicorn
- Database: SQLite (via aiosqlite) for local persistence of portfolios and alerts
- Caching: In-memory TTL caching to prevent rate-limiting from external APIs
- Frontend: Vanilla HTML, CSS (Custom Design System), and JavaScript
- Charts: TradingView Lightweight Charts, Chart.js

### API Integrations
The application seamlessly aggregates data from:
- CoinGecko (Prices, market data, charts)
- DexScreener (Trending pairs, liquidity, new tokens)
- GeckoTerminal (DEX analytics, pools)
- DefiLlama (TVL, chains, stablecoins)
- Alternative.me (Fear & Greed Index)
- Reddit API (Community sentiment)
- OpenAI (GPT-4o-mini for advanced AI analysis)

*Note: DexScreener, GeckoTerminal, DefiLlama, and Alternative.me are completely free public APIs and do not require API keys.*

## Quick Start Guide

### Prerequisites
- Python 3.11 or higher installed on your system.

### Installation

1. Clone the repository and navigate into the directory:
   git clone https://github.com/yourusername/cryptoterminal.git
   cd cryptoterminal

2. Create and activate a virtual environment:
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate

3. Install the required dependencies:
   pip install -r requirements.txt

4. Configure the environment:
   Copy the `.env.example` file to a new file named `.env`. 
   cp .env.example .env

   You can optionally add your CoinGecko, OpenAI, and Reddit API keys to the `.env` file for higher rate limits and advanced AI features. The app will gracefully fall back to free tiers and internal algorithms if these are left blank.

5. Start the development server:
   uvicorn app.main:app --reload --port 8000

6. Access the application:
   Open your web browser and navigate to http://localhost:8000

## Usage Instructions

- Navigating the App: Use the left sidebar to switch between the Dashboard, Markets, Portfolio, Watchlist, Alerts, and Learn sections.
- Analyzing a Coin: Click on any coin from the Dashboard heatmap, Trending list, or Markets table to open the detailed Coin Analysis page.
- Using AI Analysis: On the Coin Analysis page, wait for the AI score to generate. Click "Explain Why" to read the AI's natural language breakdown of the asset's current market position.
- Managing Portfolio: Go to the Portfolio tab, click "Add Holding", search for your coin, and enter your purchase details. The app will automatically track your P&L.
- Setting Alerts: Navigate to the Alerts tab to create custom notifications for price movements or market sentiment shifts.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
