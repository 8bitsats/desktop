/**
 * Solana Trading Dashboard JavaScript
 * Provides interactive functionality for the trading dashboard
 */

// Sample market data for demonstration
const marketData = {
    "SOL/USDC": {
        price: 215.78,
        change24h: 4.25,
        high24h: 217.90,
        low24h: 207.15,
        volume24h: 1245789.32
    },
    "BONK/USDC": {
        price: 0.00000245,
        change24h: -2.17,
        high24h: 0.00000258,
        low24h: 0.00000241,
        volume24h: 985634.12
    },
    "JTO/USDC": {
        price: 0.92,
        change24h: 1.35,
        high24h: 0.94,
        low24h: 0.90,
        volume24h: 568392.21
    },
    "JUP/USDC": {
        price: 1.73,
        change24h: -0.85,
        high24h: 1.78,
        low24h: 1.71,
        volume24h: 742195.67
    }
};

// Sample portfolio data
const portfolioData = {
    totalValue: 4256.89,
    totalPnL: 142.67,
    pnlPercentage: 3.47,
    holdings: [
        { token: "SOL", amount: 12.5, value: 2697.25, pnl: 98.75 },
        { token: "BONK", amount: 42000000, value: 102.90, pnl: -2.17 },
        { token: "JUP", amount: 215.4, value: 372.64, pnl: 15.42 },
        { token: "JTO", amount: 1125, value: 1035.00, pnl: 30.67 }
    ]
};

// Sample recent trades
const recentTrades = [
    { pair: "SOL/USDC", type: "BUY", price: 210.25, amount: 2.5, time: "10:23:45" },
    { pair: "BONK/USDC", type: "SELL", price: 0.00000251, amount: 5000000, time: "10:12:36" },
    { pair: "JTO/USDC", type: "BUY", price: 0.91, amount: 300, time: "09:58:12" },
    { pair: "JUP/USDC", type: "BUY", price: 1.72, amount: 50.5, time: "09:45:23" }
];

// Sample AI recommendations
const aiRecommendations = [
    { token: "SOL", action: "BUY", price: 215.50, confidence: "HIGH", reason: "Bullish momentum pattern detected, approaching ATH" },
    { token: "BONK", action: "HOLD", price: 0.00000245, confidence: "MEDIUM", reason: "Consolidation phase, awaiting breakout confirmation" },
    { token: "JTO", action: "BUY", price: 0.92, confidence: "MEDIUM", reason: "Strong support at 0.90, uptrend beginning to form" }
];

// Initialize dashboard when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    initMarketData();
    initPortfolio();
    initRecentTrades();
    initAiRecommendations();
    setupEventListeners();
    initializeCharts();
});

// Initialize market data section
function initMarketData() {
    const marketTableBody = document.getElementById('market-data-body');
    if (!marketTableBody) return;
    
    marketTableBody.innerHTML = '';
    
    for (const [pair, data] of Object.entries(marketData)) {
        const row = document.createElement('tr');
        
        const changeClass = data.change24h >= 0 ? 'positive-change' : 'negative-change';
        const changePrefix = data.change24h >= 0 ? '+' : '';
        
        row.innerHTML = `
            <td>${pair}</td>
            <td>${formatPrice(data.price)}</td>
            <td class="${changeClass}">${changePrefix}${data.change24h.toFixed(2)}%</td>
            <td>${formatPrice(data.high24h)}</td>
            <td>${formatPrice(data.low24h)}</td>
            <td>${formatNumber(data.volume24h)}</td>
            <td>
                <button class="btn btn-buy" data-pair="${pair}" data-price="${data.price}">Buy</button>
                <button class="btn btn-sell" data-pair="${pair}" data-price="${data.price}">Sell</button>
            </td>
        `;
        
        marketTableBody.appendChild(row);
    }
}

