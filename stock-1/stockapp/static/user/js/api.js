// API module for data fetching and management
class API {
    static async getStocks() {
        try {
            // Simulate API delay
            await this.delay(500);
            
            const stocks = [
                {
                    symbol: 'AAPL',
                    name: 'Apple Inc.',
                    price: 182.52,
                    change: 2.43,
                    changePercent: 1.35,
                    volume: 45632100,
                    marketCap: 2890000000000,
                    sector: 'technology',
                    market: 'NASDAQ',
                    peRatio: 29.8,
                    high52w: 198.23,
                    low52w: 142.56,
                    dividendYield: 0.52
                },
                {
                    symbol: 'GOOGL',
                    name: 'Alphabet Inc.',
                    price: 141.80,
                    change: -1.25,
                    changePercent: -0.87,
                    volume: 28456200,
                    marketCap: 1780000000000,
                    sector: 'technology',
                    market: 'NASDAQ',
                    peRatio: 25.4,
                    high52w: 151.55,
                    low52w: 101.88,
                    dividendYield: null
                },
                {
                    symbol: 'MSFT',
                    name: 'Microsoft Corporation',
                    price: 378.85,
                    change: 4.12,
                    changePercent: 1.10,
                    volume: 22145800,
                    marketCap: 2810000000000,
                    sector: 'technology',
                    market: 'NASDAQ',
                    peRatio: 32.1,
                    high52w: 384.30,
                    low52w: 309.45,
                    dividendYield: 0.68
                },
                {
                    symbol: 'TSLA',
                    name: 'Tesla Inc.',
                    price: 248.42,
                    change: -8.16,
                    changePercent: -3.18,
                    volume: 78425600,
                    marketCap: 789000000000,
                    sector: 'consumer',
                    market: 'NASDAQ',
                    peRatio: 62.3,
                    high52w: 299.29,
                    low52w: 138.80,
                    dividendYield: null
                },
                {
                    symbol: 'AMZN',
                    name: 'Amazon.com Inc.',
                    price: 153.75,
                    change: 1.89,
                    changePercent: 1.24,
                    volume: 32156700,
                    marketCap: 1590000000000,
                    sector: 'consumer',
                    market: 'NASDAQ',
                    peRatio: 45.2,
                    high52w: 170.15,
                    low52w: 118.35,
                    dividendYield: null
                },
                {
                    symbol: 'JPM',
                    name: 'JPMorgan Chase & Co.',
                    price: 165.32,
                    change: 0.78,
                    changePercent: 0.47,
                    volume: 12456300,
                    marketCap: 485000000000,
                    sector: 'finance',
                    market: 'NYSE',
                    peRatio: 11.8,
                    high52w: 172.81,
                    low52w: 135.19,
                    dividendYield: 2.15
                },
                {
                    symbol: 'JNJ',
                    name: 'Johnson & Johnson',
                    price: 160.85,
                    change: -0.52,
                    changePercent: -0.32,
                    volume: 8745200,
                    marketCap: 420000000000,
                    sector: 'healthcare',
                    market: 'NYSE',
                    peRatio: 24.1,
                    high52w: 169.94,
                    low52w: 143.13,
                    dividendYield: 3.05
                },
                {
                    symbol: 'VIC',
                    name: 'Vingroup Joint Stock Company',
                    price: 42.50,
                    change: 1.20,
                    changePercent: 2.90,
                    volume: 2156700,
                    marketCap: 18500000000,
                    sector: 'consumer',
                    market: 'HOSE',
                    peRatio: 18.5,
                    high52w: 48.30,
                    low52w: 35.20,
                    dividendYield: 1.2
                },
                {
                    symbol: 'VNM',
                    name: 'Vietnam Dairy Products Joint Stock Company',
                    price: 78.90,
                    change: -0.80,
                    changePercent: -1.00,
                    volume: 1845600,
                    marketCap: 15200000000,
                    sector: 'consumer',
                    market: 'HOSE',
                    peRatio: 22.3,
                    high52w: 85.50,
                    low52w: 68.40,
                    dividendYield: 4.5
                },
                {
                    symbol: 'FPT',
                    name: 'FPT Corporation',
                    price: 89.20,
                    change: 2.30,
                    changePercent: 2.65,
                    volume: 3245800,
                    marketCap: 12800000000,
                    sector: 'technology',
                    market: 'HOSE',
                    peRatio: 16.8,
                    high52w: 95.60,
                    low52w: 72.30,
                    dividendYield: 2.8
                }
            ];

            return stocks;
        } catch (error) {
            console.error('Error fetching stocks:', error);
            throw error;
        }
    }
static async getStockDetail(symbol) {
    try {
        // Gọi API backend lấy dữ liệu có thật
        const res = await fetch(`/api/stock_detail/?symbol=${symbol}`);
        const data = await res.json();

        if (!data.success || !data.stock) {
            throw new Error("Stock not found in backend");
        }

        const stock = data.stock;

        // Trả về kèm dữ liệu fake
        return {
            ...stock,
           
            headquarters: "TP. Hồ Chí Minh, Việt Nam", // fake fix cứng
            website: `https://www.${stock.symbol.toLowerCase()}.com`,
            revenue: `${Math.floor(Math.random() * 100000) + 1000} tỷ VND`,
            netIncome: `${Math.floor(Math.random() * 20000) + 500} tỷ VND`,
            grossMargin: `${Math.floor(Math.random() * 40) + 10}%`,
            operatingMargin: `${Math.floor(Math.random() * 20) + 5}%`,
            roe: `${Math.floor(Math.random() * 20) + 5}%`,
            roa: `${Math.floor(Math.random() * 15) + 3}%`,
            enterpriseValue: (stock.market_cap || 1000000000) * (1 + Math.random() * 0.5), // gấp 1 - 1.5 lần
            pbRatio: (Math.random() * 5 + 1).toFixed(2),
            beta: (Math.random() * 2 + 0.5).toFixed(2)
        };
    } catch (error) {
        console.error("Error fetching stock detail:", error);
        throw error;
    }
}

