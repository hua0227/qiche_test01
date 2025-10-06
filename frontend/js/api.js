// 车型查询：发送请求到后端
async function queryModelData(brand, model) {
    try {
        const response = await fetch(`http://localhost:8000/api/models?brand=${brand}&model=${model}`);
        if (!response.ok) throw new Error("查询失败");
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("车型查询错误:", error);
        alert("查询失败，请重试");
        return null;
    }
}

// 区域查询：发送请求到后端
async function queryRegionData(state, city, county) {
    try {
        const response = await fetch(`http://localhost:8000/api/regions?state=${state}&city=${city}&county=${county}`);
        if (!response.ok) throw new Error("查询失败");
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("区域查询错误:", error);
        alert("查询失败，请重试");
        return null;
    }
}

// 生成详细报告（异步任务，通过Broker处理）
async function submitDetailedReport(brand, model) {
    try {
        const response = await fetch(`http://localhost:8000/api/models/detailed-report?brand=${brand}&model=${model}`);
        const data = await response.json();
        return data.task_id; // 返回任务ID用于轮询结果
    } catch (error) {
        console.error("提交报告任务错误:", error);
        return null;
    }
}

// 轮询异步任务结果
async function checkTaskResult(taskId) {
    try {
        const response = await fetch(`http://localhost:8000/api/tasks/${taskId}`);
        const result = await response.json();
        return result;
    } catch (error) {
        console.error("查询任务结果错误:", error);
        return null;
    }
}

// 绑定表单提交事件（需在01.html中调用）
document.addEventListener('DOMContentLoaded', () => {
    // 车型查询表单提交
    const modelForm = document.getElementById('model-query-form');
    modelForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const brand = document.getElementById('brand').value;
        const model = document.getElementById('model').value;
        const result = await queryModelData(brand, model);
        if (result) {
            // 显示结果到页面（对应01.html中的结果区域）
            document.getElementById('range-result').textContent = `${result.range} 英里`;
            document.getElementById('price-result').textContent = `$${result.price.toLocaleString()}`;
            document.getElementById('market-share-result').textContent = `${result.market_share}%`;
            document.getElementById('popular-region-result').textContent = result.popular_region;
            document.getElementById('model-result').classList.remove('hidden');
            // 渲染区域分布图表（调用charts.js中的方法）
            renderRegionDistribution(result.region_distribution);
        }
    });

    // 区域查询表单提交（类似逻辑）
    const regionForm = document.getElementById('region-query-form');
    regionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const state = document.getElementById('state').value;
        const city = document.getElementById('city').value;
        const county = document.getElementById('county').value;
        const result = await queryRegionData(state, city, county);
        if (result) {
            // 显示区域查询结果（需在01.html中补充结果区域DOM）
            document.getElementById('ev-count-result').textContent = result.ev_count.toLocaleString();
            document.getElementById('region-result').classList.remove('hidden');
        }
    });
});