// Initialize portfolio section
function initPortfolio() {
    const portfolioTableBody = document.getElementById('portfolio-body');
    if (!portfolioTableBody) return;
    
    portfolioTableBody.innerHTML = '';
    
    // Update portfolio summary
    document.getElementById('portfolio-value').innerText = `$${portfolioData.totalValue.toFixed(2)}`;
    
    const pnlElement = document.getElementById('portfolio-pnl');
    if (pnlElement) {
        const isPnlPositive = portfolioData.totalPnL >= 0;
        const pnlClass = isPnlPositive ? 'positive-change' : 'negative-change';
        const pnlPrefix = isPnlPositive ? '+' : '';
        
        pnlElement.className = pnlClass;
        pnlElement.innerText = `${pnlPrefix}$${portfolioData.totalPnL.toFixed(2)} (${pnlPrefix}${portfolioData.pnlPercentage.toFixed(2)}%)`;
    }
    
    // Add portfolio holdings
    portfolioData.holdings.forEach(holding => {
        const row = document.createElement('tr');
        const isPnlPositive = holding.pnl >= 0;
        const pnlClass = isPnlPositive ? 'positive-change' : 'negative-change';
        const pnlPrefix = isPnlPositive ? '+' : '';
        
        row.innerHTML = `
            <td>${holding.token}</td>
            <td>${formatNumber(holding.amount)}</td>
            <td>$${holding.value.toFixed(2)}</td>
            <td class="${pnlClass}">${pnlPrefix}$${holding.pnl.toFixed(2)}</td>
        `;
        
        portfolioTableBody.appendChild(row);
    });
}

// Initialize recent trades section
function initRecentTrades() {
    const tradesTableBody = document.getElementById('recent-trades-body');
    if (!tradesTableBody) return;
    
    tradesTableBody.innerHTML = '';
    
    recentTrades.forEach(trade => {
        const row = document.createElement('tr');
        const tradeTypeClass = trade.type === 'BUY' ? 'trade-buy' : 'trade-sell';
        
        row.innerHTML = `
            <td>${trade.pair}</td>
            <td class="${tradeTypeClass}">${trade.type}</td>
            <td>${formatPrice(trade.price)}</td>
            <td>${formatNumber(trade.amount)}</td>
            <td>${trade.time}</td>
        `;
        
        tradesTableBody.appendChild(row);
    });
}

// Initialize AI recommendations section
function initAiRecommendations() {
    const recommendationsBody = document.getElementById('ai-recommendations-body');
    if (!recommendationsBody) return;
    
    recommendationsBody.innerHTML = '';
    
    aiRecommendations.forEach(rec => {
        const row = document.createElement('tr');
        const actionClass = rec.action === 'BUY' ? 'rec-buy' : rec.action === 'SELL' ? 'rec-sell' : 'rec-hold';
        const confidenceClass = `confidence-${rec.confidence.toLowerCase()}`;
        
        row.innerHTML = `
            <td>${rec.token}</td>
            <td class="${actionClass}">${rec.action}</td>
            <td>${formatPrice(rec.price)}</td>
            <td class="${confidenceClass}">${rec.confidence}</td>
            <td>${rec.reason}</td>
            <td>
                <button class="btn btn-execute" data-token="${rec.token}" data-action="${rec.action}" data-price="${rec.price}">Execute</button>
            </td>
        `;
        
        recommendationsBody.appendChild(row);
    });
}

// Set up event listeners for interactive elements
function setupEventListeners() {
    // Buy buttons
    document.querySelectorAll('.btn-buy').forEach(button => {
        button.addEventListener('click', (e) => {
            const pair = e.target.dataset.pair;
            const price = e.target.dataset.price;
            showTradeModal('BUY', pair, price);
        });
    });
    
    // Sell buttons
    document.querySelectorAll('.btn-sell').forEach(button => {
        button.addEventListener('click', (e) => {
            const pair = e.target.dataset.pair;
            const price = e.target.dataset.price;
            showTradeModal('SELL', pair, price);
        });
    });
    
    // Execute recommendation buttons
    document.querySelectorAll('.btn-execute').forEach(button => {
        button.addEventListener('click', (e) => {
            const token = e.target.dataset.token;
            const action = e.target.dataset.action;
            const price = e.target.dataset.price;
            showTradeModal(action, `${token}/USDC`, price);
        });
    });
}

