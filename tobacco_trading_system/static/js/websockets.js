// WebSocket manager for real-time data in TIMB Trading System

class TIMBWebSocket {
    constructor() {
        this.connections = new Map();
        this.reconnectAttempts = new Map();
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.heartbeatInterval = 30000;
        this.heartbeatTimers = new Map();
        this.messageHandlers = new Map();
        
        // Connection status indicators
        this.statusIndicators = new Set();
        
        this.init();
    }

    init() {
        // Set up global error handlers
        this.setupErrorHandlers();
        
        // Create status indicator
        this.createStatusIndicator();
        
        // Start main connections
        this.connectToRealtimeData();
        
        // If user is a merchant, connect to merchant-specific data
        if (this.isMerchant()) {
            this.connectToMerchantData();
        }
    }

    setupErrorHandlers() {
        window.addEventListener('beforeunload', () => {
            // Clean up connections before page unload
            this.connections.forEach((ws, name) => {
                this.disconnect(name);
            });
        });

        // Handle visibility change (tab switching)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                // Page is hidden, reduce activity
                this.pauseHeartbeats();
            } else {
                // Page is visible, resume activity
                this.resumeHeartbeats();
            }
        });
    }

    createStatusIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'websocket-status';
        indicator.className = 'websocket-status';
        indicator.innerHTML = `
            <div class="status-dot" title="Connection Status"></div>
            <span class="status-text">Connecting...</span>
        `;
        
        // Add CSS if not already present
        if (!document.getElementById('websocket-status-css')) {
            const style = document.createElement('style');
            style.id = 'websocket-status-css';
            style.textContent = `
                .websocket-status {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 9999;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    background: rgba(255, 255, 255, 0.95);
                    padding: 8px 12px;
                    border-radius: 20px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    font-size: 12px;
                    font-weight: 500;
                    backdrop-filter: blur(10px);
                    transition: all 0.3s ease;
                }
                .websocket-status.connected .status-dot {
                    background: #4CAF50;
                    animation: pulse 2s infinite;
                }
                .websocket-status.connecting .status-dot {
                    background: #FF9800;
                    animation: blink 1s infinite;
                }
                .websocket-status.disconnected .status-dot {
                    background: #F44336;
                }
                .status-dot {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: #ccc;
                }
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.5; }
                    100% { opacity: 1; }
                }
                @keyframes blink {
                    0%, 50% { opacity: 1; }
                    51%, 100% { opacity: 0.3; }
                }
                .websocket-status.hidden {
                    transform: translateX(100%);
                    opacity: 0;
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(indicator);
        this.statusIndicator = indicator;
        
        // Hide after initial connection
        setTimeout(() => {
            if (this.statusIndicator) {
                this.statusIndicator.classList.add('hidden');
            }
        }, 10000);
    }

    updateStatus(status, message) {
        if (!this.statusIndicator) return;
        
        this.statusIndicator.className = `websocket-status ${status}`;
        this.statusIndicator.querySelector('.status-text').textContent = message;
        
        // Show indicator temporarily for status changes
        this.statusIndicator.classList.remove('hidden');
        
        if (status === 'connected') {
            setTimeout(() => {
                this.statusIndicator?.classList.add('hidden');
            }, 3000);
        }
    }

    isMerchant() {
        return document.body.classList.contains('merchant-theme') || 
               window.location.pathname.includes('/merchant/');
    }

    connectToRealtimeData() {
        const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
        const wsPath = `${wsScheme}://${window.location.host}/ws/realtime/`;
        
        this.connect('realtime', wsPath, {
            onMessage: this.handleRealtimeMessage.bind(this),
            onConnect: () => {
                console.log('Connected to real-time data feed');
                this.updateStatus('connected', 'Live Data Connected');
            },
            onDisconnect: () => {
                console.log('Disconnected from real-time data feed');
                this.updateStatus('disconnected', 'Connection Lost');
            },
            onError: (error) => {
                console.error('Real-time WebSocket error:', error);
                this.updateStatus('disconnected', 'Connection Error');
            }
        });
    }

    connectToMerchantData() {
        const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
        const wsPath = `${wsScheme}://${window.location.host}/ws/merchant/`;
        
        this.connect('merchant', wsPath, {
            onMessage: this.handleMerchantMessage.bind(this),
            onConnect: () => {
                console.log('Connected to merchant data feed');
            },
            onDisconnect: () => {
                console.log('Disconnected from merchant data feed');
            }
        });
    }

    connect(name, url, handlers = {}) {
        if (this.connections.has(name)) {
            this.disconnect(name);
        }

        this.updateStatus('connecting', 'Connecting...');

        try {
            const ws = new WebSocket(url);
            
            ws.onopen = () => {
                console.log(`WebSocket ${name} connected`);
                this.reconnectAttempts.set(name, 0);
                this.startHeartbeat(name);
                
                if (handlers.onConnect) {
                    handlers.onConnect();
                }
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    
                    // Handle heartbeat responses
                    if (data.type === 'pong') {
                        return;
                    }
                    
                    if (handlers.onMessage) {
                        handlers.onMessage(data);
                    }
                    
                    // Emit global event for other components
                    this.emitEvent(name, data);
                    
                } catch (error) {
                    console.error(`Error parsing WebSocket message from ${name}:`, error);
                }
            };

            ws.onclose = (event) => {
                console.log(`WebSocket ${name} closed:`, event.code, event.reason);
                this.stopHeartbeat(name);
                
                if (handlers.onDisconnect) {
                    handlers.onDisconnect(event);
                }
                
                // Attempt to reconnect unless explicitly closed
                if (event.code !== 1000) {
                    this.scheduleReconnect(name, url, handlers);
                }
            };

            ws.onerror = (error) => {
                console.error(`WebSocket ${name} error:`, error);
                
                if (handlers.onError) {
                    handlers.onError(error);
                }
            };

            this.connections.set(name, ws);
            this.messageHandlers.set(name, handlers);
            
        } catch (error) {
            console.error(`Failed to create WebSocket ${name}:`, error);
            this.updateStatus('disconnected', 'Connection Failed');
            
            if (handlers.onError) {
                handlers.onError(error);
            }
        }
    }

    disconnect(name) {
        const ws = this.connections.get(name);
        if (ws) {
            this.stopHeartbeat(name);
            ws.close(1000, 'Intentional disconnect');
            this.connections.delete(name);
            this.messageHandlers.delete(name);
            this.reconnectAttempts.delete(name);
        }
    }

    scheduleReconnect(name, url, handlers) {
        const attempts = this.reconnectAttempts.get(name) || 0;
        
        if (attempts >= this.maxReconnectAttempts) {
            console.log(`Max reconnection attempts reached for ${name}`);
            this.updateStatus('disconnected', 'Connection Failed');
            return;
        }

        const delay = this.reconnectDelay * Math.pow(2, attempts); // Exponential backoff
        console.log(`Reconnecting to ${name} in ${delay}ms (attempt ${attempts + 1})`);
        
        this.updateStatus('connecting', `Reconnecting... (${attempts + 1}/${this.maxReconnectAttempts})`);
        
        setTimeout(() => {
            this.reconnectAttempts.set(name, attempts + 1);
            this.connect(name, url, handlers);
        }, delay);
    }

    startHeartbeat(name) {
        const ws = this.connections.get(name);
        if (!ws) return;

        const timer = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'ping' }));
            } else {
                this.stopHeartbeat(name);
            }
        }, this.heartbeatInterval);

        this.heartbeatTimers.set(name, timer);
    }

    stopHeartbeat(name) {
        const timer = this.heartbeatTimers.get(name);
        if (timer) {
            clearInterval(timer);
            this.heartbeatTimers.delete(name);
        }
    }

    pauseHeartbeats() {
        this.heartbeatTimers.forEach((timer, name) => {
            clearInterval(timer);
        });
        this.heartbeatTimers.clear();
    }

    resumeHeartbeats() {
        this.connections.forEach((ws, name) => {
            if (ws.readyState === WebSocket.OPEN) {
                this.startHeartbeat(name);
            }
        });
    }

    send(name, data) {
        const ws = this.connections.get(name);
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(data));
            return true;
        }
        return false;
    }

    emitEvent(source, data) {
        const event = new CustomEvent('websocket-message', {
            detail: { source, data }
        });
        document.dispatchEvent(event);
    }

    // Message handlers
    handleRealtimeMessage(data) {
        switch (data.type) {
            case 'price_update':
                this.handlePriceUpdate(data.payload);
                break;
            case 'transaction':
                this.handleTransaction(data.payload);
                break;
            case 'fraud_alert':
                this.handleFraudAlert(data.payload);
                break;
            case 'yield_prediction':
                this.handleYieldPrediction(data.payload);
                break;
            case 'market_alert':
                this.handleMarketAlert(data.payload);
                break;
            default:
                console.log('Unhandled real-time message type:', data.type);
        }
    }

    handleMerchantMessage(data) {
        switch (data.type) {
            case 'inventory_update':
                this.handleInventoryUpdate(data.payload);
                break;
            case 'order_update':
                this.handleOrderUpdate(data.payload);
                break;
            case 'recommendation':
                this.handleRecommendation(data.payload);
                break;
            case 'risk_alert':
                this.handleRiskAlert(data.payload);
                break;
            default:
                console.log('Unhandled merchant message type:', data.type);
        }
    }

    // Specific update handlers
    handlePriceUpdate(data) {
        // Update price displays
        if (window.updatePriceData) {
            window.updatePriceData(data);
        }
        
        // Update charts if available
        if (window.TIMBCharts && window.priceChart) {
            // Add new data point to price chart
            const chart = window.priceChart;
            if (chart.data.labels) {
                chart.data.labels.push(new Date().toLocaleTimeString());
                chart.data.datasets[0].data.push(data.current_price);
                
                // Keep only last 20 data points
                if (chart.data.labels.length > 20) {
                    chart.data.labels.shift();
                    chart.data.datasets[0].data.shift();
                }
                
                chart.update('none');
            }
        }
        
        console.log('Price update:', data);
    }

    handleTransaction(data) {
        // Add to real-time feed
        if (window.addTransactionToFeed) {
            window.addTransactionToFeed(data);
        }
        
        // Update statistics
        this.updateTransactionStats(data);
        
        console.log('New transaction:', data);
    }

    handleFraudAlert(data) {
        // Show alert notification
        if (window.TIMBUtils) {
            window.TIMBUtils.showNotification(
                `Fraud Alert: ${data.title}`,
                'danger',
                10000
            );
        }
        
        // Update fraud dashboard if visible
        if (window.showFraudAlert) {
            window.showFraudAlert(data);
        }
        
        console.log('Fraud alert:', data);
    }

    handleYieldPrediction(data) {
        if (window.updateYieldPrediction) {
            window.updateYieldPrediction(data);
        }
        
        console.log('Yield prediction update:', data);
    }

    handleMarketAlert(data) {
        if (window.TIMBUtils) {
            const alertType = data.severity === 'HIGH' ? 'danger' : 
                            data.severity === 'MEDIUM' ? 'warning' : 'info';
            
            window.TIMBUtils.showNotification(
                `Market Alert: ${data.message}`,
                alertType,
                8000
            );
        }
        
        console.log('Market alert:', data);
    }

    handleInventoryUpdate(data) {
        // Update inventory displays
        if (window.updateInventoryDisplay) {
            window.updateInventoryDisplay(data);
        }
        
        console.log('Inventory update:', data);
    }

    handleOrderUpdate(data) {
        // Update order status displays
        if (window.updateOrderStatus) {
            window.updateOrderStatus(data);
        }
        
        console.log('Order update:', data);
    }

    handleRecommendation(data) {
        // Show new recommendation notification
        if (window.TIMBUtils) {
            window.TIMBUtils.showNotification(
                `New AI Recommendation: ${data.title}`,
                'info',
                5000
            );
        }
        
        // Update recommendations display
        if (window.addNewRecommendation) {
            window.addNewRecommendation(data);
        }
        
        console.log('New recommendation:', data);
    }

    handleRiskAlert(data) {
        if (window.TIMBUtils) {
            window.TIMBUtils.showNotification(
                `Risk Alert: ${data.message}`,
                'warning',
                7000
            );
        }
        
        console.log('Risk alert:', data);
    }

    updateTransactionStats(data) {
        // Update various statistics displays
        const elements = {
            totalTransactions: document.querySelector('[data-stat="total-transactions"]'),
            totalVolume: document.querySelector('[data-stat="total-volume"]'),
            totalValue: document.querySelector('[data-stat="total-value"]')
        };
        
        if (elements.totalTransactions) {
            const current = parseInt(elements.totalTransactions.textContent) || 0;
            elements.totalTransactions.textContent = current + 1;
        }
        
        if (elements.totalVolume && data.quantity) {
            const current = parseFloat(elements.totalVolume.textContent.replace(/[^\d.]/g, '')) || 0;
            elements.totalVolume.textContent = (current + data.quantity).toLocaleString() + 'kg';
        }
        
        if (elements.totalValue && data.total_amount) {
            const current = parseFloat(elements.totalValue.textContent.replace(/[^\d.]/g, '')) || 0;
            elements.totalValue.textContent = '$' + (current + data.total_amount).toLocaleString();
        }
    }

    // Subscription management
    subscribe(eventType, callback) {
        document.addEventListener('websocket-message', (event) => {
            const { source, data } = event.detail;
            if (data.type === eventType) {
                callback(data.payload, source);
            }
        });
    }

    // Connection status
    isConnected(name) {
        const ws = this.connections.get(name);
        return ws && ws.readyState === WebSocket.OPEN;
    }

    getConnectionStatus() {
        const status = {};
        this.connections.forEach((ws, name) => {
            status[name] = {
                readyState: ws.readyState,
                url: ws.url,
                connected: ws.readyState === WebSocket.OPEN
            };
        });
        return status;
    }
}

// Global WebSocket manager instance
window.TIMBWebSocket = new TIMBWebSocket();

// Global function for components to use
window.subscribeToWebSocket = function(eventType, callback) {
    window.TIMBWebSocket.subscribe(eventType, callback);
};

// Debug function (development only)
window.debugWebSocket = function() {
    return window.TIMBWebSocket.getConnectionStatus();
};

console.log('TIMB WebSocket manager initialized');