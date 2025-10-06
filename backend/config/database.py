import os
import pandas as pd
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict


# --------------------------
# 路径工具（获取根目录）
# --------------------------
def get_root_dir() -> str:
    """获取项目根目录（与backend同级的目录）"""
    current_file = os.path.abspath(__file__)
    # 向上跳转3级：config -> backend -> 根目录（根据实际目录结构调整层级）
    return os.path.dirname(os.path.dirname(os.path.dirname(current_file)))


def load_csv_data(file_name: Optional[str] = None) -> pd.DataFrame:
    """读取根目录下的CSV文件，处理编码和路径问题"""
    root_dir = get_root_dir()
    file_name = file_name or "Electric_Vehicle_Population_Datas.csv"
    file_path = os.path.join(root_dir, file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"根目录下未找到文件：{file_path}")
    if not file_path.endswith(".csv"):
        raise ValueError("仅支持CSV文件格式")

    # 尝试多种编码兼容不同系统的CSV文件
    encodings = ["utf-8", "gbk", "latin-1"]
    for encoding in encodings:
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("无法解析CSV文件（尝试多种编码失败）")


# --------------------------
# 数据模型类（与数据库/CSV字段完全对应）
# --------------------------
@dataclass
class ElectricVehicleRecord:
    """电动汽车数据记录模型（严格对应CSV/数据库字段）"""
    # 自增ID（非CSV原始列，数据库用）
    id: Optional[int] = None
    # VIN前10位（对应CSV"VIN (1-10)"列）
    vin_1_to_10: Optional[str] = None
    # 县（对应CSV"County"列）
    county: Optional[str] = None
    # 城市（对应CSV"City"列）
    city: Optional[str] = None
    # 州（对应CSV"State"列，非空）
    state: str = ""
    # 车型年份（对应CSV"Model Year"列）
    model_year: Optional[int] = None
    # 品牌（对应CSV"Make"列）
    make: Optional[str] = None
    # 车型（对应CSV"Model"列）
    model: Optional[str] = None
    # 电动车类型（对应CSV"Electric Vehicle Type"列）
    ev_type: Optional[str] = None
    # CAFV资格（对应CSV"Clean Alternative Fuel Vehicle (CAFV) Eligibility"列）
    cafv_eligibility: Optional[str] = None
    # 续航里程（对应CSV"Electric Range"列）
    electric_range: Optional[float] = None
    # 基础指导价（对应CSV"Base MSRP"列）
    base_msrp: Optional[float] = None
    # 电力供应商（对应CSV"Electric Utility"列）
    electric_utility: Optional[str] = None
    # 车辆数量（默认1，若CSV有则优先使用）
    vehicle_count: int = 1


# --------------------------
# CSV数据加载工具（带缓存和完整映射）
# --------------------------
class EVDataLoader:
    """加载CSV数据并完整映射到模型类，处理类型转换和缺失值"""
    _cache: Dict[str, pd.DataFrame] = {}  # 缓存CSV数据（key为文件名）

    @classmethod
    def load_data(cls, file_name: Optional[str] = None, force_reload: bool = False) -> pd.DataFrame:
        """加载CSV数据（带缓存，避免重复IO）"""
        file_name = file_name or "Electric_Vehicle_Population_Datas.csv"
        if file_name in cls._cache and not force_reload:
            return cls._cache[file_name]
        
        # 加载并缓存数据
        df = load_csv_data(file_name)
        cls._cache[file_name] = df
        return df

    @classmethod
    def get_records(cls, file_name: Optional[str] = None) -> List[ElectricVehicleRecord]:
        """将CSV数据转换为模型列表，处理类型转换和缺失值"""
        df = cls.load_data(file_name)
        records = []
        
        for idx, row in df.iterrows():
            # 处理数值类型转换（避免字符串转数值失败）
            model_year = row.get("Model Year")
            try:
                model_year = int(model_year) if pd.notna(model_year) else None
            except (ValueError, TypeError):
                model_year = None

            electric_range = row.get("Electric Range")
            try:
                electric_range = float(electric_range) if pd.notna(electric_range) else None
            except (ValueError, TypeError):
                electric_range = None

            base_msrp = row.get("Base MSRP")
            try:
                base_msrp = float(base_msrp) if pd.notna(base_msrp) else None
            except (ValueError, TypeError):
                base_msrp = None

            # 处理车辆数量（优先使用CSV中的列，无则默认1）
            vehicle_count = row.get("Vehicle Count")  # 假设CSV可能有该列
            try:
                vehicle_count = int(vehicle_count) if pd.notna(vehicle_count) else 1
            except (ValueError, TypeError):
                vehicle_count = 1

            # 构建模型实例（完整映射所有字段）
            records.append(
                ElectricVehicleRecord(
                    id=idx + 1,  # 自动生成ID（从1开始）
                    vin_1_to_10=str(row.get("VIN (1-10)", "")).strip() or None,
                    county=str(row.get("County", "")).strip() or None,
                    city=str(row.get("City", "")).strip() or None,
                    state=str(row.get("State", "")).strip() or "未知",  # 确保非空（避免空字符串）
                    model_year=model_year,
                    make=str(row.get("Make", "")).strip() or None,
                    model=str(row.get("Model", "")).strip() or None,
                    ev_type=str(row.get("Electric Vehicle Type", "")).strip() or None,
                    cafv_eligibility=str(row.get("Clean Alternative Fuel Vehicle (CAFV) Eligibility", "")).strip() or None,
                    electric_range=electric_range,
                    base_msrp=base_msrp,
                    electric_utility=str(row.get("Electric Utility", "")).strip() or None,
                    vehicle_count=vehicle_count
                )
            )
        return records

    @classmethod
    def clear_cache(cls) -> None:
        """清空缓存（CSV文件更新后调用）"""
        cls._cache = {}