    static async getCompanyProfile(symbol) {
        try {
            const stockDetail = await this.getStockDetail(symbol);
            
            return {
                ...stockDetail,
                tagline: this.getCompanyTagline(symbol),
                exchange: stockDetail.market
            };
        } catch (error) {
            console.error('Error fetching company profile:', error);
            throw error;
        }
    }

    static async getStockChart(symbol, period = '1D') {
        try {
            await this.delay(200);
            
            const basePrice = (await this.getStockDetail(symbol)).close_price;

            const dataPoints = this.getDataPointsForPeriod(period);
            const labels = [];
            const prices = [];
            
            let currentPrice = basePrice * 0.95; // Start slightly below current price
            const volatility = 0.02; // 2% volatility
            
            for (let i = 0; i < dataPoints; i++) {
                labels.push(this.generateLabel(i, period));
                
                // Generate realistic price movement
                const change = (Math.random() - 0.5) * 2 * volatility;
                currentPrice = Math.max(currentPrice * (1 + change), basePrice * 0.8);
                prices.push(parseFloat(currentPrice.toFixed(2)));
            }
            
            // Ensure the last price is close to the current price
            prices[prices.length - 1] = basePrice;
            
            return {
                labels,
                datasets: [{
                    label: symbol,
                    data: prices,
                    borderColor: prices[prices.length - 1] >= prices[0] ? '#22c55e' : '#ef4444',
                    backgroundColor: prices[prices.length - 1] >= prices[0] ? 
                        'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                }]
            };
        } catch (error) {
            console.error('Error fetching stock chart:', error);
            throw error;
        }
    }

    static async getNews() {
        try {
            await this.delay(400);
            
            const news = [
                {
                    id: 'news_1',
                    title: 'Tech Stocks Rally as Market Optimism Returns',
                    description: 'Technology stocks surged in morning trading as investors showed renewed confidence in growth prospects for the sector.',
                    category: 'tech',
                    date: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
                    image: 'https://images.pexels.com/photos/590020/pexels-photo-590020.jpeg?auto=compress&cs=tinysrgb&w=400&h=250&fit=crop'
                },
                {
                    id: 'news_2',
                    title: 'Federal Reserve Hints at Interest Rate Stability',
                    description: 'Central bank officials suggest rates may remain steady in the coming months, providing clarity for market participants.',
                    category: 'economy',
                    date: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), // 4 hours ago
                    image: 'https://images.pexels.com/photos/6693655/pexels-photo-6693655.jpeg?auto=compress&cs=tinysrgb&w=400&h=250&fit=crop'
                },
                {
                    id: 'news_3',
                    title: 'Energy Sector Faces Headwinds Amid Price Volatility',
                    description: 'Oil and gas companies navigate challenging market conditions as commodity prices experience significant fluctuations.',
                    category: 'market',
                    date: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), // 6 hours ago
                    image: 'https://images.pexels.com/photos/4254551/pexels-photo-4254551.jpeg?auto=compress&cs=tinysrgb&w=400&h=250&fit=crop'
                },
                {
                    id: 'news_4',
                    title: 'Q4 Earnings Season Shows Strong Corporate Performance',
                    description: 'Major corporations report better-than-expected quarterly results, driving investor confidence across multiple sectors.',
                    category: 'stocks',
                    date: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(), // 8 hours ago
                    image: 'https://images.pexels.com/photos/6772076/pexels-photo-6772076.jpeg?auto=compress&cs=tinysrgb&w=400&h=250&fit=crop'
                },
                {
                    id: 'news_5',
                    title: 'Global Markets React to Economic Data Releases',
                    description: 'International markets show mixed reactions to latest economic indicators and employment figures.',
                    category: 'market',
                    date: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(), // 12 hours ago
                    image: 'https://images.pexels.com/photos/3483098/pexels-photo-3483098.jpeg?auto=compress&cs=tinysrgb&w=400&h=250&fit=crop'
                },
                {
                    id: 'news_6',
                    title: 'Artificial Intelligence Investments Surge in Tech Sector',
                    description: 'Technology companies increase AI investments as the sector continues to show remarkable growth potential.',
                    category: 'tech',
                    date: new Date(Date.now() - 18 * 60 * 60 * 1000).toISOString(), // 18 hours ago
                    image: 'https://images.pexels.com/photos/8386440/pexels-photo-8386440.jpeg?auto=compress&cs=tinysrgb&w=400&h=250&fit=crop'
                },
                {
                    id: 'news_7',
                    title: 'Healthcare Stocks Gain on Breakthrough Drug Approvals',
                    description: 'Pharmaceutical companies see significant gains following regulatory approvals for innovative treatments.',
                    category: 'stocks',
                    date: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
                    image: 'https://images.pexels.com/photos/3825368/pexels-photo-3825368.jpeg?auto=compress&cs=tinysrgb&w=400&h=250&fit=crop'
                },
                {
                    id: 'news_8',
                    title: 'Inflation Data Influences Market Sentiment',
                    description: 'Latest consumer price index figures provide insights into economic trends and monetary policy direction.',
                    category: 'economy',
                    date: new Date(Date.now() - 30 * 60 * 60 * 1000).toISOString(), // 30 hours ago
                    image: 'https://images.pexels.com/photos/6801648/pexels-photo-6801648.jpeg?auto=compress&cs=tinysrgb&w=400&h=250&fit=crop'
                }
            ];

            return news;
        } catch (error) {
            console.error('Error fetching news:', error);
            throw error;
        }
    }

