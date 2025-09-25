// Chart.js configurations and utilities for TIMB Trading System

class TIMBCharts {
    constructor() {
        this.defaultColors = {
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
        
        this.defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            family: 'Inter, sans-serif',
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#ffffff',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        title: function(context) {
                            return context[0].label || '';
                        }
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        };
    }

    getTheme() {
        return document.body.classList.contains('merchant-theme') ? 'merchant' : 'timb';
    }

    getColors() {
        return this.defaultColors[this.getTheme()];
    }

    createGradient(ctx, color1, color2, direction = 'vertical') {
        const gradient = direction === 'vertical' 
            ? ctx.createLinearGradient(0, 0, 0, 400)
            : ctx.createLinearGradient(0, 0, 400, 0);
        
        gradient.addColorStop(0, color1);
        gradient.addColorStop(1, color2);
        return gradient;
    }

    // Price Trend Chart
    createPriceTrendChart(ctx, data, options = {}) {
        const colors = this.getColors();
        
        const config = {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: data.datasets.map((dataset, index) => ({
                    ...dataset,
                    borderColor: dataset.borderColor || colors.primary,
                    backgroundColor: dataset.backgroundColor || this.createGradient(ctx, colors.primary + '40', colors.primary + '10'),
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: dataset.borderColor || colors.primary,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }))
            },
            options: {
                ...this.defaultOptions,
                ...options,
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time Period',
                            font: {
                                family: 'Inter, sans-serif',
                                size: 14,
                                weight: 'bold'
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Price (USD/kg)',
                            font: {
                                family: 'Inter, sans-serif',
                                size: 14,
                                weight: 'bold'
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toFixed(2);
                            }
                        }
                    }
                },
                plugins: {
                    ...this.defaultOptions.plugins,
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': $' + context.parsed.y.toFixed(2) + '/kg';
                            }
                        }
                    }
                }
            }
        };

        return new Chart(ctx, config);
    }

    // Volume Chart
    createVolumeChart(ctx, data, options = {}) {
        const colors = this.getColors();
        
        const config = {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: data.datasets.map((dataset, index) => ({
                    ...dataset,
                    backgroundColor: dataset.backgroundColor || this.createGradient(ctx, colors.secondary, colors.primary),
                    borderColor: dataset.borderColor || colors.primary,
                    borderWidth: 2,
                    borderRadius: 4,
                    borderSkipped: false,
                }))
            },
            options: {
                ...this.defaultOptions,
                ...options,
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Date',
                            font: {
                                family: 'Inter, sans-serif',
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Volume (kg)',
                            font: {
                                family: 'Inter, sans-serif',
                                size: 14,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString() + ' kg';
                            }
                        }
                    }
                },
                plugins: {
                    ...this.defaultOptions.plugins,
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.parsed.y.toLocaleString() + ' kg';
                            }
                        }
                    }
                }
            }
        };

        return new Chart(ctx, config);
    }

    // Fraud Detection Chart
    createFraudDetectionChart(ctx, data, options = {}) {
        const colors = this.getColors();
        
        const config = {
            type: 'doughnut',
            data: {
                labels: data.labels || ['Normal', 'Suspicious', 'Fraudulent'],
                datasets: [{
                    data: data.values || [],
                    backgroundColor: [
                        colors.success,
                        colors.warning,
                        colors.danger
                    ],
                    borderWidth: 3,
                    borderColor: '#ffffff',
                    hoverBorderWidth: 4
                }]
            },
            options: {
                ...this.defaultOptions,
                ...options,
                cutout: '60%',
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: {
                        position: 'bottom',
                        labels: {
                            generateLabels: function(chart) {
                                const data = chart.data;
                                return data.labels.map((label, index) => ({
                                    text: label,
                                    fillStyle: data.datasets[0].backgroundColor[index],
                                    strokeStyle: data.datasets[0].backgroundColor[index],
                                    lineWidth: 0,
                                    pointStyle: 'circle',
                                    hidden: false,
                                    index: index
                                }));
                            }
                        }
                    },
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                            }
                        }
                    }
                }
            }
        };

        return new Chart(ctx, config);
    }

    // Yield Prediction Chart
    createYieldChart(ctx, data, options = {}) {
        const colors = this.getColors();
        
        const config = {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [
                    {
                        label: 'Predicted Yield',
                        data: data.predicted || [],
                        borderColor: colors.primary,
                        backgroundColor: colors.primary + '20',
                        fill: false,
                        tension: 0.4,
                        pointStyle: 'circle',
                        pointRadius: 5,
                        pointHoverRadius: 7
                    },
                    {
                        label: 'Actual Yield',
                        data: data.actual || [],
                        borderColor: colors.accent,
                        backgroundColor: colors.accent + '20',
                        fill: false,
                        tension: 0.4,
                        pointStyle: 'triangle',
                        pointRadius: 5,
                        pointHoverRadius: 7
                    }
                ]
            },
            options: {
                ...this.defaultOptions,
                ...options,
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Year',
                            font: {
                                family: 'Inter, sans-serif',
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Yield (kg)',
                            font: {
                                family: 'Inter, sans-serif',
                                size: 14,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            callback: function(value) {
                                return (value / 1000000).toFixed(1) + 'M kg';
                            }
                        }
                    }
                },
                plugins: {
                    ...this.defaultOptions.plugins,
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + (context.parsed.y / 1000000).toFixed(2) + 'M kg';
                            }
                        }
                    }
                }
            }
        };

        return new Chart(ctx, config);
    }

    // Inventory Distribution Chart
    createInventoryChart(ctx, data, options = {}) {
        const colors = this.getColors();
        
        const config = {
            type: 'polarArea',
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.values || [],
                    backgroundColor: [
                        colors.primary + '80',
                        colors.secondary + '80',
                        colors.accent + '80',
                        colors.info + '80',
                        colors.success + '80',
                        colors.warning + '80'
                    ],
                    borderColor: [
                        colors.primary,
                        colors.secondary,
                        colors.accent,
                        colors.info,
                        colors.success,
                        colors.warning
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                ...this.defaultOptions,
                ...options,
                scales: {
                    r: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString() + ' kg';
                            }
                        }
                    }
                },
                plugins: {
                    ...this.defaultOptions.plugins,
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed.toLocaleString() + ' kg';
                            }
                        }
                    }
                }
            }
        };

        return new Chart(ctx, config);
    }

    // Real-time Dashboard Chart
    createRealtimeChart(ctx, initialData = {}, options = {}) {
        const colors = this.getColors();
        
        const config = {
            type: 'line',
            data: {
                labels: initialData.labels || [],
                datasets: [{
                    label: 'Live Data',
                    data: initialData.data || [],
                    borderColor: colors.accent,
                    backgroundColor: this.createGradient(ctx, colors.accent + '40', colors.accent + '10'),
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    animation: false // Disable animation for real-time updates
                }]
            },
            options: {
                ...this.defaultOptions,
                ...options,
                animation: false,
                scales: {
                    x: {
                        type: 'realtime',
                        realtime: {
                            duration: 20000,
                            refresh: 1000,
                            delay: 2000,
                            onRefresh: function(chart) {
                                // This would be called from external real-time data source
                                if (window.realtimeDataCallback) {
                                    window.realtimeDataCallback(chart);
                                }
                            }
                        }
                    },
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        };

        return new Chart(ctx, config);
    }

    // Risk Assessment Radar Chart
    createRiskRadarChart(ctx, data, options = {}) {
        const colors = this.getColors();
        
        const config = {
            type: 'radar',
            data: {
                labels: data.labels || ['Market Risk', 'Credit Risk', 'Operational Risk', 'Compliance Risk', 'Fraud Risk'],
                datasets: [{
                    label: 'Risk Level',
                    data: data.values || [],
                    borderColor: colors.danger,
                    backgroundColor: colors.danger + '20',
                    pointBackgroundColor: colors.danger,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5
                }]
            },
            options: {
                ...this.defaultOptions,
                ...options,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        pointLabels: {
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        }
                    }
                },
                plugins: {
                    ...this.defaultOptions.plugins,
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed.r + '%';
                            }
                        }
                    }
                }
            }
        };

        return new Chart(ctx, config);
    }

    // Performance Metrics Chart
    createPerformanceChart(ctx, data, options = {}) {
        const colors = this.getColors();
        
        const config = {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: data.datasets.map((dataset, index) => ({
                    ...dataset,
                    backgroundColor: this.createGradient(ctx, colors.primary, colors.secondary),
                    borderColor: colors.primary,
                    borderWidth: 2,
                    borderRadius: 6,
                    borderSkipped: false
                }))
            },
            options: {
                ...this.defaultOptions,
                ...options,
                indexAxis: 'y',
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                plugins: {
                    ...this.defaultOptions.plugins,
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.parsed.x + '%';
                            }
                        }
                    }
                }
            }
        };

        return new Chart(ctx, config);
    }

    // Update chart data (for real-time updates)
    updateChart(chart, newData) {
        if (!chart || !newData) return;

        if (newData.labels) {
            chart.data.labels = newData.labels;
        }

        if (newData.datasets) {
            newData.datasets.forEach((newDataset, index) => {
                if (chart.data.datasets[index]) {
                    chart.data.datasets[index].data = newDataset.data;
                }
            });
        }

        chart.update('none'); // Update without animation for real-time
    }

    // Destroy chart safely
    destroyChart(chart) {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
        }
    }

    // Chart animation presets
    getAnimationPresets() {
        return {
            fadeIn: {
                onProgress: function(animation) {
                    animation.chart.canvas.style.opacity = animation.currentStep / animation.numSteps;
                }
            },
            slideUp: {
                onProgress: function(animation) {
                    const progress = animation.currentStep / animation.numSteps;
                    animation.chart.canvas.style.transform = `translateY(${(1 - progress) * 50}px)`;
                }
            },
            bounce: {
                easing: 'easeOutBounce',
                duration: 1500
            }
        };
    }
}

