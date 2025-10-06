from backend.config.database import EVDataQuery, ElectricVehicleRecord
from typing import List, Dict, Optional
import numpy as np

# 移除Excel加载数据库的函数（不再依赖SQL数据库）


def get_model_list(brand: str = None) -> List[Dict[str, str]]:
    """获取车型列表（支持品牌过滤，数据来自CSV）"""
    all_records = EVDataQuery._get_all_records()
    
    # 提取所有品牌-车型组合（去重）
    model_set = set()
    for record in all_records:
        if record.make and record.model:
            # 统一转为小写避免重复（如Tesla和tesla视为同一品牌）
            brand_key = record.make.lower()
            model_key = record.model.lower()
            model_set.add((brand_key, record.make, record.model))  # 保留原始大小写
    
    # 过滤品牌（如果指定）
    filtered = []
    for brand_key, original_brand, original_model in model_set:
        if not brand or brand.lower() in brand_key:
            filtered.append({
                "brand": original_brand,
                "model": original_model
            })
    
    # 按品牌和车型排序
    filtered.sort(key=lambda x: (x["brand"].lower(), x["model"].lower()))
    return filtered if filtered else []


def get_model_data(brand: str, model: str) -> Optional[Dict]:
    """获取特定车型的详细数据（数据来自CSV）"""
    brand_lower = brand.lower()
    model_lower = model.lower()
    
    # 筛选匹配的记录
    matched_records = [
        record for record in EVDataQuery._get_all_records()
        if record.make and record.model 
        and record.make.lower() == brand_lower 
        and record.model.lower() == model_lower
    ]
    
    if not matched_records:
        return None
    
    # 计算基础数据（取多数值的平均或众数）
    first_record = matched_records[0]
    avg_range = np.mean([r.electric_range for r in matched_records if r.electric_range])
    avg_price = np.mean([r.base_msrp for r in matched_records if r.base_msrp])
    model_years = list({r.model_year for r in matched_records if r.model_year})
    ev_types = list({r.ev_type for r in matched_records if r.ev_type})
    
    # 统计区域分布（基于车辆数量）
    region_counts = {}
    total_vehicles = sum(r.vehicle_count for r in matched_records)
    for record in matched_records:
        if record.state:
            region_counts[record.state] = region_counts.get(record.state, 0) + record.vehicle_count
    
    # 转换为百分比
    region_distribution = {
        state: round((count / total_vehicles) * 100, 1)
        for state, count in region_counts.items()
    }
    
    # 补充热门区域（取占比最高的）
    popular_region = max(region_distribution.items(), key=lambda x: x[1])[0] if region_distribution else None
    
    return {
        "brand": first_record.make,
        "model": first_record.model,
        "range": round(avg_range, 1) if not np.isnan(avg_range) else None,
        "price": round(avg_price, 2) if not np.isnan(avg_price) else None,
        "market_share": round((total_vehicles / sum(r.vehicle_count for r in EVDataQuery._get_all_records())) * 100, 2),
        "popular_region": popular_region,
        "region_distribution": region_distribution,
        "model_years": sorted(model_years),
        "ev_types": ev_types,
        "total_vehicles": total_vehicles
    }