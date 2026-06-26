/**
 * CryptoTerminal — Utility Functions
 * Formatting, helpers, and shared logic.
 */

const Utils = {
  /**
   * Format a number as currency (USD).
   */
  formatCurrency(value, decimals = 2) {
    if (value == null || isNaN(value)) return '$0.00';
    if (Math.abs(value) >= 1e12) return '$' + (value / 1e12).toFixed(2) + 'T';
    if (Math.abs(value) >= 1e9) return '$' + (value / 1e9).toFixed(2) + 'B';
    if (Math.abs(value) >= 1e6) return '$' + (value / 1e6).toFixed(2) + 'M';
    if (Math.abs(value) >= 1e3) return '$' + (value / 1e3).toFixed(2) + 'K';
    if (Math.abs(value) < 0.01 && value !== 0) {
      return '$' + value.toFixed(6);
    }
    return '$' + value.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  },

  /**
   * Format price with smart decimal places.
   */
  formatPrice(value) {
    if (value == null || isNaN(value)) return '$0.00';
    if (value >= 1000) return Utils.formatCurrency(value, 2);
    if (value >= 1) return Utils.formatCurrency(value, 2);
    if (value >= 0.01) return '$' + value.toFixed(4);
    if (value >= 0.0001) return '$' + value.toFixed(6);
    return '$' + value.toFixed(8);
  },

  /**
   * Format percentage with color class.
   */
  formatPercent(value, includeSign = true) {
    if (value == null || isNaN(value)) return '0.00%';
    const sign = value >= 0 ? '+' : '';
    return (includeSign ? sign : '') + value.toFixed(2) + '%';
  },

  /**
   * Get CSS class for a percentage value.
   */
  percentClass(value) {
    if (value > 0) return 'text-gain';
    if (value < 0) return 'text-loss';
    return 'text-neutral';
  },

  /**
   * Format large number with abbreviation.
   */
  formatNumber(value) {
    if (value == null || isNaN(value)) return '0';
    if (value >= 1e12) return (value / 1e12).toFixed(2) + 'T';
    if (value >= 1e9) return (value / 1e9).toFixed(2) + 'B';
    if (value >= 1e6) return (value / 1e6).toFixed(2) + 'M';
    if (value >= 1e3) return (value / 1e3).toFixed(2) + 'K';
    return value.toLocaleString('en-US');
  },

  /**
   * Format supply (e.g. "19.7M BTC").
   */
  formatSupply(value, symbol = '') {
    if (!value) return 'N/A';
    const formatted = Utils.formatNumber(value);
    return symbol ? `${formatted} ${symbol.toUpperCase()}` : formatted;
  },

  /**
   * Relative time (e.g. "2h ago", "3d ago").
   */
  timeAgo(timestamp) {
    const now = Date.now();
    let ts = timestamp;
    if (typeof timestamp === 'string') ts = new Date(timestamp).getTime();
    if (ts < 1e12) ts *= 1000; // Unix seconds → ms

    const diff = now - ts;
    const mins = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 30) return `${days}d ago`;
    return new Date(ts).toLocaleDateString();
  },

  /**
   * Debounce function calls.
   */
  debounce(fn, delay = 300) {
    let timer;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  },

  /**
   * Create DOM element with attributes.
   */
  createElement(tag, attrs = {}, children = []) {
    const el = document.createElement(tag);
    for (const [key, value] of Object.entries(attrs)) {
      if (key === 'className') el.className = value;
      else if (key === 'innerHTML') el.innerHTML = value;
      else if (key === 'textContent') el.textContent = value;
      else if (key.startsWith('on')) el.addEventListener(key.slice(2).toLowerCase(), value);
      else el.setAttribute(key, value);
    }
    children.forEach(child => {
      if (typeof child === 'string') el.appendChild(document.createTextNode(child));
      else if (child) el.appendChild(child);
    });
    return el;
  },

  /**
   * Show a toast notification.
   */
  showToast(title, message, type = 'info', duration = 4000) {
    const container = document.getElementById('toast-container');
    const icons = {
      success: 'fas fa-check-circle',
      error: 'fas fa-exclamation-circle',
      warning: 'fas fa-exclamation-triangle',
      info: 'fas fa-info-circle',
    };

    const toast = Utils.createElement('div', { className: 'toast' }, [
      Utils.createElement('i', { className: `toast-icon ${type} ${icons[type] || icons.info}` }),
      Utils.createElement('div', { className: 'toast-content' }, [
        Utils.createElement('div', { className: 'toast-title', textContent: title }),
        Utils.createElement('div', { className: 'toast-message', textContent: message }),
      ]),
      Utils.createElement('button', {
        className: 'toast-close',
        innerHTML: '<i class="fas fa-times"></i>',
        onClick: () => removeToast(toast),
      }),
    ]);

    container.appendChild(toast);

    function removeToast(el) {
      el.classList.add('removing');
      setTimeout(() => el.remove(), 300);
    }

    setTimeout(() => removeToast(toast), duration);
  },

  /**
   * Heatmap color based on percentage change.
   */
  heatmapColor(pct) {
    if (pct == null) return 'rgba(136, 146, 176, 0.1)';
    const clamped = Math.max(-15, Math.min(15, pct));
    if (clamped >= 0) {
      const intensity = Math.min(clamped / 15, 1);
      const r = Math.round(0 + (0 - 0) * intensity);
      const g = Math.round(40 + (200 - 40) * intensity);
      const b = Math.round(20 + (100 - 20) * intensity);
      return `rgba(${r}, ${g}, ${b}, ${0.4 + intensity * 0.5})`;
    } else {
      const intensity = Math.min(Math.abs(clamped) / 15, 1);
      const r = Math.round(40 + (200 - 40) * intensity);
      const g = Math.round(20 + (30 - 20) * intensity);
      const b = Math.round(30 + (50 - 30) * intensity);
      return `rgba(${r}, ${g}, ${b}, ${0.4 + intensity * 0.5})`;
    }
  },

  /**
   * Open/close modal.
   */
  openModal(title, bodyHTML, footerHTML = '') {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = bodyHTML;
    document.getElementById('modal-footer').innerHTML = footerHTML;
    document.getElementById('modal-overlay').classList.add('active');
  },

  closeModal() {
    document.getElementById('modal-overlay').classList.remove('active');
  },

  /**
   * Fear & Greed color.
   */
  fgColor(value) {
    if (value <= 20) return '#ff3b5c';
    if (value <= 40) return '#ff9500';
    if (value <= 60) return '#ffd60a';
    if (value <= 80) return '#00cc6a';
    return '#00ff88';
  },

  /**
   * Fear & Greed label.
   */
  fgLabel(value) {
    if (value <= 20) return 'Extreme Fear';
    if (value <= 40) return 'Fear';
    if (value <= 60) return 'Neutral';
    if (value <= 80) return 'Greed';
    return 'Extreme Greed';
  },
};