// Show trade modal for buy/sell orders
function showTradeModal(action, pair, price) {
    const modal = document.getElementById('trade-modal');
    const modalAction = document.getElementById('modal-action');
    const modalPair = document.getElementById('modal-pair');
    const modalPrice = document.getElementById('modal-price');
    const amountInput = document.getElementById('trade-amount');
    const totalDisplay = document.getElementById('trade-total');
    
    if (!modal) return;
    
    // Update modal content
    modalAction.innerText = action;
    modalAction.className = action === 'BUY' ? 'trade-buy' : 'trade-sell';
    modalPair.innerText = pair;
    modalPrice.innerText = formatPrice(price);
    amountInput.value = '';
    totalDisplay.innerText = '$0.00';
    
    // Show modal
    modal.style.display = 'block';
    
    // Calculate total when amount changes
    amountInput.addEventListener('input', () => {
        const amount = parseFloat(amountInput.value) || 0;
        const total = amount * parseFloat(price);
        totalDisplay.innerText = `$${total.toFixed(2)}`;
    });
    
    // Handle confirm button
    const confirmButton = document.getElementById('confirm-trade');
    if (confirmButton) {
        confirmButton.onclick = () => {
            const amount = parseFloat(amountInput.value);
            if (amount <= 0) {
                alert('Please enter a valid amount');
                return;
            }
            
            // Execute trade (simulation)
            executeTrade(action, pair, parseFloat(price), amount);
            modal.style.display = 'none';
        };
    }
    
    // Close modal on X click
    const closeButton = modal.querySelector('.close');
    if (closeButton) {
        closeButton.onclick = () => {
            modal.style.display = 'none';
        };
    }
    
    // Close modal when clicking outside
    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };
}

// Execute a trade (simulation)
function executeTrade(action, pair, price, amount) {
    // In a real implementation, this would connect to a trading API
    console.log(`Executing ${action} order for ${amount} ${pair} at ${price}`);
    
    // Add to recent trades
    const now = new Date();
    const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
    
    recentTrades.unshift({
        pair: pair,
        type: action,
        price: price,
        amount: amount,
        time: timeString
    });
    
    // Only keep the most recent trades
    if (recentTrades.length > 5) {
        recentTrades.pop();
    }
    
    // Update UI
    initRecentTrades();
    
    // Show success notification
    showNotification(`${action} order executed: ${amount} ${pair} at ${formatPrice(price)}`, 'success');
}

// Show notification
function showNotification(message, type = 'info') {
    const notifications = document.getElementById('notifications');
    if (!notifications) return;
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerText = message;
    
    notifications.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notifications.removeChild(notification);
        }, 500);
    }, 5000);
}

// Initialize charts
function initializeCharts() {
    // This would be replaced with a proper charting library like Chart.js
    const chartPlaceholder = document.getElementById('price-chart');
    if (chartPlaceholder) {
        chartPlaceholder.innerHTML = '<div class="chart-placeholder">Interactive price chart will be displayed here</div>';
    }
}

// Helper function to format price values
function formatPrice(price) {
    if (price < 0.0001) {
        return price.toFixed(8);
    } else if (price < 0.01) {
        return price.toFixed(6);
    } else if (price < 1) {
        return price.toFixed(4);
    } else {
        return price.toFixed(2);
    }
}

// Helper function to format numbers with commas
function formatNumber(num) {
    if (num >= 1000000) {
        return `${(num / 1000000).toFixed(2)}M`;
    } else if (num >= 1000) {
        return `${(num / 1000).toFixed(2)}K`;
    } else {
        return num.toString();
    }
}
