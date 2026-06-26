/**
 * CryptoTerminal — Main App Controller
 * Handles SPA routing, global search, and initialization.
 */

const App = {
  async init() {
    this.bindEvents();
    
    // Hide loading screen, show app
    const loadingScreen = document.getElementById('loading-screen');
    const appShell = document.getElementById('app');
    if (loadingScreen) loadingScreen.style.display = 'none';
    if (appShell) appShell.style.display = 'flex';

    // Check path for deep linking
    const path = window.location.pathname;
    if (path.startsWith('/coin/')) {
      const id = path.split('/')[2];
      this.navigateToCoin(id);
    } else {
      this.switchView('dashboard');
    }

    // Refresh data periodically
    setInterval(() => {
      const view = Store.get('currentView');
      if (view === 'dashboard') Dashboard.init();
      if (view === 'markets') Markets.loadMarkets();
      if (view === 'watchlist') Watchlist.loadWatchlist();
      if (view === 'alerts') Alerts.loadAlerts();
    }, 60000); // Every minute
  },

  bindEvents() {
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const view = item.dataset.view;
        if (view) this.switchView(view);
      });
    });

    // Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
      sidebarToggle.addEventListener('click', () => {
        const sidebar = document.getElementById('sidebar');
        if (window.innerWidth <= 768) {
          sidebar.classList.toggle('open');
        } else {
          sidebar.classList.toggle('collapsed');
        }
      });
    }

    // Global Search
    const searchInput = document.getElementById('global-search');
    const searchResults = document.getElementById('search-dropdown');

    searchInput.addEventListener('input', Utils.debounce(async (e) => {
      const query = e.target.value.trim();
      if (query.length < 2) {
        searchResults.classList.remove('active');
        return;
      }
      
      const data = await API.searchCoins(query);
      if (!data || !data.coins || data.coins.length === 0) {
        searchResults.innerHTML = '<div class="search-result-item" style="justify-content:center;color:var(--text-secondary)">No results found</div>';
        searchResults.classList.add('active');
        return;
      }

      searchResults.innerHTML = data.coins.slice(0, 8).map(coin => `
        <div class="search-result-item" onclick="App.navigateToCoin('${coin.id}'); document.getElementById('global-search').value=''; document.getElementById('search-results').classList.remove('active')">
          <img class="search-result-icon" src="${coin.thumb}" alt="${coin.name}" />
          <div class="search-result-info">
            <div class="search-result-name">${coin.name}</div>
            <div class="search-result-symbol">${coin.symbol}</div>
          </div>
          <div class="search-result-rank">#${coin.market_cap_rank || '-'}</div>
        </div>
      `).join('');
      searchResults.classList.add('active');
    }, 300));

    // Close search on click outside
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.search-container')) {
        searchResults.classList.remove('active');
      }
    });

    // Ctrl+K to focus search
    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        searchInput.focus();
      }
    });
  },

  switchView(viewName) {
    Store.set('currentView', viewName);
    
    // Update nav state
    document.querySelectorAll('.nav-item').forEach(item => {
      if (item.dataset.view === viewName) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
        if (item.dataset.view === 'coin-detail') {
            item.style.display = 'none'; // hide coin detail nav unless we're on it
        }
      }
    });

    // Update views
    document.querySelectorAll('.view').forEach(section => {
      if (section.id === `view-${viewName}`) {
        section.classList.add('active');
      } else {
        section.classList.remove('active');
      }
    });

    // Initialize module based on view
    switch(viewName) {
      case 'dashboard': Dashboard.init(); break;
      case 'markets': Markets.init(); break;
      case 'watchlist': Watchlist.init(); break;
      case 'alerts': Alerts.init(); break;
      case 'learn': if(window.Learn) Learn.init(); break;
    }

    // Scroll to top
    document.getElementById('content').scrollTo(0, 0);
  },

  navigateToCoin(coinId) {
    this.switchView('coin-detail');
    CoinDetail.load(coinId);
  }
};

// Boot the app
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
