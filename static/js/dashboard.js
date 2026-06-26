/**
 * CryptoTerminal — Dashboard Module
 * Renders the main dashboard with all panels.
 */

const Dashboard = {
  _btcChartInstance: null,

  async init() {
    await Promise.all([
      this.loadGlobalMetrics(),
      this.loadFearGreed(),
      this.loadTrending(),
      this.loadGainersLosers(),
      this.loadBtcChart(7),
      this.loadHeatmap(),
    ]);

    this.bindEvents();
  },

  bindEvents() {
    // BTC chart range buttons
    document.querySelectorAll('#panel-market-chart .panel-action-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#panel-market-chart .panel-action-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.loadBtcChart(parseInt(btn.dataset.range));
      });
    });

    // Heatmap period buttons
    document.querySelectorAll('#panel-heatmap .panel-action-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#panel-heatmap .panel-action-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.loadHeatmap(btn.dataset.heatmap);
      });
    });
  },

  async loadGlobalMetrics() {
    const data = await API.getGlobalData();
    if (!data || !data.data) return;

    const d = data.data;
    Store.set('globalData', data);

    const strip = document.getElementById('global-metrics-strip');
    const totalMcap = d.total_market_cap?.usd || 0;
    const totalVol = d.total_volume?.usd || 0;
    const mcapChange = d.market_cap_change_percentage_24h_usd || 0;
    const btcDom = d.market_cap_percentage?.btc || 0;
    const ethDom = d.market_cap_percentage?.eth || 0;
    const activeCryptos = d.active_cryptocurrencies || 0;

    strip.innerHTML = `
      <div class="metric-card">
        <div class="metric-card-label"><i class="fas fa-globe"></i> Total Market Cap</div>
        <div class="metric-card-value">${Utils.formatCurrency(totalMcap)}</div>
        <div class="metric-card-change ${Utils.percentClass(mcapChange)}">${Utils.formatPercent(mcapChange)}</div>
      </div>
      <div class="metric-card">
        <div class="metric-card-label"><i class="fas fa-chart-bar"></i> 24h Volume</div>
        <div class="metric-card-value">${Utils.formatCurrency(totalVol)}</div>
      </div>
      <div class="metric-card">
        <div class="metric-card-label"><i class="fab fa-bitcoin"></i> BTC Dominance</div>
        <div class="metric-card-value">${btcDom.toFixed(1)}%</div>
      </div>
      <div class="metric-card">
        <div class="metric-card-label"><i class="fab fa-ethereum"></i> ETH Dominance</div>
        <div class="metric-card-value">${ethDom.toFixed(1)}%</div>
      </div>
      <div class="metric-card">
        <div class="metric-card-label"><i class="fas fa-coins"></i> Active Cryptos</div>
        <div class="metric-card-value">${activeCryptos.toLocaleString()}</div>
      </div>
    `;

    // Topbar ticker
    this.updateTopbarTicker(d);

    // Dominance chart
    const domLabels = [];
    const domData = [];
    const domColors = ['#f7931a', '#627eea', '#00ff88', '#8892b0'];
    let otherDom = 100;

    if (d.market_cap_percentage) {
      const sorted = Object.entries(d.market_cap_percentage)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3);
      sorted.forEach(([key, val]) => {
        domLabels.push(key.toUpperCase());
        domData.push(val);
        otherDom -= val;
      });
      domLabels.push('Others');
      domData.push(Math.max(0, otherDom));
    }

    Charts.createDoughnut('dominance-chart', domLabels, domData, domColors);
  },

  updateTopbarTicker(d) {
    const ticker = document.getElementById('topbar-ticker');
    if (!ticker) return;
    const mcapChange = d.market_cap_change_percentage_24h_usd || 0;
    const btcDom = d.market_cap_percentage?.btc || 0;
    ticker.innerHTML = `
      <span class="ticker-item">
        <span>MCap</span>
        <span class="ticker-price">${Utils.formatCurrency(d.total_market_cap?.usd || 0)}</span>
        <span class="ticker-change ${Utils.percentClass(mcapChange)}">${Utils.formatPercent(mcapChange)}</span>
      </span>
      <span class="ticker-item">
        <span>BTC.D</span>
        <span class="ticker-price">${btcDom.toFixed(1)}%</span>
      </span>
      <span class="ticker-item">
        <span>Vol 24h</span>
        <span class="ticker-price">${Utils.formatCurrency(d.total_volume?.usd || 0)}</span>
      </span>
    `;
  },

  async loadFearGreed() {
    const data = await API.getFearGreed(7);
    if (!data || !data.current) return;

    Store.set('fearGreed', data);
    const value = data.current.value;
    const label = Utils.fgLabel(value);
    const color = Utils.fgColor(value);

    // Gauge
    Charts.drawFearGreedGauge('fg-gauge-canvas', value);

    // Value & label
    const fgValue = document.getElementById('fg-value');
    const fgLabel = document.getElementById('fg-label');
    fgValue.textContent = value;
    fgValue.style.color = color;
    fgLabel.textContent = label;
    fgLabel.style.color = color;

    // Sidebar mini
    document.getElementById('fg-mini-value').textContent = value;
    document.getElementById('fg-mini-value').style.color = color;
    const bar = document.getElementById('fg-mini-bar-fill');
    bar.style.width = value + '%';
    bar.style.background = color;

    // History
    const historyEl = document.getElementById('fg-history');
    if (data.history && data.history.length > 1) {
      const items = data.history.slice(0, 5);
      historyEl.innerHTML = items.map((item, i) => {
        const labels = ['Today', 'Yesterday', '2d ago', '3d ago', '4d ago'];
        const c = Utils.fgColor(item.value);
        return `
          <div class="fg-history-item">
            <div class="fg-history-label">${labels[i] || i + 'd ago'}</div>
            <div class="fg-history-value" style="color:${c}">${item.value}</div>
          </div>
        `;
      }).join('');
    }
  },

  async loadTrending() {
    const data = await API.getTrending();
    if (!data || !data.coins) return;

    const list = document.getElementById('trending-list');
    list.innerHTML = data.coins.slice(0, 7).map((item, i) => {
      const coin = item.item;
      const price = coin.data?.price || '';
      const change = coin.data?.price_change_percentage_24h?.usd || 0;
      return `
        <div class="coin-row" onclick="App.navigateToCoin('${coin.id}')">
          <span class="coin-row-rank">${i + 1}</span>
          <img class="coin-row-icon" src="${coin.small}" alt="${coin.name}" loading="lazy" />
          <div class="coin-row-info">
            <div class="coin-row-name">${coin.name}</div>
            <div class="coin-row-symbol">${coin.symbol}</div>
          </div>
          <span class="coin-row-change ${Utils.percentClass(change)}">${Utils.formatPercent(change)}</span>
        </div>
      `;
    }).join('');
  },

  async loadGainersLosers() {
    const data = await API.getGainersLosers(7);
    if (!data || data.error) return;

    const renderList = (items, containerId) => {
      const container = document.getElementById(containerId);
      container.innerHTML = items.map((coin, i) => {
        const change = coin.price_change_percentage_24h || 0;
        return `
          <div class="coin-row" onclick="App.navigateToCoin('${coin.id}')">
            <span class="coin-row-rank">${i + 1}</span>
            <img class="coin-row-icon" src="${coin.image}" alt="${coin.name}" loading="lazy" />
            <div class="coin-row-info">
              <div class="coin-row-name">${coin.name}</div>
              <div class="coin-row-symbol">${coin.symbol}</div>
            </div>
            <span class="coin-row-price">${Utils.formatPrice(coin.current_price)}</span>
            <span class="coin-row-change ${Utils.percentClass(change)}">${Utils.formatPercent(change)}</span>
          </div>
        `;
      }).join('');
    };

    renderList(data.gainers || [], 'gainers-list');
    renderList(data.losers || [], 'losers-list');
  },

  async loadBtcChart(days = 7) {
    const data = await API.getCoinChart('bitcoin', days);
    if (!data || !data.prices) return;

    const chartData = data.prices.map(([ts, price]) => ({
      time: Math.floor(ts / 1000),
      value: price,
    }));

    Charts.createAreaChart('market-cap-chart-container', chartData);
  },

  async loadHeatmap(field = 'price_change_percentage_24h_in_currency') {
    let coins = Store.get('topCoins');
    if (!coins || coins.length === 0) {
      coins = await API.getCoinsMarkets(1, 50);
      if (coins && !coins.error) Store.set('topCoins', coins);
    }
    if (!coins || coins.error) return;

    const grid = document.getElementById('heatmap-grid');
    const is7d = field.includes('7d');

    grid.innerHTML = coins.slice(0, 40).map(coin => {
      const change = is7d
        ? (coin.price_change_percentage_7d_in_currency || 0)
        : (coin.price_change_percentage_24h_in_currency || coin.price_change_percentage_24h || 0);
      const bgColor = Utils.heatmapColor(change);
      const mcap = coin.market_cap || 0;
      // Size based on market cap rank
      const size = coin.market_cap_rank <= 5 ? 'font-size:14px' : '';
      return `
        <div class="heatmap-cell" style="background:${bgColor};${size}"
             onclick="App.navigateToCoin('${coin.id}')" title="${coin.name}: ${Utils.formatPercent(change)}">
          <span class="heatmap-symbol">${coin.symbol}</span>
          <span class="heatmap-change">${Utils.formatPercent(change)}</span>
        </div>
      `;
    }).join('');
  },

  async loadNews() {
    // CoinGecko doesn't have a news endpoint on free tier
    // Show status updates or placeholder
    const feed = document.getElementById('news-feed');
    feed.innerHTML = `
      <div class="news-item">
        <span class="news-item-time">Now</span>
        <div class="news-item-content">
          <div class="news-item-title">Market data is live — dashboard auto-refreshes every 60 seconds</div>
          <div class="news-item-source">CryptoTerminal</div>
        </div>
        <span class="news-item-sentiment neutral-sent">INFO</span>
      </div>
      <div class="news-item">
        <span class="news-item-time">Tip</span>
        <div class="news-item-content">
          <div class="news-item-title">Click any coin to see the AI Analysis with the "Explain Why" feature</div>
          <div class="news-item-source">CryptoTerminal</div>
        </div>
        <span class="news-item-sentiment bullish">TIP</span>
      </div>
      <div class="news-item">
        <span class="news-item-time">Tip</span>
        <div class="news-item-content">
          <div class="news-item-title">Add API keys in .env for higher rate limits and news feeds</div>
          <div class="news-item-source">CryptoTerminal</div>
        </div>
        <span class="news-item-sentiment neutral-sent">CONFIG</span>
      </div>
    `;
  },
};
