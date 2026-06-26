/**
 * CryptoTerminal — Portfolio Module
 * Holdings management, P&L tracking, allocation chart.
 */

const Portfolio = {
  async init() {
    this.bindEvents();
    await this.loadPortfolio();
  },

  bindEvents() {
    document.getElementById('btn-add-holding')?.addEventListener('click', () => {
      this.showAddModal();
    });
  },

  async loadPortfolio() {
    const data = await API.getPortfolio();
    if (!data) return;

    this.renderSummary(data);
    this.renderHoldings(data.holdings || []);
    this.renderAllocationChart(data.holdings || []);
  },

  renderSummary(data) {
    const container = document.getElementById('portfolio-summary');
    const pnlClass = data.total_pnl >= 0 ? 'text-gain' : 'text-loss';

    container.innerHTML = `
      <div class="portfolio-stat">
        <div class="portfolio-stat-label">Total Value</div>
        <div class="portfolio-stat-value">${Utils.formatCurrency(data.total_value)}</div>
      </div>
      <div class="portfolio-stat">
        <div class="portfolio-stat-label">Total Invested</div>
        <div class="portfolio-stat-value">${Utils.formatCurrency(data.total_invested)}</div>
      </div>
      <div class="portfolio-stat">
        <div class="portfolio-stat-label">Total P&L</div>
        <div class="portfolio-stat-value ${pnlClass}">
          ${Utils.formatCurrency(data.total_pnl)}
          <small>(${Utils.formatPercent(data.total_pnl_pct)})</small>
        </div>
      </div>
      <div class="portfolio-stat">
        <div class="portfolio-stat-label">Holdings</div>
        <div class="portfolio-stat-value">${(data.holdings || []).length}</div>
      </div>
    `;
  },

  renderHoldings(holdings) {
    const container = document.getElementById('portfolio-holdings');

    if (holdings.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-wallet"></i>
          <h3>No holdings yet</h3>
          <p>Add your first cryptocurrency holding to start tracking your portfolio.</p>
          <button class="btn btn-primary" onclick="Portfolio.showAddModal()">
            <i class="fas fa-plus"></i> Add Holding
          </button>
        </div>
      `;
      return;
    }

    container.innerHTML = `
      <div class="holding-row holding-row-header">
        <div>Coin</div>
        <div>Amount</div>
        <div>Avg Buy</div>
        <div>Current</div>
        <div>P&L</div>
        <div></div>
      </div>
      ${holdings.map(h => {
        const pnlClass = h.pnl >= 0 ? 'text-gain' : 'text-loss';
        return `
          <div class="holding-row">
            <div class="holding-coin" onclick="App.navigateToCoin('${h.coin_id}')" style="cursor:pointer">
              <div>
                <div class="holding-coin-name">${h.name}</div>
                <div class="holding-coin-symbol">${h.symbol}</div>
              </div>
            </div>
            <div class="holding-value">${h.amount}</div>
            <div class="holding-value">${Utils.formatPrice(h.buy_price)}</div>
            <div class="holding-value">${Utils.formatPrice(h.current_price)}</div>
            <div class="holding-pnl ${pnlClass}">
              ${Utils.formatCurrency(h.pnl)}<br>
              <small>${Utils.formatPercent(h.pnl_pct)}</small>
            </div>
            <div class="holding-actions">
              <button class="btn btn-icon btn-sm btn-danger" onclick="Portfolio.deleteHolding(${h.id})" title="Delete">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
        `;
      }).join('')}
    `;
  },

  renderAllocationChart(holdings) {
    if (holdings.length === 0) {
      document.getElementById('portfolio-chart-container').style.display = 'none';
      return;
    }
    document.getElementById('portfolio-chart-container').style.display = 'block';

    const labels = holdings.map(h => h.symbol.toUpperCase());
    const data = holdings.map(h => h.current_value || 0);
    const total = data.reduce((a, b) => a + b, 0);
    const percentages = data.map(v => total > 0 ? (v / total) * 100 : 0);

    Charts.createDoughnut('portfolio-allocation-chart', labels, percentages);
  },

  showAddModal(coinId = '', symbol = '', name = '') {
    Utils.openModal('Add Holding', `
      <div class="add-holding-form">
        <div class="form-group coin-search-in-modal">
          <label class="form-label">Coin</label>
          <input type="text" class="form-input" id="holding-coin-search"
                 placeholder="Search for a coin..." value="${name}"
                 oninput="Portfolio.searchCoin(this.value)" autocomplete="off" />
          <input type="hidden" id="holding-coin-id" value="${coinId}" />
          <input type="hidden" id="holding-coin-symbol" value="${symbol}" />
          <input type="hidden" id="holding-coin-name" value="${name}" />
          <div class="coin-search-results" id="holding-search-results"></div>
        </div>
        <div class="form-group">
          <label class="form-label">Amount</label>
          <input type="number" class="form-input" id="holding-amount"
                 placeholder="e.g. 1000" step="any" min="0" />
        </div>
        <div class="form-group">
          <label class="form-label">Buy Price (USD)</label>
          <input type="number" class="form-input" id="holding-buy-price"
                 placeholder="e.g. 0.00001234" step="any" min="0" />
        </div>
        <div class="form-group">
          <label class="form-label">Date (optional)</label>
          <input type="date" class="form-input" id="holding-buy-date" />
        </div>
      </div>
    `, `
      <button class="btn btn-secondary" onclick="Utils.closeModal()">Cancel</button>
      <button class="btn btn-primary" onclick="Portfolio.submitHolding()">Add Holding</button>
    `);
  },

  async searchCoin(query) {
    const results = document.getElementById('holding-search-results');
    if (!query || query.length < 2) {
      results.classList.remove('active');
      return;
    }

    const data = await API.searchCoins(query);
    if (!data || !data.coins) return;

    results.innerHTML = data.coins.slice(0, 8).map(coin => `
      <div class="coin-search-result-item" onclick="Portfolio.selectCoin('${coin.id}', '${coin.symbol}', '${coin.name}', '${coin.thumb}')">
        <img src="${coin.thumb}" alt="${coin.name}" />
        <span>${coin.name}</span>
        <span style="color:var(--text-tertiary); font-family:var(--font-mono); text-transform:uppercase; font-size:11px;">${coin.symbol}</span>
      </div>
    `).join('');
    results.classList.add('active');
  },

  selectCoin(id, symbol, name, thumb) {
    document.getElementById('holding-coin-id').value = id;
    document.getElementById('holding-coin-symbol').value = symbol;
    document.getElementById('holding-coin-name').value = name;
    document.getElementById('holding-coin-search').value = name;
    document.getElementById('holding-search-results').classList.remove('active');
  },

  async submitHolding() {
    const coinId = document.getElementById('holding-coin-id').value;
    const symbol = document.getElementById('holding-coin-symbol').value;
    const name = document.getElementById('holding-coin-name').value;
    const amount = parseFloat(document.getElementById('holding-amount').value);
    const buyPrice = parseFloat(document.getElementById('holding-buy-price').value);
    const buyDate = document.getElementById('holding-buy-date').value;

    if (!coinId || !amount || !buyPrice) {
      Utils.showToast('Error', 'Please fill in coin, amount, and buy price', 'error');
      return;
    }

    const result = await API.addHolding({
      coin_id: coinId,
      symbol: symbol,
      name: name,
      amount: amount,
      buy_price: buyPrice,
      buy_date: buyDate || new Date().toISOString().split('T')[0],
    });

    if (result && !result.error) {
      Utils.closeModal();
      Utils.showToast('Holding Added', `${name} added to your portfolio`, 'success');
      await this.loadPortfolio();
    } else {
      Utils.showToast('Error', 'Failed to add holding', 'error');
    }
  },

  async deleteHolding(id) {
    if (!confirm('Remove this holding from your portfolio?')) return;
    const result = await API.deleteHolding(id);
    if (result && result.success) {
      Utils.showToast('Removed', 'Holding removed from portfolio', 'success');
      await this.loadPortfolio();
    }
  },
};
