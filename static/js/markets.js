/**
 * CryptoTerminal — Markets Module
 * Full market table with pagination and category filtering.
 */

const Markets = {
  _page: 1,
  _category: '',

  async init() {
    this.bindEvents();
    await this.loadMarkets();
  },

  bindEvents() {
    // Category tabs
    document.querySelectorAll('#market-categories .category-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('#market-categories .category-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        this._category = tab.dataset.category || '';
        this._page = 1;
        this.loadMarkets();
      });
    });
  },

  async loadMarkets() {
    const data = await API.getCoinsMarkets(this._page, 100, this._category);
    if (!data || data.error) return;

    // Also store for heatmap usage
    if (this._page === 1 && !this._category) {
      Store.set('topCoins', data);
    }

    this.renderTable(data);
    this.renderPagination();
  },

  renderTable(coins) {
    const tbody = document.getElementById('markets-tbody');
    tbody.innerHTML = coins.map(coin => {
      const pct1h = coin.price_change_percentage_1h_in_currency || 0;
      const pct24h = coin.price_change_percentage_24h_in_currency || coin.price_change_percentage_24h || 0;
      const pct7d = coin.price_change_percentage_7d_in_currency || 0;
      const sparkData = coin.sparkline_in_7d?.price || [];
      const sparkColor = pct7d >= 0 ? '#00ff88' : '#ff3b5c';
      const sparkId = `spark_${coin.id}`;

      return `
        <tr onclick="App.navigateToCoin('${coin.id}')">
          <td>${coin.market_cap_rank || '—'}</td>
          <td>
            <div class="coin-cell">
              <img src="${coin.image}" alt="${coin.name}" loading="lazy" />
              <span class="coin-cell-name">${coin.name}</span>
              <span class="coin-cell-symbol">${coin.symbol}</span>
            </div>
          </td>
          <td>${Utils.formatPrice(coin.current_price)}</td>
          <td class="${Utils.percentClass(pct1h)}">${Utils.formatPercent(pct1h)}</td>
          <td class="${Utils.percentClass(pct24h)}">${Utils.formatPercent(pct24h)}</td>
          <td class="${Utils.percentClass(pct7d)}">${Utils.formatPercent(pct7d)}</td>
          <td>${Utils.formatCurrency(coin.market_cap)}</td>
          <td>${Utils.formatCurrency(coin.total_volume)}</td>
          <td>
            <canvas id="${sparkId}" width="120" height="40" class="sparkline-container"
                    data-spark='${JSON.stringify(sparkData.slice(-30))}'
                    data-color="${sparkColor}"></canvas>
          </td>
        </tr>
      `;
    }).join('');

    // Draw sparklines after render
    requestAnimationFrame(() => {
      coins.forEach(coin => {
        const canvas = document.getElementById(`spark_${coin.id}`);
        if (canvas) {
          try {
            const data = JSON.parse(canvas.dataset.spark || '[]');
            Charts.drawSparkline(canvas, data, canvas.dataset.color);
          } catch (e) { /* skip */ }
        }
      });
    });
  },

  renderPagination() {
    const container = document.getElementById('markets-pagination');
    const totalPages = 5; // CoinGecko free tier practical limit
    let html = '';

    for (let i = 1; i <= totalPages; i++) {
      html += `<button class="page-btn ${i === this._page ? 'active' : ''}"
                       onclick="Markets.goToPage(${i})">${i}</button>`;
    }

    container.innerHTML = html;
  },

  goToPage(page) {
    this._page = page;
    this.loadMarkets();
    document.getElementById('content').scrollTo({ top: 0, behavior: 'smooth' });
  },
};
