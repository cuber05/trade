/**
 * CryptoTerminal — Learn/Academy Module
 */

const Learn = {
  articles: [
    {
      id: 'market-cap',
      title: 'Understanding Market Cap',
      desc: 'Why market capitalization matters more than the price per coin.',
      level: 'beginner',
      icon: 'fa-chart-pie',
      content: `
        <h4>What is Market Capitalization?</h4>
        <p>Market Cap = Current Price × Circulating Supply. It represents the total dollar value of all coins currently in existence.</p>
        <div class="tip-box">
          <strong>Pro Tip:</strong> A coin priced at $0.01 with 1 trillion supply has the same market cap as a coin priced at $10 with 1 billion supply. Don't fall for "cheap" coins just because their unit price is low!
        </div>
      `
    },
    {
      id: 'volume',
      title: 'Reading Trading Volume',
      desc: 'How to use volume to confirm price trends and spot fake breakouts.',
      level: 'intermediate',
      icon: 'fa-chart-bar',
      content: `
        <h4>Why Volume Matters</h4>
        <p>Volume measures how much of a cryptocurrency has traded over a set period (usually 24h). High volume indicates strong interest and liquidity.</p>
        <ul>
          <li><strong>Price up + High volume:</strong> Strong bullish trend</li>
          <li><strong>Price up + Low volume:</strong> Weak trend, might reverse</li>
          <li><strong>Price down + High volume:</strong> Strong bearish trend</li>
        </ul>
      `
    },
    {
      id: 'rsi-macd',
      title: 'RSI & MACD Basics',
      desc: 'Two of the most popular technical indicators for spotting momentum.',
      level: 'advanced',
      icon: 'fa-wave-square',
      content: `
        <h4>Relative Strength Index (RSI)</h4>
        <p>RSI measures the speed and change of price movements on a scale of 0 to 100.</p>
        <ul>
          <li><strong>Over 70:</strong> Overbought (potential sell signal)</li>
          <li><strong>Under 30:</strong> Oversold (potential buy signal)</li>
        </ul>
        <div class="tip-box">
          <strong>Caution:</strong> In strong bull markets, assets can stay "overbought" for a very long time.
        </div>
      `
    }
  ],

  init() {
    this.renderGrid();
  },

  renderGrid() {
    const grid = document.getElementById('learn-grid');
    if (!grid) return;

    grid.innerHTML = this.articles.map(article => `
      <div class="learn-card stagger-children" onclick="Learn.openArticle('${article.id}')">
        <i class="fas ${article.icon} learn-card-icon text-neon"></i>
        <div class="learn-card-title">${article.title}</div>
        <div class="learn-card-desc">${article.desc}</div>
        <span class="learn-card-level ${article.level}">${article.level.toUpperCase()}</span>
      </div>
    `).join('');
  },

  openArticle(id) {
    const article = this.articles.find(a => a.id === id);
    if (!article) return;

    Utils.openModal(
      article.title,
      `<div class="learn-detail">${article.content}</div>`,
      `<button class="btn btn-secondary" onclick="Utils.closeModal()">Close</button>`
    );
  }
};
