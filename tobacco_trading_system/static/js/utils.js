// Utility functions for TIMB Trading System

// Global utilities object
window.TIMBUtils = {
    // Formatting functions
    formatCurrency: function(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-ZW', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    },

    formatWeight: function(weight, unit = 'kg') {
        return new Intl.NumberFormat('en-ZW', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(weight) + ' ' + unit;
    },

    formatNumber: function(number, decimals = 0) {
        return new Intl.NumberFormat('en-ZW', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(number);
    },

    formatPercentage: function(value, decimals = 1) {
        return new Intl.NumberFormat('en-ZW', {
            style: 'percent',
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(value / 100);
    },

    // Date and time functions
    formatDate: function(date, format = 'short') {
        const options = {
            short: { year: 'numeric', month: 'short', day: 'numeric' },
            long: { year: 'numeric', month: 'long', day: 'numeric' },
            time: { hour: '2-digit', minute: '2-digit' },
            datetime: { 
                year: 'numeric', month: 'short', day: 'numeric',
                hour: '2-digit', minute: '2-digit' 
            }
        };
        
        return new Intl.DateTimeFormat('en-ZW', options[format]).format(new Date(date));
    },

    timeAgo: function(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diffInSeconds = Math.floor((now - time) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return Math.floor(diffInSeconds / 60) + ' minutes ago';
        if (diffInSeconds < 86400) return Math.floor(diffInSeconds / 3600) + ' hours ago';
        if (diffInSeconds < 2592000) return Math.floor(diffInSeconds / 86400) + ' days ago';
        
        return this.formatDate(timestamp);
    },

    // API utilities
    getCsrfToken: function() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }
        return null;
    },

    makeApiRequest: function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            }
        };

        const finalOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        return fetch(url, finalOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            });
    },

    // UI utilities
    showLoader: function(target = 'body') {
        const loader = document.createElement('div');
        loader.className = 'loading-overlay';
        loader.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading...</p>
            </div>
        `;
        loader.id = 'loading-overlay';
        
        if (target === 'body') {
            document.body.appendChild(loader);
        } else {
            const targetElement = document.querySelector(target);
            if (targetElement) {
                targetElement.style.position = 'relative';
                targetElement.appendChild(loader);
            }
        }
    },

    hideLoader: function() {
        const loader = document.getElementById('loading-overlay');
        if (loader) {
            loader.remove();
        }
    },

    showNotification: function(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-dismiss
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
    },

    showConfirmDialog: function(message, onConfirm, onCancel = null) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Confirm Action</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="confirmBtn">Confirm</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        modal.querySelector('#confirmBtn').addEventListener('click', () => {
            bsModal.hide();
            if (onConfirm) onConfirm();
        });
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
            if (onCancel) onCancel();
        });
    },

    // Chart utilities
    getChartColors: function(theme = 'timb') {
        const colors = {
            timb: {
                primary: '#2E7D32',
                secondary: '#4CAF50',
                accent: '#FFC107',
                success: '#4CAF50',
                warning: '#FF9800',
                danger: '#F44336',
                info: '#2196F3'
            },
            merchant: {
                primary: '#1976D2',
                secondary: '#2196F3',
                accent: '#FF9800',
                success: '#4CAF50',
                warning: '#FF9800',
                danger: '#F44336',
                info: '#2196F3'
            }
        };
        
        return colors[theme] || colors.timb;
    },

    createGradient: function(ctx, color1, color2) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, color1);
        gradient.addColorStop(1, color2);
        return gradient;
    },

    // Data processing utilities
    groupBy: function(array, key) {
        return array.reduce((groups, item) => {
            const group = item[key];
            if (!groups[group]) {
                groups[group] = [];
            }
            groups[group].push(item);
            return groups;
        }, {});
    },

    sumBy: function(array, key) {
        return array.reduce((sum, item) => sum + (parseFloat(item[key]) || 0), 0);
    },

    averageBy: function(array, key) {
        if (array.length === 0) return 0;
        return this.sumBy(array, key) / array.length;
    },

    // Validation utilities
    validateEmail: function(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    },

    validatePhone: function(phone) {
        const regex = /^[\+]?[1-9][\d]{0,15}$/;
        return regex.test(phone.replace(/\s/g, ''));
    },

    validateRequired: function(value) {
        return value !== null && value !== undefined && value.toString().trim() !== '';
    },

    // Local storage utilities
    setItem: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.warn('localStorage not available:', e);
            return false;
        }
    },

    getItem: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.warn('Error reading from localStorage:', e);
            return defaultValue;
        }
    },

    removeItem: function(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (e) {
            console.warn('Error removing from localStorage:', e);
            return false;
        }
    },

    // Theme utilities
    setTheme: function(theme) {
        document.body.className = document.body.className.replace(/\b\w+-theme\b/g, '');
        if (theme !== 'timb') {
            document.body.classList.add(`${theme}-theme`);
        }
        this.setItem('theme', theme);
    },

    getTheme: function() {
        return this.getItem('theme', 'timb');
    },

    // Debounce utility
    debounce: function(func, wait, immediate = false) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func.apply(this, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(this, args);
        };
    },

    // Throttle utility
    throttle: function(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// Initialize utilities
document.addEventListener('DOMContentLoaded', function() {
    // Set saved theme
    const savedTheme = TIMBUtils.getTheme();
    TIMBUtils.setTheme(savedTheme);
    
    // Add global error handler
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        // Optionally show user-friendly error message
    });
    
    // Add global promise rejection handler
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        // Optionally show user-friendly error message
    });
});