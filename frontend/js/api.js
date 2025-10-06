// 车型查询：发送请求到后端（处理响应结构和参数编码）
async function queryModelData(brand, model) {
    try {
        // 使用URLSearchParams处理参数编码，支持特殊字符
        const params = new URLSearchParams();
        params.append('brand', brand);
        params.append('model', model);
        
        const response = await fetch(`http://localhost:8000/api/models?${params}`);
        const data = await response.json(); // 先解析JSON，无论响应状态码
        
        if (!response.ok) {
            // 处理后端返回的错误信息（如404未找到）
            throw new Error(data.message || "查询失败：未找到车型数据");
        }
        
        // 后端返回格式为 {success: true, data: {...}}，需通过data字段获取数据
        return data.data;
    } catch (error) {
        console.error("车型查询错误:", error);
        alert(error.message || "查询失败，请重试");
        return null;
    }
}

// 区域查询：发送请求到后端（处理可选参数和响应结构）
async function queryRegionData(state, city, county) {
    try {
        const params = new URLSearchParams();
        params.append('state', state);
        // 可选参数：仅当有值时添加，避免传递空字符串
        if (city) params.append('city', city);
        if (county) params.append('county', county);
        
        const response = await fetch(`http://localhost:8000/api/regions?${params}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || "查询失败：未找到区域数据");
        }
        
        // 后端返回格式为 {success: true, data: {...}}
        return data.data;
    } catch (error) {
        console.error("区域查询错误:", error);
        alert(error.message || "查询失败，请重试");
        return null;
    }
}

// 生成详细报告（异步任务）
async function submitDetailedReport(brand, model) {
    try {
        const params = new URLSearchParams();
        params.append('brand', brand);
        params.append('model', model);
        
        const response = await fetch(`http://localhost:8000/api/models/detailed-report?${params}`);
        const data = await response.json();
        
        if (!response.ok || !data.success) {
            throw new Error(data.message || "提交报告任务失败");
        }
        
        return data.task_id; // 从成功响应中获取task_id
    } catch (error) {
        console.error("提交报告任务错误:", error);
        alert(error.message || "提交失败，请重试");
        return null;
    }
}

// 轮询异步任务结果
async function checkTaskResult(taskId) {
    try {
        const response = await fetch(`http://localhost:8000/api/tasks/${taskId}`);
        const result = await response.json();
        
        // 直接返回完整结果（包含success、status、result等字段）
        return result;
    } catch (error) {
        console.error("查询任务结果错误:", error);
        alert("查询任务状态失败，请重试");
        return null;
    }
}

// 绑定表单提交事件
document.addEventListener('DOMContentLoaded', () => {
    // 车型查询表单提交
    const modelForm = document.getElementById('model-query-form');
    if (modelForm) { // 避免DOM元素不存在时报错
        modelForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const brand = document.getElementById('brand').value.trim();
            const model = document.getElementById('model').value.trim();
            
            // 简单验证
            if (!brand || !model) {
                alert("请输入品牌和车型");
                return;
            }
            
            const result = await queryModelData(brand, model);
            if (result) {
                // 从后端返回的data字段中获取具体数据
                document.getElementById('range-result').textContent = `${result.range || '未知'} 英里`;
                document.getElementById('price-result').textContent = result.price 
                    ? `$${result.price.toLocaleString()}` 
                    : '未知';
                document.getElementById('market-share-result').textContent = `${result.market_share || '未知'}%`;
                document.getElementById('popular-region-result').textContent = result.popular_region || '未知';
                document.getElementById('model-result').classList.remove('hidden');
                // 渲染区域分布图表
                if (window.renderRegionDistribution) {
                    renderRegionDistribution(result.region_distribution || {});
                }
            }
        });
    }

    // 区域查询表单提交
    const regionForm = document.getElementById('region-query-form');
    if (regionForm) { // 避免DOM元素不存在时报错
        regionForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const state = document.getElementById('state').value.trim();
            const city = document.getElementById('city').value.trim();
            const county = document.getElementById('county').value.trim();
            
            // 验证必填参数
            if (!state) {
                alert("请选择州");
                return;
            }
            
            const result = await queryRegionData(state, city, county);
            if (result) {
                document.getElementById('ev-count-result').textContent = result.ev_count 
                    ? result.ev_count.toLocaleString() 
                    : '0';
                // 补充其他区域数据显示（如占比、充电站数量）
                if (document.getElementById('ev-ratio-result')) {
                    document.getElementById('ev-ratio-result').textContent = `${result.ev_ratio || 0}%`;
                }
                if (document.getElementById('charging-stations-result')) {
                    document.getElementById('charging-stations-result').textContent = result.charging_stations 
                        ? result.charging_stations.toLocaleString() 
                        : '0';
                }
                document.getElementById('region-result').classList.remove('hidden');
            }
        });
    }
});