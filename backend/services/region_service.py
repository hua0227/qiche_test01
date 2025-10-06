from typing import List, Dict, Optional
from backend.config.database import EVDataQuery, ElectricVehicleRecord

# 移除Excel加载数据库的函数（不再依赖SQL数据库，使用CSV数据）


def get_regions_by_level(level: str = "state") -> List[str]:
    """获取指定层级的区域列表（state/city/county），数据来自CSV"""
    all_records = EVDataQuery._get_all_records()
    region_set = set()

    # 根据层级提取对应区域字段（去重并过滤空值）
    if level == "state":
        region_set = {
            record.state for record in all_records
            if record.state and record.state.strip()
        }
    elif level == "city":
        region_set = {
            record.city for record in all_records
            if record.city and record.city.strip()
        }
    elif level == "county":
        region_set = {
            record.county for record in all_records
            if record.county and record.county.strip()
        }

    # 转换为排序后的列表，确保返回格式一致
    return sorted(region_set)


def get_cities_by_state(state: str) -> List[str]:
    """根据州名称获取下属城市列表（数据来自CSV）"""
    # 利用EVDataQuery的州筛选方法获取该州所有记录
    state_records = EVDataQuery.get_by_state(state)
    # 提取城市并去重（过滤空值）
    cities = {
        record.city for record in state_records
        if record.city and record.city.strip()
    }
    return sorted(cities) if cities else []


def get_counties_by_city(city: str) -> List[str]:
    """根据城市名称获取下属县列表（数据来自CSV）"""
    all_records = EVDataQuery._get_all_records()
    city_lower = city.lower()
    # 筛选出匹配城市的记录，提取县并去重（过滤空值）
    counties = {
        record.county for record in all_records
        if record.city and record.city.lower() == city_lower
        and record.county and record.county.strip()
    }
    return sorted(counties) if counties else []


def get_region_data(state: str, city: Optional[str] = None, county: Optional[str] = None) -> Optional[Dict]:
    """获取特定区域的电动汽车数据（数据来自CSV）"""
    # 基础筛选：先获取该州的所有记录
    state_records = EVDataQuery.get_by_state(state)
    if not state_records:
        return None

    # 进一步筛选：城市（如果指定）
    filtered_records = state_records
    if city:
        city_lower = city.lower()
        filtered_records = [
            r for r in filtered_records
            if r.city and r.city.lower() == city_lower
        ]
        if not filtered_records:
            return None

    # 进一步筛选：县（如果指定）
    if county:
        county_lower = county.lower()
        filtered_records = [
            r for r in filtered_records
            if r.county and r.county.lower() == county_lower
        ]
        if not filtered_records:
            return None

    # 计算核心指标（基于CSV中的vehicle_count字段）
    total_ev = sum(record.vehicle_count for record in filtered_records)
    # 计算该区域电动车占所在州总电动车的比例（替代原ev_ratio）
    state_total_ev = sum(record.vehicle_count for record in state_records)
    ev_ratio = round((total_ev / state_total_ev) * 100, 2) if state_total_ev > 0 else 0.0

    # 提取该区域的电力供应商（CSV中无充电站数量，作为替代参考）
    electric_utilities = {r.electric_utility for r in filtered_records if r.electric_utility}

    return {
        "state": state,
        "city": city,
        "county": county,
        "ev_count": total_ev,
        "ev_ratio": ev_ratio,  # 区域内电动车占该州总电动车的比例（%）
        "charging_stations": list(electric_utilities),  # 用电力供应商替代充电站数据
        "data_points": len(filtered_records)
    }