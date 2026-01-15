// Main application logic and navigation
class Main {
    constructor() {
        this.init();
    }

    init() {
        this.setupNavigation();
        this.checkAuthentication();
        this.initializePage();
    }

    setupNavigation() {
        // Mobile menu toggle
        const navToggle = document.getElementById('nav-toggle');
        const navMenu = document.getElementById('nav-menu');

        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                navMenu.classList.toggle('active');
                navToggle.classList.toggle('active');
            });

            // Close menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                    navMenu.classList.remove('active');
                    navToggle.classList.remove('active');
                }
            });

            // Close menu when clicking on nav links
            const navLinks = navMenu.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                link.addEventListener('click', () => {
                    navMenu.classList.remove('active');
                    navToggle.classList.remove('active');
                });
            });
        }

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const href = this.getAttribute('href');
                if (href && href.startsWith('#')) {
                    e.preventDefault();
                    const target = document.querySelector(href);
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }
            });
        });
    }

    checkAuthentication() {
    const loginBtn = document.getElementById('login-btn');
    const registerBtn = document.getElementById('register-btn');
    const logoutBtn = document.getElementById('logout-btn');

    Auth.getCurrentUser().then(currentUser => {
        if (currentUser) {
            if (loginBtn) loginBtn.style.display = 'none';
            if (registerBtn) registerBtn.style.display = 'none';
        } else {
            if (loginBtn) loginBtn.style.display = 'inline-flex';
            if (registerBtn) registerBtn.style.display = 'inline-flex';
        }
    }).catch(err => {
        console.error('Auth error:', err);
    });
}


    async initializePage() {
        const path = window.location.pathname;
        const page = path.split('/').pop() || 'index.html';

        switch (page) {
            case 'index.html':
            case '':
                await this.initializeHomepage();
                break;
            default:
                // Page-specific initialization is handled in each HTML file
                break;
        }
    }

    async initializeHomepage() {
        try {
            // Load featured stocks
            const stocks = await API.getStocks();
            const featuredStocks = stocks.slice(0, 6); // Show first 6 stocks
            this.displayFeaturedStocks(featuredStocks);
        } catch (error) {
            console.error('Error loading homepage data:', error);
        }
    }

    displayFeaturedStocks(stocks) {
        const container = document.getElementById('featured-stocks');
        if (!container) return;

        container.innerHTML = '';

        stocks.forEach(stock => {
            const stockCard = this.createStockCard(stock);
            container.appendChild(stockCard);
        });
    }

    
    async addToWatchlist(symbol) {
    const user = await Auth.getCurrentUser();
    
    if (!user) {
        // 🔹 dùng toast thay confirm
        this.showToast("You need to log in to add stocks to your watchlist", "warning");
        return;
    }

    try {
        const token = localStorage.getItem('token');
        const res = await fetch('/api/watchlist/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ symbol })
        });

        const data = await res.json();
        if (data.success) {
            this.showToast(`${symbol} added to your watchlist!`, 'success');
        } else {
            this.showToast(data.error || 'Failed to add stock', 'error');
        }
    } catch (err) {
        console.error(err);
        this.showToast('Error connecting to server', 'error');
    }
}


    showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        // Style the toast
        toast.style.position = 'fixed';
        toast.style.top = '20px';
        toast.style.right = '20px';
        toast.style.padding = 'var(--space-3) var(--space-4)';
        toast.style.borderRadius = 'var(--radius-md)';
        toast.style.boxShadow = 'var(--shadow-lg)';
        toast.style.zIndex = '10000';
        toast.style.fontSize = '0.875rem';
        toast.style.fontWeight = 'var(--font-weight-medium)';
        toast.style.maxWidth = '300px';
        toast.style.wordWrap = 'break-word';
        
        // Set colors based on type
        switch (type) {
            case 'success':
                toast.style.backgroundColor = 'var(--success-600)';
                toast.style.color = 'white';
                break;
            case 'error':
                toast.style.backgroundColor = 'var(--error-600)';
                toast.style.color = 'white';
                break;
            case 'warning':
                toast.style.backgroundColor = 'var(--warning-600)';
                toast.style.color = 'white';
                break;
            default:
                toast.style.backgroundColor = 'var(--primary-600)';
                toast.style.color = 'white';
        }
        
        // Add to document
        document.body.appendChild(toast);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 3000);
    }

    // Utility method to get URL parameters
    getUrlParameter(name) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name);
    }

    // Utility method to set page title
    setPageTitle(title) {
        document.title = `${title} - StockHub`;
    }

    // Method to handle errors
    handleError(error, userMessage = 'An error occurred. Please try again.') {
        console.error('Error:', error);
        this.showToast(userMessage, 'error');
    }
}

// Initialize the main application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mainApp = new Main();
    
    // Make addToWatchlist globally accessible for onclick handlers
    window.addToWatchlist = (symbol) => {
        window.mainApp.addToWatchlist(symbol);
    };
});

// Handle page visibility change
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        // Page became visible, refresh auth state
        if (window.mainApp) {
            window.mainApp.checkAuthentication();
        }
    }
});

// Handle online/offline status
window.addEventListener('online', () => {
    if (window.mainApp) {
        window.mainApp.showToast('Connection restored', 'success');
    }
});

window.addEventListener('offline', () => {
    if (window.mainApp) {
        window.mainApp.showToast('No internet connection', 'warning');
    }
});

// Export Main class for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Main;
}