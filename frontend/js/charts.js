// 初始化英雄区域图表（页面加载时调用）
function initHeroChart() {
    const ctx = document.getElementById('hero-chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['2018', '2019', '2020', '2021', '2022', '2023'],
            datasets: [{
                label: '美国电动汽车销量（万辆）',
                data: [36, 49, 63, 91, 131, 178],
                borderColor: 'rgba(255, 255, 255, 0.8)',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: 'rgba(255, 255, 255, 0.8)' }
                }
            },
            scales: {
                x: { ticks: { color: 'rgba(255, 255, 255, 0.7)' } },
                y: { ticks: { color: 'rgba(255, 255, 255, 0.7)' } }
            }
        }
    });
}

// 渲染车型区域分布图表（查询后调用）
function renderRegionDistribution(data) {
    const ctx = document.getElementById('region-distribution-chart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: [
                    '#165DFF', '#36D399', '#7C3AED', '#F59E0B', '#EF4444'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'right' } }
        }
    });
}

// 页面加载时初始化图表
document.addEventListener('DOMContentLoaded', () => {
    initHeroChart();
});