    static getDataPointsForPeriod(period) {
        const dataPoints = {
            '1D': 48,    // 30-minute intervals
            '1W': 35,    // Daily intervals
            '1M': 30,    // Daily intervals
            '3M': 60,    // Every 1.5 days
            '1Y': 52     // Weekly intervals
        };
        return dataPoints[period] || 30;
    }

    static generateLabel(index, period) {
        const now = new Date();
        
        switch (period) {
            case '1D':
                const thirtyMinutesAgo = new Date(now.getTime() - (47 - index) * 30 * 60 * 1000);
                return thirtyMinutesAgo.toLocaleTimeString('en-US', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                });
            case '1W':
                const daysAgo = new Date(now.getTime() - (34 - index) * 24 * 60 * 60 * 1000);
                return daysAgo.toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric' 
                });
            case '1M':
                const monthDaysAgo = new Date(now.getTime() - (29 - index) * 24 * 60 * 60 * 1000);
                return monthDaysAgo.toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric' 
                });
            case '3M':
                const threeDaysAgo = new Date(now.getTime() - (59 - index) * 1.5 * 24 * 60 * 60 * 1000);
                return threeDaysAgo.toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric' 
                });
            case '1Y':
                const weeksAgo = new Date(now.getTime() - (51 - index) * 7 * 24 * 60 * 60 * 1000);
                return weeksAgo.toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric' 
                });
            default:
                return index.toString();
        }
    }

    static delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}