// Global instance
window.TIMBCharts = new TIMBCharts();

// Auto-initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-detect and initialize charts with data attributes
    const chartElements = document.querySelectorAll('[data-chart-type]');
    
    chartElements.forEach(element => {
        const chartType = element.dataset.chartType;
        const chartData = element.dataset.chartData ? JSON.parse(element.dataset.chartData) : {};
        const chartOptions = element.dataset.chartOptions ? JSON.parse(element.dataset.chartOptions) : {};
        
        const ctx = element.getContext('2d');
        
        switch (chartType) {
            case 'price-trend':
                window.TIMBCharts.createPriceTrendChart(ctx, chartData, chartOptions);
                break;
            case 'volume':
                window.TIMBCharts.createVolumeChart(ctx, chartData, chartOptions);
                break;
            case 'fraud-detection':
                window.TIMBCharts.createFraudDetectionChart(ctx, chartData, chartOptions);
                break;
            case 'yield':
                window.TIMBCharts.createYieldChart(ctx, chartData, chartOptions);
                break;
            case 'inventory':
                window.TIMBCharts.createInventoryChart(ctx, chartData, chartOptions);
                break;
            case 'realtime':
                window.TIMBCharts.createRealtimeChart(ctx, chartData, chartOptions);
                break;
            case 'risk-radar':
                window.TIMBCharts.createRiskRadarChart(ctx, chartData, chartOptions);
                break;
            case 'performance':
                window.TIMBCharts.createPerformanceChart(ctx, chartData, chartOptions);
                break;
        }
    });
});