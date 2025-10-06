// 初始化英雄区域图表（页面加载时调用）
function initHeroChart() {
    // 检查图表容器是否存在，避免DOM错误
    const chartContainer = document.getElementById('hero-chart');
    if (!chartContainer) {
        console.warn('英雄区域图表容器不存在，跳过初始化');
        return;
    }

    const ctx = chartContainer.getContext('2d');
    // 销毁可能存在的旧图表实例（避免重复渲染）
    if (window.heroChartInstance) {
        window.heroChartInstance.destroy();
    }

    // 创建新图表实例并缓存
    window.heroChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['2018', '2019', '2020', '2021', '2022', '2023'],
            datasets: [{
                label: '美国电动汽车销量（万辆）',
                data: [36, 49, 63, 91, 131, 178],
                borderColor: 'rgba(255, 255, 255, 0.8)',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 2,  // 增加线条宽度，提升可读性
                tension: 0.4,
                fill: true,
                pointBackgroundColor: 'rgba(255, 255, 255, 1)',  // 数据点颜色
                pointRadius: 4,  // 数据点大小
                pointHoverRadius: 6  //  hover时数据点大小
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,  // 允许图表自适应容器大小
            plugins: {
                legend: {
                    labels: { 
                        color: 'rgba(255, 255, 255, 0.8)',
                        font: { size: 12 }  // 调整图例字体大小
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',  //  tooltip背景
                    titleColor: '#fff',
                    bodyColor: '#fff'
                }
            },
            scales: {
                x: { 
                    ticks: { color: 'rgba(255, 255, 255, 0.7)' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }  // 网格线颜色
                },
                y: { 
                    ticks: { color: 'rgba(255, 255, 255, 0.7)' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    beginAtZero: true  // Y轴从0开始，更直观
                }
            },
            interaction: {
                mode: 'index',  // 鼠标hover时显示对应索引的所有数据
                intersect: false
            }
        }
    });
}

// 渲染车型区域分布图表（查询后调用）
function renderRegionDistribution(data) {
    // 数据有效性验证
    if (!data || typeof data !== 'object' || Object.keys(data).length === 0) {
        console.warn('无效的区域分布数据，无法渲染图表');
        return;
    }

    // 检查图表容器是否存在
    const chartContainer = document.getElementById('region-distribution-chart');
    if (!chartContainer) {
        console.warn('区域分布图表容器不存在，跳过渲染');
        return;
    }

    const ctx = chartContainer.getContext('2d');
    // 销毁旧实例
    if (window.regionChartInstance) {
        window.regionChartInstance.destroy();
    }

    // 生成动态颜色（支持更多区域）
    const baseColors = ['#165DFF', '#36D399', '#7C3AED', '#F59E0B', '#EF4444', '#06B6D4', '#EC4899', '#10B981'];
    const colors = Object.keys(data).map((_, index) => baseColors[index % baseColors.length]);

    // 创建新图表实例并缓存
    window.regionChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: colors,
                borderWidth: 1,
                borderColor: '#fff'  // 区域间白色边框，提升区分度
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { 
                    position: 'right',
                    labels: {
                        padding: 20,  // 图例项间距
                        font: { size: 11 }
                    }
                },
                tooltip: {
                    callbacks: {
                        // 显示百分比（基于后端返回的占比数据）
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            return `${label}: ${value}%`;
                        }
                    }
                }
            },
            cutout: '60%',  // 环形图内径比例，更美观
            animation: {
                animateScale: true,  // 缩放动画
                animateRotate: true  // 旋转动画
            }
        }
    });
}

// 页面加载时初始化图表
document.addEventListener('DOMContentLoaded', () => {
    // 确保DOM完全加载后初始化图表
    setTimeout(initHeroChart, 100);  // 轻微延迟，避免容器未就绪
});