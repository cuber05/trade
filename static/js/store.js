/**
 * CryptoTerminal — Client-Side Store
 * Lightweight reactive state management.
 */

const Store = {
  _state: {
    currentView: 'dashboard',
    currentCoinId: null,
    globalData: null,
    fearGreed: null,
    trendingCoins: [],
    topCoins: [],
    marketPage: 1,
    marketCategory: '',
    sidebarCollapsed: false,
  },

  _listeners: {},

  get(key) {
    return this._state[key];
  },

  set(key, value) {
    this._state[key] = value;
    this._notify(key, value);
  },

  on(key, callback) {
    if (!this._listeners[key]) this._listeners[key] = [];
    this._listeners[key].push(callback);
  },

  off(key, callback) {
    if (!this._listeners[key]) return;
    this._listeners[key] = this._listeners[key].filter(cb => cb !== callback);
  },

  _notify(key, value) {
    if (this._listeners[key]) {
      this._listeners[key].forEach(cb => cb(value));
    }
  },
};