# --------------------------
# 数据查询工具（优化查询效率）
# --------------------------
class EVDataQuery:
    """封装CSV数据查询方法，增加缓存和过滤优化"""
    _record_cache: Optional[List[ElectricVehicleRecord]] = None  # 缓存记录列表

    @classmethod
    def _get_all_records(cls, file_name: Optional[str] = None) -> List[ElectricVehicleRecord]:
        """获取所有记录（带本地缓存，减少重复转换）"""
        if cls._record_cache is None:
            cls._record_cache = EVDataLoader.get_records(file_name)
        return cls._record_cache

    @staticmethod
    def clear_query_cache() -> None:
        """清空查询缓存（数据更新后调用）"""
        EVDataQuery._record_cache = None

    @classmethod
    def get_by_brand(cls, brand: str) -> List[ElectricVehicleRecord]:
        """根据品牌查询（不区分大小写）"""
        brand_lower = brand.lower()
        return [
            record for record in cls._get_all_records()
            if record.make and record.make.lower() == brand_lower
        ]

    @classmethod
    def get_by_state(cls, state: str) -> List[ElectricVehicleRecord]:
        """根据州查询（不区分大小写）"""
        state_lower = state.lower()
        return [
            record for record in cls._get_all_records()
            if record.state and record.state.lower() == state_lower
        ]

    @classmethod
    def get_brand_models(cls, brand: str) -> List[str]:
        """查询指定品牌的所有车型（去重，排序）"""
        brand_records = cls.get_by_brand(brand)
        models = {record.model for record in brand_records if record.model}
        return sorted(models)  # 排序后返回，更友好

    @classmethod
    def get_state_ev_count(cls, state: str) -> int:
        """统计指定州的电动汽车总数（基于vehicle_count）"""
        state_records = cls.get_by_state(state)
        return sum(record.vehicle_count for record in state_records)

    @classmethod
    def get_by_ev_type(cls, ev_type: str) -> List[ElectricVehicleRecord]:
        """新增：根据电动车类型查询（扩展查询能力）"""
        ev_type_lower = ev_type.lower()
        return [
            record for record in cls._get_all_records()
            if record.ev_type and record.ev_type.lower() == ev_type_lower
        ]


# --------------------------
# 初始化函数（预加载数据，带错误处理）
# --------------------------
def init_ev_data() -> None:
    """初始化电动汽车数据，预加载并验证数据完整性"""
    try:
        # 预加载数据并缓存
        EVDataLoader.load_data()
        # 触发一次记录转换，验证映射是否正确
        sample_records = EVDataLoader.get_records()[:5]  # 只验证前5条
        print(f"CSV数据初始化成功，共加载 {len(EVDataLoader.load_data())} 行数据")
        print(f"示例数据：{sample_records[0] if sample_records else '无数据'}")
    except Exception as e:
        print(f"CSV数据初始化失败：{str(e)}")
        # 初始化失败时清空缓存，避免后续调用出错
        EVDataLoader.clear_cache()
        EVDataQuery.clear_query_cache()


# --------------------------
# 使用示例
# --------------------------
if __name__ == "__main__":
    init_ev_data()

    # 示例1：查询特斯拉的所有车型
    tesla_models = EVDataQuery.get_brand_models("Tesla")
    print(f"\n特斯拉车型列表：{tesla_models}")

    # 示例2：统计华盛顿州的电动汽车总数
    wa_count = EVDataQuery.get_state_ev_count("WA")
    print(f"华盛顿州电动汽车总数：{wa_count}")

    # 示例3：查询纯电动车类型的记录
    bev_records = EVDataQuery.get_by_ev_type("Battery Electric Vehicle (BEV)")
    print(f"纯电动车记录数：{len(bev_records)}")