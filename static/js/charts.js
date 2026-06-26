/**
 * CryptoTerminal — Chart Helpers
 * TradingView Lightweight Charts + Chart.js wrappers.
 */

const Charts = {
  _instances: {},

  /**
   * Create a TradingView area chart.
   */
  createAreaChart(containerId, data, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) return null;

    // Clean up existing chart
    if (this._instances[containerId]) {
      this._instances[containerId].remove();
      container.innerHTML = '';
    }

    const chart = LightweightCharts.createChart(container, {
      layout: {
        background: { type: 'solid', color: 'transparent' },
        textColor: '#8892b0',
        fontSize: 11,
        fontFamily: "'Inter', sans-serif",
      },
      grid: {
        vertLines: { color: 'rgba(136, 146, 176, 0.06)' },
        horzLines: { color: 'rgba(136, 146, 176, 0.06)' },
      },
      crosshair: {
        vertLine: { color: 'rgba(0, 255, 136, 0.3)', width: 1, style: 2 },
        horzLine: { color: 'rgba(0, 255, 136, 0.3)', width: 1, style: 2 },
      },
      rightPriceScale: {
        borderColor: 'rgba(136, 146, 176, 0.1)',
      },
      timeScale: {
        borderColor: 'rgba(136, 146, 176, 0.1)',
        timeVisible: true,
        secondsVisible: false,
      },
      handleScroll: { vertTouchDrag: false },
      ...options,
    });

    const series = chart.addAreaSeries({
      topColor: 'rgba(0, 255, 136, 0.25)',
      bottomColor: 'rgba(0, 255, 136, 0.01)',
      lineColor: '#00ff88',
      lineWidth: 2,
      crosshairMarkerVisible: true,
      crosshairMarkerRadius: 4,
      crosshairMarkerBorderColor: '#00ff88',
      crosshairMarkerBackgroundColor: '#0a0e17',
    });

    if (data && data.length > 0) {
      series.setData(data);
      chart.timeScale().fitContent();
    }

    this._instances[containerId] = chart;

    // Auto-resize
    const observer = new ResizeObserver(() => {
      chart.applyOptions({
        width: container.clientWidth,
        height: container.clientHeight,
      });
    });
    observer.observe(container);

    return { chart, series };
  },

  /**
   * Create a TradingView candlestick chart.
   */
  createCandlestickChart(containerId, data, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) return null;

    if (this._instances[containerId]) {
      this._instances[containerId].remove();
      container.innerHTML = '';
    }

    const chart = LightweightCharts.createChart(container, {
      layout: {
        background: { type: 'solid', color: 'transparent' },
        textColor: '#8892b0',
        fontSize: 11,
        fontFamily: "'Inter', sans-serif",
      },
      grid: {
        vertLines: { color: 'rgba(136, 146, 176, 0.06)' },
        horzLines: { color: 'rgba(136, 146, 176, 0.06)' },
      },
      crosshair: {
        vertLine: { color: 'rgba(0, 255, 136, 0.3)', width: 1, style: 2 },
        horzLine: { color: 'rgba(0, 255, 136, 0.3)', width: 1, style: 2 },
      },
      rightPriceScale: { borderColor: 'rgba(136, 146, 176, 0.1)' },
      timeScale: {
        borderColor: 'rgba(136, 146, 176, 0.1)',
        timeVisible: true,
      },
      ...options,
    });

    const series = chart.addCandlestickSeries({
      upColor: '#00ff88',
      downColor: '#ff3b5c',
      borderUpColor: '#00ff88',
      borderDownColor: '#ff3b5c',
      wickUpColor: '#00ff88',
      wickDownColor: '#ff3b5c',
    });

    if (data && data.length > 0) {
      series.setData(data);
      chart.timeScale().fitContent();
    }

    // Volume
    const volumeSeries = chart.addHistogramSeries({
      priceFormat: { type: 'volume' },
      priceScaleId: '',
    });
    volumeSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    this._instances[containerId] = chart;

    const observer = new ResizeObserver(() => {
      chart.applyOptions({
        width: container.clientWidth,
        height: container.clientHeight,
      });
    });
    observer.observe(container);

    return { chart, series, volumeSeries };
  },

  /**
   * Create a Chart.js doughnut chart (for dominance, allocation).
   */
  createDoughnut(canvasId, labels, data, colors) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    if (this._instances[canvasId]) {
      this._instances[canvasId].destroy();
    }

    const ctx = canvas.getContext('2d');
    const chart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: colors || [
            '#00ff88', '#00d4ff', '#a855f7', '#ff9500',
            '#ff3b8b', '#ffd60a', '#06d6a0', '#8892b0',
          ],
          borderColor: '#0a0e17',
          borderWidth: 2,
          hoverBorderWidth: 3,
          hoverBorderColor: '#1a2340',
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        cutout: '65%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: '#8892b0',
              font: { family: "'Inter', sans-serif", size: 11 },
              padding: 12,
              usePointStyle: true,
              pointStyleWidth: 8,
            },
          },
          tooltip: {
            backgroundColor: '#1a2340',
            titleColor: '#e6f1ff',
            bodyColor: '#8892b0',
            borderColor: 'rgba(136, 146, 176, 0.2)',
            borderWidth: 1,
            cornerRadius: 8,
            padding: 10,
            callbacks: {
              label: (ctx) => ` ${ctx.label}: ${ctx.parsed.toFixed(1)}%`,
            },
          },
        },
      },
    });

    this._instances[canvasId] = chart;
    return chart;
  },

  /**
   * Draw Fear & Greed gauge on canvas.
   */
  drawFearGreedGauge(canvasId, value) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const centerX = width / 2;
    const centerY = height - 10;
    const radius = Math.min(width, height) - 30;

    ctx.clearRect(0, 0, width, height);

    // Gauge background arc
    const startAngle = Math.PI;
    const endAngle = 2 * Math.PI;

    // Gradient segments
    const segments = [
      { start: 0, end: 0.2, color: '#ff3b5c' },
      { start: 0.2, end: 0.4, color: '#ff9500' },
      { start: 0.4, end: 0.6, color: '#ffd60a' },
      { start: 0.6, end: 0.8, color: '#00cc6a' },
      { start: 0.8, end: 1.0, color: '#00ff88' },
    ];

    segments.forEach(seg => {
      const sAngle = startAngle + (endAngle - startAngle) * seg.start;
      const eAngle = startAngle + (endAngle - startAngle) * seg.end;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, sAngle, eAngle);
      ctx.strokeStyle = seg.color;
      ctx.lineWidth = 12;
      ctx.lineCap = 'round';
      ctx.globalAlpha = 0.25;
      ctx.stroke();
    });

    // Active arc
    ctx.globalAlpha = 1;
    const valueAngle = startAngle + (endAngle - startAngle) * (value / 100);
    const color = Utils.fgColor(value);

    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, startAngle, valueAngle);
    ctx.strokeStyle = color;
    ctx.lineWidth = 12;
    ctx.lineCap = 'round';
    ctx.shadowColor = color;
    ctx.shadowBlur = 15;
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Needle dot
    const needleX = centerX + radius * Math.cos(valueAngle);
    const needleY = centerY + radius * Math.sin(valueAngle);
    ctx.beginPath();
    ctx.arc(needleX, needleY, 6, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.shadowColor = color;
    ctx.shadowBlur = 12;
    ctx.fill();
    ctx.shadowBlur = 0;
  },

  /**
   * Draw a mini sparkline on a canvas.
   */
  drawSparkline(canvas, data, color = '#00ff88') {
    if (!canvas || !data || data.length < 2) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;

    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    ctx.lineJoin = 'round';

    data.forEach((val, i) => {
      const x = (i / (data.length - 1)) * w;
      const y = h - ((val - min) / range) * (h - 4) - 2;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
  },
};
