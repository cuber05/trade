/**
 * CryptoTerminal — Watchlist Module
 */

const Watchlist = {
  async init() {
    await this.loadWatchlist();
  },

  async loadWatchlist() {
    const data = await API.getWatchlist();
    const grid = document.getElementById('watchlist-grid');

    if (!data || data.length === 0) {
      grid.innerHTML = `
        <div class="empty-state" style="grid-column: 1/-1;">
          <i class="fas fa-star"></i>
          <h3>Your watchlist is empty</h3>
          <p>Search for any coin and add it to your watchlist to track it here.</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = data.map(item => {
      const changeClass = Utils.percentClass(item.change_24h);
      return `
        <div class="watchlist-card" onclick="App.navigateToCoin('${item.coin_id}')">
          <div class="watchlist-card-header">
            <div class="watchlist-card-coin">
              <img src="${item.image_url}" alt="${item.name}" />
              <div>
                <div class="watchlist-card-name">${item.name}</div>
                <div class="watchlist-card-symbol">${item.symbol}</div>
              </div>
            </div>
            <button class="watchlist-card-remove" onclick="event.stopPropagation(); Watchlist.remove('${item.coin_id}', '${item.name}')">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="watchlist-card-price">${Utils.formatPrice(item.current_price)}</div>
          <div class="watchlist-card-change ${changeClass}">${Utils.formatPercent(item.change_24h)}</div>
        </div>
      `;
    }).join('');
  },

  async remove(coinId, name) {
    const result = await API.removeFromWatchlist(coinId);
    if (result && result.success) {
      Utils.showToast('Removed', `${name} removed from watchlist`, 'success');
      await this.loadWatchlist();
    }
  },
};
