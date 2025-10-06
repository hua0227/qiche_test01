from fastapi import APIRouter, Query, HTTPException
from backend.config.database import EVDataQuery  # 引入CSV数据查询工具

router = APIRouter(
    prefix="/api/regions",
    tags=["区域数据"],
    responses={404: {"description": "未找到"}}
)

@router.get("/states")
async def get_all_states():
    """获取所有州列表（数据来自CSV）"""
    # 从所有记录中提取不重复的州，排除空值并排序
    all_records = EVDataQuery._get_all_records()
    states = {record.state for record in all_records if record.state and record.state != "未知"}
    sorted_states = sorted(states)
    
    if not sorted_states:
        raise HTTPException(status_code=404, detail="未找到州数据")
    return {"success": True, "data": sorted_states}

@router.get("/cities")
async def get_cities(
    state: str = Query(..., description="州名称（如california，不区分大小写）")
):
    """根据州获取城市列表（数据来自CSV）"""
    # 获取指定州的所有记录，提取不重复的城市
    state_records = EVDataQuery.get_by_state(state)
    cities = {record.city for record in state_records if record.city}
    sorted_cities = sorted(cities)
    
    if not sorted_cities:
        raise HTTPException(status_code=404, detail=f"未找到{state}的城市数据")
    return {"success": True, "data": sorted_cities}

@router.get("/counties")
async def get_counties(
    city: str = Query(..., description="城市名称（不区分大小写）"),
    state: str = Query(..., description="所属州名称（如california，用于精确筛选）")
):
    """根据城市和所属州获取县列表（数据来自CSV）"""
    # 先通过州筛选，再通过城市筛选，提取不重复的县
    state_records = EVDataQuery.get_by_state(state)
    city_records = [
        r for r in state_records 
        if r.city and r.city.lower() == city.lower()
    ]
    counties = {record.county for record in city_records if record.county}
    sorted_counties = sorted(counties)
    
    if not sorted_counties:
        raise HTTPException(status_code=404, detail=f"未找到{city}的县数据")
    return {"success": True, "data": sorted_counties}

@router.get("/")
async def query_region(
    state: str = Query(..., description="州"),
    city: str = Query(None, description="市（可选）"),
    county: str = Query(None, description="县（可选）")
):
    """查询特定区域的电动汽车数据（数据来自CSV）"""
    # 基础筛选：先按州过滤
    records = EVDataQuery.get_by_state(state)
    
    # 可选筛选：城市
    if city:
        city_lower = city.lower()
        records = [r for r in records if r.city and r.city.lower() == city_lower]
    
    # 可选筛选：县
    if county:
        county_lower = county.lower()
        records = [r for r in records if r.county and r.county.lower() == county_lower]
    
    if not records:
        raise HTTPException(status_code=404, detail="未找到该区域数据")
    
    # 计算汇总数据（基于CSV中的字段）
    total_ev = sum(record.vehicle_count for record in records)
    total_stations = sum(
        # 假设CSV中"Electric Utility"字段可能包含充电站相关信息，此处简化处理
        1 for record in records if record.electric_utility  # 实际场景可能需要更精确的统计逻辑
    )
    # 提取该区域的电动车类型分布
    ev_type_distribution = {}
    for record in records:
        if record.ev_type:
            ev_type = record.ev_type
            ev_type_distribution[ev_type] = ev_type_distribution.get(ev_type, 0) + record.vehicle_count
    
    return {"success": True, "data": {
        "state": state,
        "city": city,
        "county": county,
        "total_ev_count": total_ev,
        "charging_stations_estimated": total_stations,  # 估算值，根据实际业务调整
        "ev_type_distribution": ev_type_distribution,
        "record_count": len(records)  # 数据记录条数
    }}