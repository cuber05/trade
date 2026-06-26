/**
 * CryptoTerminal — Alerts Module
 */

const Alerts = {
  async init() {
    this.bindEvents();
    await this.loadAlerts();
  },

  bindEvents() {
    document.getElementById('btn-create-alert')?.addEventListener('click', () => {
      this.showCreateModal();
    });
  },

  async loadAlerts() {
    const alerts = await API.getAlerts();
    const container = document.getElementById('alerts-active');

    if (!alerts || alerts.length === 0) {
      container.innerHTML = `
        <div class="empty-state" style="grid-column: 1/-1;">
          <i class="fas fa-bell"></i>
          <h3>No alerts set</h3>
          <p>Create price, volume, or market sentiment alerts to stay informed.</p>
          <button class="btn btn-primary" onclick="Alerts.showCreateModal()">
            <i class="fas fa-plus"></i> Create Alert
          </button>
        </div>
      `;
      return;
    }

    container.innerHTML = alerts.map(alert => {
      const isActive = alert.is_active;
      const typeIcons = {
        price_above: 'fa-arrow-up',
        price_below: 'fa-arrow-down',
        volume_spike: 'fa-chart-bar',
        pct_change: 'fa-percent',
        fear_greed: 'fa-heartbeat',
      };
      const icon = typeIcons[alert.alert_type] || 'fa-bell';
      const conditionText = this.formatCondition(alert);

      return `
        <div class="alert-card ${isActive ? '' : 'inactive'}">
          <div class="alert-card-header">
            <div class="alert-card-coin">
              <i class="alert-icon fas ${icon}"></i>
              <span>${alert.name} (${alert.symbol.toUpperCase()})</span>
            </div>
            <div class="alert-card-actions">
              <button class="btn btn-icon btn-sm btn-secondary" onclick="Alerts.toggle(${alert.id})" title="${isActive ? 'Disable' : 'Enable'}">
                <i class="fas ${isActive ? 'fa-pause' : 'fa-play'}"></i>
              </button>
              <button class="btn btn-icon btn-sm btn-danger" onclick="Alerts.deleteAlert(${alert.id})" title="Delete">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
          <div class="alert-card-condition">
            <i class="fas fa-bell"></i>
            ${conditionText}
          </div>
        </div>
      `;
    }).join('');

    // Load history
    this.loadHistory();
  },

  formatCondition(alert) {
    const threshold = alert.threshold;
    switch (alert.alert_type) {
      case 'price_above':
        return `Notify when price goes above ${Utils.formatPrice(threshold)}`;
      case 'price_below':
        return `Notify when price drops below ${Utils.formatPrice(threshold)}`;
      case 'volume_spike':
        return `Notify when 24h volume increases by ${threshold}%`;
      case 'pct_change':
        return `Notify when price changes by ${threshold}%`;
      case 'fear_greed':
        return `Notify when Fear & Greed ${alert.condition === 'below' ? 'drops below' : 'rises above'} ${threshold}`;
      default:
        return `${alert.condition} ${threshold}`;
    }
  },

  async loadHistory() {
    const history = await API.getAlertHistory();
    const container = document.getElementById('alerts-history-list');
    if (!history || history.length === 0) {
      container.innerHTML = '<p class="text-secondary" style="font-size:var(--fs-sm); padding: var(--sp-3);">No alerts triggered yet.</p>';
      return;
    }

    container.innerHTML = history.map(h => `
      <div class="alert-history-item">
        <div class="alert-history-icon"><i class="fas fa-bell"></i></div>
        <div class="alert-history-content">
          <div class="alert-history-message">${h.message}</div>
          <div class="alert-history-time">${Utils.timeAgo(h.triggered_at)}</div>
        </div>
      </div>
    `).join('');
  },

  showCreateModal() {
    Utils.openModal('Create Alert', `
      <div class="alert-form">
        <div class="form-group coin-search-in-modal">
          <label class="form-label">Coin</label>
          <input type="text" class="form-input" id="alert-coin-search"
                 placeholder="Search for a coin..." oninput="Alerts.searchCoin(this.value)" autocomplete="off" />
          <input type="hidden" id="alert-coin-id" />
          <input type="hidden" id="alert-coin-symbol" />
          <input type="hidden" id="alert-coin-name" />
          <div class="coin-search-results" id="alert-search-results"></div>
        </div>
        <div class="form-group">
          <label class="form-label">Alert Type</label>
          <select class="form-select" id="alert-type">
            <option value="price_above">Price goes above</option>
            <option value="price_below">Price drops below</option>
            <option value="pct_change">Price changes by %</option>
            <option value="volume_spike">Volume spike %</option>
            <option value="fear_greed">Fear & Greed Index</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Threshold</label>
          <input type="number" class="form-input" id="alert-threshold"
                 placeholder="e.g. 0.001 or 200" step="any" />
        </div>
      </div>
    `, `
      <button class="btn btn-secondary" onclick="Utils.closeModal()">Cancel</button>
      <button class="btn btn-primary" onclick="Alerts.submitAlert()">Create Alert</button>
    `);
  },

  async searchCoin(query) {
    const results = document.getElementById('alert-search-results');
    if (!query || query.length < 2) { results.classList.remove('active'); return; }
    const data = await API.searchCoins(query);
    if (!data || !data.coins) return;
    results.innerHTML = data.coins.slice(0, 6).map(coin => `
      <div class="coin-search-result-item" onclick="Alerts.selectCoin('${coin.id}', '${coin.symbol}', '${coin.name}')">
        <img src="${coin.thumb}" alt="${coin.name}" />
        <span>${coin.name}</span>
        <span style="color:var(--text-tertiary); font-family:var(--font-mono); text-transform:uppercase; font-size:11px;">${coin.symbol}</span>
      </div>
    `).join('');
    results.classList.add('active');
  },

  selectCoin(id, symbol, name) {
    document.getElementById('alert-coin-id').value = id;
    document.getElementById('alert-coin-symbol').value = symbol;
    document.getElementById('alert-coin-name').value = name;
    document.getElementById('alert-coin-search').value = name;
    document.getElementById('alert-search-results').classList.remove('active');
  },

  async submitAlert() {
    const coinId = document.getElementById('alert-coin-id').value;
    const symbol = document.getElementById('alert-coin-symbol').value;
    const name = document.getElementById('alert-coin-name').value;
    const alertType = document.getElementById('alert-type').value;
    const threshold = parseFloat(document.getElementById('alert-threshold').value);

    if (!coinId || !threshold) {
      Utils.showToast('Error', 'Please fill in all fields', 'error');
      return;
    }

    const condition = alertType.includes('above') ? 'above' : 'below';
    const result = await API.createAlert({
      coin_id: coinId, symbol, name, alert_type: alertType,
      condition, threshold,
    });

    if (result && !result.error) {
      Utils.closeModal();
      Utils.showToast('Alert Created', `Alert for ${name} created`, 'success');
      await this.loadAlerts();
    }
  },

  async toggle(id) {
    await API.toggleAlert(id);
    await this.loadAlerts();
  },

  async deleteAlert(id) {
    if (!confirm('Delete this alert?')) return;
    await API.deleteAlert(id);
    Utils.showToast('Deleted', 'Alert removed', 'success');
    await this.loadAlerts();
  },
};
