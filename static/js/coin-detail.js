/**
 * CryptoTerminal — Coin Detail Module
 * Full coin analysis page with charts, AI rating, and "Explain Why".
 */

const CoinDetail = {
  _currentCoin: null,
  _chartDays: 7,
  _chartType: 'area', // 'area' or 'candle'

  async load(coinId) {
    this._currentCoin = coinId;
    const container = document.getElementById('coin-detail-content');
    container.innerHTML = '<div class="empty-state"><i class="fas fa-spinner spin"></i><h3>Loading analysis...</h3></div>';

    // Show the nav item
    const navItem = document.getElementById('nav-coin-detail');
    navItem.style.display = 'flex';

    const coinData = await API.getCoinDetail(coinId);
    if (!coinData || coinData.error) {
      container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><h3>Coin not found</h3><p>Could not load data for this coin.</p></div>';
      return;
    }

    this.render(coinData);
    this.loadChart(coinId, this._chartDays);
    this.loadAIAnalysis(coinId);
  },

  render(coin) {
    const md = coin.market_data || {};
    const price = md.current_price?.usd || 0;
    const pct24h = md.price_change_percentage_24h || 0;
    const pct7d = md.price_change_percentage_7d || 0;
    const pct30d = md.price_change_percentage_30d || 0;
    const mcap = md.market_cap?.usd || 0;
    const volume = md.total_volume?.usd || 0;
    const rank = md.market_cap_rank || '—';
    const ath = md.ath?.usd || 0;
    const athPct = md.ath_change_percentage?.usd || 0;
    const atl = md.atl?.usd || 0;
    const atlPct = md.atl_change_percentage?.usd || 0;
    const circulating = md.circulating_supply || 0;
    const total = md.total_supply || 0;
    const maxSupply = md.max_supply || 0;
    const fdv = md.fully_diluted_valuation?.usd || 0;
    const symbol = (coin.symbol || '').toUpperCase();

    // Developer data
    const dev = coin.developer_data || {};
    const commits = dev.commit_count_4_weeks || 0;
    const stars = dev.stars || 0;
    const forks = dev.forks || 0;

    // Community
    const community = coin.community_data || {};
    const twitter = community.twitter_followers || 0;
    const redditSubs = community.reddit_subscribers || 0;

    const container = document.getElementById('coin-detail-content');
    container.innerHTML = `
      <!-- Coin Header -->
      <div class="coin-header">
        <img class="coin-header-icon" src="${coin.image?.large || coin.image?.small || ''}" alt="${coin.name}" />
        <div class="coin-header-info">
          <div class="coin-header-name">
            ${coin.name}
            <span class="coin-header-symbol">${symbol}</span>
            <span class="coin-header-rank">Rank #${rank}</span>
          </div>
          <div>
            <span class="coin-header-price">${Utils.formatPrice(price)}</span>
            <span class="coin-header-change ${Utils.percentClass(pct24h)}">${Utils.formatPercent(pct24h)} (24h)</span>
          </div>
        </div>
        <div class="coin-header-actions">
          <button class="btn btn-outline btn-sm" onclick="CoinDetail.addToWatchlist('${coin.id}', '${symbol}', '${coin.name}', '${coin.image?.small || ''}')">
            <i class="fas fa-star"></i> Watchlist
          </button>
          <button class="btn btn-primary btn-sm" onclick="CoinDetail.addToPortfolio('${coin.id}', '${symbol}', '${coin.name}')">
            <i class="fas fa-plus"></i> Add to Portfolio
          </button>
        </div>
      </div>

      <!-- Detail Grid -->
      <div class="coin-detail-grid">
        <!-- Chart Panel -->
        <div class="panel coin-chart-panel">
          <div class="coin-chart-header">
            <div class="coin-chart-tabs">
              <button class="coin-chart-tab active" data-type="area" onclick="CoinDetail.switchChartType('area', this)">Area</button>
              <button class="coin-chart-tab" data-type="candle" onclick="CoinDetail.switchChartType('candle', this)">Candles</button>
            </div>
            <div class="coin-chart-tabs">
              <button class="coin-chart-tab" data-days="1" onclick="CoinDetail.switchChartDays(1, this)">1D</button>
              <button class="coin-chart-tab active" data-days="7" onclick="CoinDetail.switchChartDays(7, this)">7D</button>
              <button class="coin-chart-tab" data-days="30" onclick="CoinDetail.switchChartDays(30, this)">1M</button>
              <button class="coin-chart-tab" data-days="90" onclick="CoinDetail.switchChartDays(90, this)">3M</button>
              <button class="coin-chart-tab" data-days="365" onclick="CoinDetail.switchChartDays(365, this)">1Y</button>
              <button class="coin-chart-tab" data-days="max" onclick="CoinDetail.switchChartDays('max', this)">All</button>
            </div>
          </div>
          <div id="coin-tv-chart" class="coin-tv-chart"></div>
        </div>

        <!-- Stats Panel -->
        <div class="panel coin-stats-panel">
          <div class="panel-header">
            <h3><i class="fas fa-chart-bar"></i> Market Stats</h3>
          </div>
          <div class="panel-body">
            <div class="stat-item">
              <span class="stat-label">Market Cap</span>
              <span class="stat-value">${Utils.formatCurrency(mcap)}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">24h Volume</span>
              <span class="stat-value">${Utils.formatCurrency(volume)}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">FDV</span>
              <span class="stat-value">${fdv ? Utils.formatCurrency(fdv) : 'N/A'}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Vol/MCap</span>
              <span class="stat-value">${mcap ? (volume / mcap * 100).toFixed(2) + '%' : 'N/A'}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Circulating Supply</span>
              <span class="stat-value">${Utils.formatSupply(circulating, symbol)}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Total Supply</span>
              <span class="stat-value">${total ? Utils.formatSupply(total, symbol) : 'N/A'}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Max Supply</span>
              <span class="stat-value">${maxSupply ? Utils.formatSupply(maxSupply, symbol) : '∞'}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">ATH</span>
              <span class="stat-value">${Utils.formatPrice(ath)} <small class="${Utils.percentClass(athPct)}">(${Utils.formatPercent(athPct)})</small></span>
            </div>
            <div class="stat-item">
              <span class="stat-label">ATL</span>
              <span class="stat-value">${Utils.formatPrice(atl)} <small class="text-gain">(${Utils.formatPercent(atlPct)})</small></span>
            </div>

            <div style="margin-top: var(--sp-4); padding-top: var(--sp-3); border-top: 1px solid var(--border-color);">
              <div class="stat-item">
                <span class="stat-label">7d Change</span>
                <span class="stat-value ${Utils.percentClass(pct7d)}">${Utils.formatPercent(pct7d)}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">30d Change</span>
                <span class="stat-value ${Utils.percentClass(pct30d)}">${Utils.formatPercent(pct30d)}</span>
              </div>
            </div>

            <div style="margin-top: var(--sp-4); padding-top: var(--sp-3); border-top: 1px solid var(--border-color);">
              <div class="stat-item">
                <span class="stat-label"><i class="fab fa-twitter" style="color:#1DA1F2"></i> Twitter</span>
                <span class="stat-value">${twitter ? twitter.toLocaleString() : 'N/A'}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label"><i class="fab fa-reddit" style="color:#ff4500"></i> Reddit</span>
                <span class="stat-value">${redditSubs ? redditSubs.toLocaleString() : 'N/A'}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label"><i class="fab fa-github"></i> Commits (4w)</span>
                <span class="stat-value">${commits}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label"><i class="fas fa-star" style="color:#ffd60a"></i> Stars</span>
                <span class="stat-value">${stars ? stars.toLocaleString() : 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Analysis Panel -->
        <div class="panel ai-analysis-panel" id="ai-analysis-panel">
          <div class="panel-header">
            <h3><i class="fas fa-robot"></i> AI Analysis</h3>
            <span class="tag tag-accent"><i class="fas fa-bolt"></i> Powered by AI</span>
          </div>
          <div class="panel-body" id="ai-analysis-body">
            <div class="empty-state" style="padding: var(--sp-6);">
              <i class="fas fa-spinner spin" style="font-size: var(--fs-xl);"></i>
              <p>Analyzing ${coin.name}...</p>
            </div>
          </div>
        </div>
      </div>
    `;
  },

  async loadChart(coinId, days) {
    if (this._chartType === 'candle') {
      const data = await API.getCoinOHLC(coinId, typeof days === 'string' ? 365 : days);
      if (!data || data.error || !Array.isArray(data)) return;
      const formatted = data.map(([ts, o, h, l, c]) => ({
        time: Math.floor(ts / 1000),
        open: o, high: h, low: l, close: c,
      }));
      Charts.createCandlestickChart('coin-tv-chart', formatted);
    } else {
      const data = await API.getCoinChart(coinId, days);
      if (!data || !data.prices) return;
      const formatted = data.prices.map(([ts, price]) => ({
        time: Math.floor(ts / 1000),
        value: price,
      }));
      Charts.createAreaChart('coin-tv-chart', formatted);
    }
  },

  switchChartType(type, btn) {
    this._chartType = type;
    btn.parentElement.querySelectorAll('.coin-chart-tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    this.loadChart(this._currentCoin, this._chartDays);
  },

  switchChartDays(days, btn) {
    this._chartDays = days;
    btn.parentElement.querySelectorAll('.coin-chart-tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    this.loadChart(this._currentCoin, days);
  },

  async loadAIAnalysis(coinId) {
    const data = await API.getCoinAIAnalysis(coinId);
    const body = document.getElementById('ai-analysis-body');
    if (!data || data.error) {
      body.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>AI analysis unavailable</p></div>';
      return;
    }

    const score = data.score || 50;
    const circumference = 2 * Math.PI * 50;
    const offset = circumference - (score / 100) * circumference;
    const color = data.sentiment_color || Utils.fgColor(score);

    body.innerHTML = `
      <div class="ai-score-container">
        <div class="ai-score-ring">
          <svg viewBox="0 0 120 120">
            <circle class="ring-bg" cx="60" cy="60" r="50" />
            <circle class="ring-fill" cx="60" cy="60" r="50"
              stroke="${color}"
              stroke-dasharray="${circumference}"
              stroke-dashoffset="${offset}" />
          </svg>
          <div class="ai-score-value">
            <span class="ai-score-number" style="color:${color}">${score}</span>
            <span class="ai-score-max">/100</span>
          </div>
        </div>
        <div>
          <div class="ai-sentiment-label" style="color:${color}">${data.sentiment || 'Neutral'}</div>
          <div class="ai-risk-label">Risk: ${data.risk_level || 'Medium'}</div>
          ${data.source === 'openai' ? '<div style="margin-top:4px;"><span class="tag tag-accent"><i class="fas fa-bolt"></i> GPT-4o Analysis</span></div>' : ''}
        </div>
      </div>

      <div class="ai-factors">
        <div class="ai-factors-list">
          <h4 class="text-gain"><i class="fas fa-arrow-up"></i> Bullish Factors</h4>
          ${(data.bullish_factors || []).map(f => `
            <div class="ai-factor-item"><i class="fas fa-check text-gain"></i> ${f}</div>
          `).join('') || '<div class="ai-factor-item text-secondary">No strong bullish signals</div>'}
        </div>
        <div class="ai-factors-list">
          <h4 class="text-loss"><i class="fas fa-arrow-down"></i> Bearish Factors</h4>
          ${(data.bearish_factors || []).map(f => `
            <div class="ai-factor-item"><i class="fas fa-exclamation text-loss"></i> ${f}</div>
          `).join('') || '<div class="ai-factor-item text-secondary">No strong bearish signals</div>'}
        </div>
      </div>

      ${(data.risks || []).length > 0 ? `
        <div style="margin-bottom: var(--sp-4);">
          <h4 style="font-size: var(--fs-sm); color: var(--warning); margin-bottom: var(--sp-2);">
            <i class="fas fa-shield-alt"></i> Risks
          </h4>
          ${data.risks.map(r => `<div class="ai-factor-item"><i class="fas fa-triangle-exclamation" style="color:var(--warning)"></i> ${r}</div>`).join('')}
        </div>
      ` : ''}

      ${data.reddit_sentiment && data.reddit_sentiment.available ? `
        <div style="margin-bottom: var(--sp-4); padding: var(--sp-4); background: var(--bg-tertiary); border-radius: var(--border-radius);">
          <h4 style="font-size: var(--fs-sm); color: var(--neon-purple); margin-bottom: var(--sp-2);">
            <i class="fab fa-reddit"></i> Reddit Sentiment
          </h4>
          <div style="display:flex; gap: var(--sp-6); font-size: var(--fs-sm);">
            <div><span class="text-secondary">Score:</span> <strong>${data.reddit_sentiment.sentiment_score}/100</strong> (${data.reddit_sentiment.sentiment_label})</div>
            <div><span class="text-secondary">Posts:</span> ${data.reddit_sentiment.posts_analyzed}</div>
            <div class="text-gain">↑ ${data.reddit_sentiment.positive_signals}</div>
            <div class="text-loss">↓ ${data.reddit_sentiment.negative_signals}</div>
          </div>
        </div>
      ` : ''}

      <button class="explain-why-btn" onclick="CoinDetail.toggleExplainWhy()">
        <i class="fas fa-lightbulb"></i> Explain Why
      </button>

      <div class="explain-box" id="explain-box" style="display:none;">
        <span class="explain-icon">💡</span>
        <p>${data.explanation || 'No explanation available.'}</p>
      </div>
    `;
  },

  toggleExplainWhy() {
    const box = document.getElementById('explain-box');
    if (box) {
      box.style.display = box.style.display === 'none' ? 'block' : 'none';
    }
  },

  async addToWatchlist(coinId, symbol, name, image) {
    const result = await API.addToWatchlist({ coin_id: coinId, symbol, name, image_url: image });
    if (result) {
      Utils.showToast('Added to Watchlist', `${name} has been added to your watchlist`, 'success');
    }
  },

  addToPortfolio(coinId, symbol, name) {
    Portfolio.showAddModal(coinId, symbol, name);
  },
};
