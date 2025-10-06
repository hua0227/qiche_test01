// 车型查询：发送请求到后端（处理响应结构和参数编码，支持特殊字符）
async function queryModelData(brand, model) {
    try {
        // 使用URLSearchParams处理参数编码，避免特殊字符导致的请求错误
        const params = new URLSearchParams();
        params.append('brand', brand);
        params.append('model', model);
        
        const response = await fetch(`http://localhost:8000/api/models?${params}`);
        const data = await response.json(); // 先解析JSON，获取后端详细错误信息
        
        if (!response.ok) {
            // 传递后端返回的具体错误（如“未找到该车型数据”），而非笼统提示
            throw new Error(data.message || "查询失败：未找到车型数据");
        }
        
        // 直接返回后端数据（若后端返回格式为{success:true, data:{...}}则取data，否则取完整data）
        return data.data || data;
    } catch (error) {
        console.error("车型查询错误:", error);
        alert(error.message || "查询失败，请重试");
        return null;
    }
}

// 区域查询：发送请求到后端（处理可选参数，避免空值传递）
async function queryRegionData(state, city, county) {
    try {
        const params = new URLSearchParams();
        params.append('state', state);
        // 可选参数：仅当有实际值时添加，避免传递空字符串导致后端查询异常
        if (city.trim()) params.append('city', city);
        if (county.trim()) params.append('county', county);
        
        const response = await fetch(`http://localhost:8000/api/regions?${params}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || "查询失败：未找到区域数据");
        }
        
        // 适配后端返回格式（优先取data字段，无则取完整响应）
        return data.data || data;
    } catch (error) {
        console.error("区域查询错误:", error);
        alert(error.message || "查询失败，请重试");
        return null;
    }
}

// 生成详细报告（异步任务，提交任务并返回task_id用于轮询）
async function submitDetailedReport(brand, model) {
    try {
        const params = new URLSearchParams();
        params.append('brand', brand);
        params.append('model', model);
        
        const response = await fetch(`http://localhost:8000/api/models/detailed-report?${params}`);
        const data = await response.json();
        
        if (!response.ok || !data.task_id) {
            throw new Error(data.message || "提交报告任务失败：未获取到任务ID");
        }
        
        return data.task_id; // 返回任务ID，供后续轮询结果使用
    } catch (error) {
        console.error("提交报告任务错误:", error);
        alert(error.message || "提交失败，请重试");
        return null;
    }
}

// 轮询异步任务结果（查询报告生成状态）
async function checkTaskResult(taskId) {
    try {
        const response = await fetch(`http://localhost:8000/api/tasks/${taskId}`);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.message || "查询任务状态失败");
        }
        
        return result; // 返回完整任务结果（含status、result等字段）
    } catch (error) {
        console.error("查询任务结果错误:", error);
        alert(error.message || "查询任务状态失败，请重试");
        return null;
    }
}

// 绑定表单提交事件（确保DOM加载完成后执行，避免元素不存在报错）
document.addEventListener('DOMContentLoaded', () => {
    // 车型查询表单提交（增加DOM存在性检查，增强兼容性）
    const modelForm = document.getElementById('model-query-form');
    if (modelForm) {
        modelForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const brand = document.getElementById('brand').value.trim();
            const model = document.getElementById('model').value.trim();
            
            // 前端参数验证：避免空值请求
            if (!brand || !model) {
                alert("请输入品牌和车型（不能为空）");
                return;
            }
            
            const result = await queryModelData(brand, model);
            if (result) {
                // 渲染查询结果到页面（适配后端返回的字段名，与CSV数据匹配）
                document.getElementById('range-result').textContent = `${result.electric_range || '未知'} 英里`;
                document.getElementById('price-result').textContent = result.base_msrp 
                    ? `$${result.base_msrp.toLocaleString()}` 
                    : '未知';
                document.getElementById('market-share-result').textContent = `${result.market_share || '未知'}%`;
                document.getElementById('popular-region-result').textContent = result.state || '未知';
                document.getElementById('model-result').classList.remove('hidden');
                
                // 渲染区域分布图表（若存在图表渲染函数则调用）
                if (window.renderRegionDistribution && result.region_distribution) {
                    renderRegionDistribution(result.region_distribution);
                }
            }
        });
    }

    // 区域查询表单提交（同样增加DOM检查和参数验证）
    const regionForm = document.getElementById('region-query-form');
    if (regionForm) {
        regionForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const state = document.getElementById('state').value.trim();
            const city = document.getElementById('city').value.trim();
            const county = document.getElementById('county').value.trim();
            
            // 前端参数验证：州为必填项
            if (!state) {
                alert("请选择或输入州（必填项）");
                return;
            }
            
            const result = await queryRegionData(state, city, county);
            if (result) {
                // 渲染区域查询结果（适配后端统计字段，如车辆总数）
                document.getElementById('ev-count-result').textContent = result.ev_count 
                    ? result.ev_count.toLocaleString() 
                    : '0';
                // 补充其他区域数据（若页面有对应DOM）
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