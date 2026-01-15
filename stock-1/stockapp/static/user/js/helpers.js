// Helper utility functions
class Helpers {
    // Format currency values
    // Format currency values (VNĐ, không thập phân)
static formatCurrency(amount, abbreviated = false) {
    if (amount === null || amount === undefined || isNaN(amount)) {
        return 'đ0';
    }

    if (abbreviated && amount >= 1e9) {
        return 'đ' + (amount / 1e9).toFixed(0) + 'B';
    } else if (abbreviated && amount >= 1e6) {
        return 'đ' + (amount / 1e6).toFixed(0) + 'M';
    } else if (abbreviated && amount >= 1e3) {
        return 'đ' + (amount / 1e3).toFixed(0) + 'K';
    }

    // ✅ đổi sang vi-VN, bỏ fractionDigits
    return 'đ' + new Intl.NumberFormat('vi-VN', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}


    // Format large numbers with abbreviations
    static formatNumber(number, abbreviated = true) {
        if (number === null || number === undefined || isNaN(number)) {
            return '0';
        }

        if (abbreviated && number >= 1e9) {
            return (number / 1e9).toFixed(1) + 'B';
        } else if (abbreviated && number >= 1e6) {
            return (number / 1e6).toFixed(1) + 'M';
        } else if (abbreviated && number >= 1e3) {
            return (number / 1e3).toFixed(1) + 'K';
        }

        return new Intl.NumberFormat('en-US').format(number);
    }

    // Format percentage values
    static formatPercentage(decimal, decimalPlaces = 2) {
        if (decimal === null || decimal === undefined || isNaN(decimal)) {
            return '0.00%';
        }

        return (decimal * 100).toFixed(decimalPlaces) + '%';
    }

    // Format date values
    static formatDate(date, format = 'medium') {
        if (!date) return '--';

        const dateObj = date instanceof Date ? date : new Date(date);
        
        if (isNaN(dateObj.getTime())) {
            return '--';
        }

        const options = {
            short: {
                month: 'short',
                day: 'numeric'
            },
            medium: {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            },
            long: {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            },
            time: {
                hour: '2-digit',
                minute: '2-digit'
            },
            datetime: {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            }
        };

        return new Intl.DateTimeFormat('en-US', options[format] || options.medium).format(dateObj);
    }

    // Format relative time (e.g., "2 hours ago")
    static formatRelativeTime(date) {
        if (!date) return '--';

        const dateObj = date instanceof Date ? date : new Date(date);
        const now = new Date();
        const diffInSeconds = Math.floor((now - dateObj) / 1000);

        if (diffInSeconds < 60) {
            return 'Just now';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
        } else if (diffInSeconds < 2592000) {
            const days = Math.floor(diffInSeconds / 86400);
            return `${days} day${days !== 1 ? 's' : ''} ago`;
        } else {
            return this.formatDate(dateObj, 'medium');
        }
    }

    // Calculate percentage change
    static calculatePercentageChange(oldValue, newValue) {
        if (oldValue === 0 || oldValue === null || oldValue === undefined) {
            return 0;
        }
        
        return ((newValue - oldValue) / Math.abs(oldValue)) * 100;
    }

    // Validate email format
    static isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Generate random ID
    static generateId(prefix = 'id') {
        return prefix + '_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    // Debounce function calls
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

    // Throttle function calls
    static throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // Deep clone object
    static deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => this.deepClone(item));
        if (typeof obj === 'object') {
            const clonedObj = {};
            for (const key in obj) {
                if (obj.hasOwnProperty(key)) {
                    clonedObj[key] = this.deepClone(obj[key]);
                }
            }
            return clonedObj;
        }
    }

    // Sanitize HTML to prevent XSS
    static sanitizeHtml(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }

    // Capitalize first letter of each word
    static capitalizeWords(str) {
        if (!str) return '';
        return str.replace(/\w\S*/g, txt => 
            txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
        );
    }

    // Format file size
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Check if element is in viewport
    static isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    // Smooth scroll to element
    static scrollToElement(element, offset = 0) {
        if (!element) return;
        
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - offset;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }

    // Copy text to clipboard
    static async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'absolute';
            textArea.style.left = '-999999px';
            document.body.appendChild(textArea);
            textArea.select();
            
            try {
                const successful = document.execCommand('copy');
                document.body.removeChild(textArea);
                return successful;
            } catch (err) {
                document.body.removeChild(textArea);
                return false;
            
            }
        }
    }

    // Get URL parameters
    static getUrlParams() {
        const params = {};
        const urlSearchParams = new URLSearchParams(window.location.search);
        for (const [key, value] of urlSearchParams) {
            params[key] = value;
        }
        return params;
    }

    // Set URL parameter without page reload
    static setUrlParam(key, value) {
        const url = new URL(window.location);
        url.searchParams.set(key, value);
        window.history.pushState({}, '', url);
    }

    // Remove URL parameter without page reload
    static removeUrlParam(key) {
        const url = new URL(window.location);
        url.searchParams.delete(key);
        window.history.pushState({}, '', url);
    }

    // Format stock change with color class
    static formatStockChange(change, changePercent) {
        const isPositive = change >= 0;
        const symbol = isPositive ? '+' : '';
        const colorClass = isPositive ? 'positive' : 'negative';
        
        return {
            text: `${symbol}${this.formatCurrency(change)} (${symbol}${changePercent.toFixed(2)}%)`,
            class: colorClass,
            isPositive
        };
    }

    // Generate color based on string (for avatars, etc.)
    static stringToColor(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
        }
        
        const hue = hash % 360;
        return `hsl(${hue}, 70%, 50%)`;
    }

    // Check if user prefers dark mode
    static prefersDarkMode() {
        return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    }

    // Local storage helpers with error handling
    static setLocalStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('Error setting localStorage:', error);
            return false;
        }
    }

    static getLocalStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Error getting localStorage:', error);
            return defaultValue;
        }
    }

    static removeLocalStorage(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Error removing localStorage:', error);
            return false;
        }
    }

    // Format market cap with appropriate suffix
    static formatMarketCap(marketCap) {
        if (marketCap >= 1e12) {
            return '$' + (marketCap / 1e12).toFixed(2) + 'T';
        } else if (marketCap >= 1e9) {
            return '$' + (marketCap / 1e9).toFixed(2) + 'B';
        } else if (marketCap >= 1e6) {
            return '$' + (marketCap / 1e6).toFixed(2) + 'M';
        } else {
            return this.formatCurrency(marketCap);
        }
    }

    // Check if device is mobile
    static isMobile() {
        return window.innerWidth <= 768;
    }

    // Check if device is tablet
    static isTablet() {
        return window.innerWidth > 768 && window.innerWidth <= 1024;
    }

    // Check if device is desktop
    static isDesktop() {
        return window.innerWidth > 1024;
    }
} 