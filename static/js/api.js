/**
 * CryptoTerminal — API Client
 * All backend API calls go through here.
 */

const API = {
  BASE: '/api/v1',

  async _fetch(endpoint, options = {}) {
    try {
      const url = `${this.BASE}${endpoint}`;
      const resp = await fetch(url, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
      });
      if (!resp.ok) {
        console.error(`API error ${resp.status}: ${endpoint}`);
        return null;
      }
      return await resp.json();
    } catch (err) {
      console.error(`API request failed: ${endpoint}`, err);
      return null;
    }
  },

  // ── Market ──
  async getGlobalData() {
    return this._fetch('/market/global');
  },

  async getFearGreed(limit = 30) {
    return this._fetch(`/market/fear-greed?limit=${limit}`);
  },

  async getTrending() {
    return this._fetch('/market/trending');
  },

  async getCoinsMarkets(page = 1, perPage = 100, category = '') {
    let url = `/market/coins?page=${page}&per_page=${perPage}&sparkline=true`;
    if (category) url += `&category=${category}`;
    return this._fetch(url);
  },

  async getGainersLosers(limit = 10) {
    return this._fetch(`/market/gainers-losers?limit=${limit}`);
  },

  async searchCoins(query) {
    return this._fetch(`/market/search?q=${encodeURIComponent(query)}`);
  },

  // ── Coins ──
  async getCoinDetail(coinId) {
    return this._fetch(`/coins/${coinId}`);
  },

  async getCoinChart(coinId, days = 7) {
    return this._fetch(`/coins/${coinId}/chart?days=${days}`);
  },

  async getCoinOHLC(coinId, days = 7) {
    return this._fetch(`/coins/${coinId}/ohlc?days=${days}`);
  },

  async getCoinAIAnalysis(coinId) {
    return this._fetch(`/coins/${coinId}/ai-analysis`);
  },

  // ── Portfolio ──
  async getPortfolio() {
    return this._fetch('/portfolio');
  },

  async addHolding(data) {
    return this._fetch('/portfolio', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateHolding(id, data) {
    return this._fetch(`/portfolio/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async deleteHolding(id) {
    return this._fetch(`/portfolio/${id}`, { method: 'DELETE' });
  },

  // ── Watchlist ──
  async getWatchlist() {
    return this._fetch('/watchlist');
  },

  async addToWatchlist(data) {
    return this._fetch('/watchlist', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async removeFromWatchlist(coinId) {
    return this._fetch(`/watchlist/${coinId}`, { method: 'DELETE' });
  },

  // ── Alerts ──
  async getAlerts(activeOnly = false) {
    return this._fetch(`/alerts?active_only=${activeOnly}`);
  },

  async createAlert(data) {
    return this._fetch('/alerts', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async deleteAlert(id) {
    return this._fetch(`/alerts/${id}`, { method: 'DELETE' });
  },

  async toggleAlert(id) {
    return this._fetch(`/alerts/${id}/toggle`, { method: 'PUT' });
  },

  async getAlertHistory() {
    return this._fetch('/alerts/history');
  },
};
