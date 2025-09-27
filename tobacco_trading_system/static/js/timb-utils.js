/**
 * TIMB Trading System Utilities
 * Common JavaScript functions for the tobacco trading system
 */
class TIMBUtils {
    
    /**
     * Get CSRF token for Django forms
     */
    static getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
               '';
    }
    
    /**
     * Show notification to user
     */
    static showNotification(message, type = 'info', duration = 5000) {
        // Remove existing notifications
        const existing = document.querySelectorAll('.toast-notification');
        existing.forEach(toast => toast.remove());
        
        // Create new notification
        const toast = document.createElement('div');
        toast.className = `toast-notification toast show position-fixed`;
        toast.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
        `;
        
        const bgClass = {
            'success': 'bg-success',
            'danger': 'bg-danger', 
            'warning': 'bg-warning',
            'info': 'bg-info'
        }[type] || 'bg-info';
        
        const icon = {
            'success': 'check-circle',
            'danger': 'x-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        }[type] || 'info-circle';
        
        toast.innerHTML = `
            <div class="toast-header ${bgClass} text-white">
                <i class="bi bi-${icon} me-2"></i>
                <strong class="me-auto">Notification</strong>
                <button type="button" class="btn-close btn-close-white" onclick="this.closest('.toast-notification').remove()"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, duration);
        }
    }
    
    /**
     * Show confirmation dialog
     */
    static showConfirmDialog(message, onConfirm, onCancel = null) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.style.zIndex = '10000';
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
                        <button type="button" class="btn btn-danger" id="confirmBtn">Confirm</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const bootstrapModal = new bootstrap.Modal(modal);
        
        modal.querySelector('#confirmBtn').addEventListener('click', () => {
            bootstrapModal.hide();
            if (onConfirm) onConfirm();
        });
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
            if (onCancel) onCancel();
        });
        
        bootstrapModal.show();
    }
    
    /**
     * Show loading spinner
     */
    static showLoader(message = 'Loading...') {
        // Remove existing loader
        const existing = document.getElementById('global-loader');
        if (existing) existing.remove();
        
        const loader = document.createElement('div');
        loader.id = 'global-loader';
        loader.className = 'position-fixed w-100 h-100 d-flex align-items-center justify-content-center';
        loader.style.cssText = `
            top: 0;
            left: 0;
            background: rgba(0,0,0,0.5);
            z-index: 99999;
        `;
        
        loader.innerHTML = `
            <div class="bg-white rounded p-4 text-center">
                <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div>${message}</div>
            </div>
        `;
        
        document.body.appendChild(loader);
    }
    
    /**
     * Hide loading spinner
     */
    static hideLoader() {
        const loader = document.getElementById('global-loader');
        if (loader) loader.remove();
    }
    
    /**
     * Format currency
     */
    static formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    }
    
    /**
     * Format weight
     */
    static formatWeight(weight, unit = 'kg') {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(weight) + ' ' + unit;
    }
    
    /**
     * Format date
     */
    static formatDate(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        
        return new Date(date).toLocaleDateString('en-US', { ...defaultOptions, ...options });
    }
    
    /**
     * Time ago helper
     */
    static timeAgo(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diffInSeconds = Math.floor((now - time) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return Math.floor(diffInSeconds / 60) + ' minutes ago';
        if (diffInSeconds < 86400) return Math.floor(diffInSeconds / 3600) + ' hours ago';
        return Math.floor(diffInSeconds / 86400) + ' days ago';
    }
    
    /**
     * Debounce function calls
     */
    static debounce(func, wait, immediate = false) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    }
    
    /**
     * Throttle function calls
     */
    static throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    /**
     * API request helper
     */
    static async apiRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken(),
                ...options.headers
            }
        };
        
        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
    
    /**
     * Download file from blob
     */
    static downloadBlob(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    }
    
    /**
     * Copy text to clipboard
     */
    static async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showNotification('Copied to clipboard', 'success', 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
            this.showNotification('Failed to copy to clipboard', 'danger');
        }
    }
    
    /**
     * Validate form
     */
    static validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    }
    
    /**
     * Auto-resize textarea
     */
    static autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    }
    
    /**
     * Initialize tooltips
     */
    static initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    /**
     * Initialize popovers
     */
    static initializePopovers() {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
}

// Initialize utilities when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    TIMBUtils.initializeTooltips();
    TIMBUtils.initializePopovers();
    
    // Auto-resize textareas
    document.querySelectorAll('textarea[data-auto-resize]').forEach(textarea => {
        textarea.addEventListener('input', () => TIMBUtils.autoResizeTextarea(textarea));
        TIMBUtils.autoResizeTextarea(textarea); // Initial resize
    });
});

// Make TIMBUtils globally available
window.TIMBUtils = TIMBUtils;