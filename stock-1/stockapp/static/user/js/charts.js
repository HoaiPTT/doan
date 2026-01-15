// Charts module using Chart.js
class Charts {
    static stockChart = null;

    static renderStockChart(canvasId, chartData) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            console.error('Canvas element not found:', canvasId);
            return null;
        }

        // Destroy existing chart if it exists
        if (this.stockChart) {
            this.stockChart.destroy();
        }

        const config = {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 24, 39, 0.9)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#374151',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            title: function(context) {
                                return context[0].label;
                            },
                             label: function(context) {
                                const value = context.parsed.y;
                                return value != null ? `${value.toLocaleString('vi-VN')} ₫` : '0 ₫';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        },
                        border: {
                            display: false
                        },
                        ticks: {
                            maxRotation: 0,
                            maxTicksLimit: 8,
                            color: '#6B7280',
                            font: {
                                size: 12
                            }
                        }
                    },
                    y: {
                        display: true,
                        position: 'right',
                        grid: {
                            color: '#F3F4F6',
                            drawBorder: false
                        },
                        border: {
                            display: false
                        },
                        ticks: {
                            color: '#6B7280',
                            font: {
                                size: 12
                            },
                            callback: function(value) {
                                return '$' + value.toFixed(2);
                            }
                        }
                    }
                },
                elements: {
                    point: {
                        radius: 0,
                        hoverRadius: 6,
                        hoverBorderWidth: 2,
                        hoverBackgroundColor: '#ffffff'
                    },
                    line: {
                        borderCapStyle: 'round',
                        borderJoinStyle: 'round'
                    }
                },
                animation: {
                    duration: 750,
                    easing: 'easeInOutQuart'
                },
                onHover: (event, activeElements) => {
                    event.native.target.style.cursor = activeElements.length > 0 ? 'pointer' : 'default';
                }
            }
        };

        this.stockChart = new Chart(ctx, config);
        return this.stockChart;
    }

    static updateStockChart(chartData) {
        if (!this.stockChart) {
            console.error('No existing chart to update');
            return;
        }

        // Update chart data
        this.stockChart.data = chartData;
        
        // Update colors based on performance
        const firstPrice = chartData.datasets[0].data[0];
        const lastPrice = chartData.datasets[0].data[chartData.datasets[0].data.length - 1];
        const isPositive = lastPrice >= firstPrice;
        
        chartData.datasets[0].borderColor = isPositive ? '#22c55e' : '#ef4444';
        chartData.datasets[0].backgroundColor = isPositive ? 
            'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)';
        
        // Animate the update
        this.stockChart.update('active');
    }

    static renderPortfolioChart(canvasId, portfolioData) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            console.error('Canvas element not found:', canvasId);
            return null;
        }

        const config = {
            type: 'doughnut',
            data: {
                labels: portfolioData.labels,
                datasets: [{
                    data: portfolioData.values,
                    backgroundColor: [
                        '#3B82F6',
                        '#10B981',
                        '#F59E0B',
                        '#EF4444',
                        '#8B5CF6',
                        '#EC4899',
                        '#6B7280'
                    ],
                    borderWidth: 0,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle',
                            font: {
                                size: 12
                            },
                            color: '#374151'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 24, 39, 0.9)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#374151',
                        borderWidth: 1,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${percentage}%`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 1000
                }
            }
        };

        return new Chart(ctx, config);
    }

    static renderPerformanceChart(canvasId, performanceData) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            console.error('Canvas element not found:', canvasId);
            return null;
        }

        const config = {
            type: 'bar',
            data: {
                labels: performanceData.labels,
                datasets: [{
                    label: 'Return %',
                    data: performanceData.returns,
                    backgroundColor: function(context) {
                        const value = context.parsed.y;
                        return value >= 0 ? 'rgba(34, 197, 94, 0.8)' : 'rgba(239, 68, 68, 0.8)';
                    },
                    borderColor: function(context) {
                        const value = context.parsed.y;
                        return value >= 0 ? '#22c55e' : '#ef4444';
                    },
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 24, 39, 0.9)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#374151',
                        borderWidth: 1,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed.y;
                                return `Return: ${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        border: {
                            display: false
                        },
                        ticks: {
                            color: '#6B7280',
                            font: {
                                size: 12
                            }
                        }
                    },
                    y: {
                        grid: {
                            color: '#F3F4F6',
                            drawBorder: false
                        },
                        border: {
                            display: false
                        },
                        ticks: {
                            color: '#6B7280',
                            font: {
                                size: 12
                            },
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                animation: {
                    duration: 750,
                    easing: 'easeInOutQuart'
                }
            }
        };

        return new Chart(ctx, config);
    }

    // Utility method to generate sample portfolio data
    static generateSamplePortfolioData() {
        return {
            labels: ['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer', 'Industrial', 'Others'],
            values: [35, 20, 15, 10, 8, 7, 5]
        };
    }

    // Utility method to generate sample performance data
    static generateSamplePerformanceData() {
        return {
            labels: ['1M', '3M', '6M', '1Y', '2Y', '3Y'],
            returns: [2.5, -1.2, 8.7, 15.3, 22.1, 18.9]
        };
    }

    // Method to destroy all charts
    static destroyAllCharts() {
        if (this.stockChart) {
            this.stockChart.destroy();
            this.stockChart = null;
        }
    }

    // Method to resize all charts
    static resizeAllCharts() {
        if (this.stockChart) {
            this.stockChart.resize();
        }
    }
}

// Handle window resize
window.addEventListener('resize', () => {
    Charts.resizeAllCharts();
});

// Clean up charts when page unloads
window.addEventListener('beforeunload', () => {
    Charts.destroyAllCharts();
});