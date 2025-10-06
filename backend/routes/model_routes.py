from fastapi import APIRouter, Query, HTTPException
from backend.services.model_service import get_model_data, get_model_list  # 保留服务层调用（后续可迁移逻辑到EVDataQuery）
from backend.tasks.data_tasks import generate_detailed_report
from backend.config.database import EVDataQuery  # 引入CSV数据查询工具

# 定义路由前缀和标签
router = APIRouter(
    prefix="/api/models",
    tags=["车型数据"],
    responses={404: {"description": "未找到"}}
)

@router.get("/list")
async def get_available_models(
    brand: str = Query(None, description="品牌过滤（可选，如tesla）")
):
    """获取所有可用车型列表（支持品牌过滤，数据来自CSV）"""
    # 适配CSV查询工具：获取指定品牌的所有车型（去重排序）
    if brand:
        models = [{"brand": brand, "model": model} for model in EVDataQuery.get_brand_models(brand)]
    else:
        # 若需全品牌车型，可扩展EVDataQuery实现全品牌查询
        all_records = EVDataQuery._get_all_records()
        brand_model_set = {(r.make, r.model) for r in all_records if r.make and r.model}
        models = [{"brand": b, "model": m} for b, m in sorted(brand_model_set)]
    
    if not models:
        raise HTTPException(status_code=404, detail="未找到车型数据")
    return {"success": True, "data": models}

@router.get("/")
async def query_model(
    brand: str = Query(..., description="品牌（如tesla）"),
    model: str = Query(..., description="车型（如Model 3）")
):
    """查询特定车型的基础数据（数据来自CSV）"""
    # 从品牌记录中筛选匹配车型
    brand_records = EVDataQuery.get_by_brand(brand)
    target_record = next(
        (r for r in brand_records if r.model and r.model.lower() == model.lower()),
        None
    )
    
    if not target_record:
        raise HTTPException(status_code=404, detail="未找到该车型数据")
    
    # 构造返回数据（映射CSV字段）
    return {"success": True, "data": {
        "brand": target_record.make,
        "model": target_record.model,
        "model_year": target_record.model_year,
        "ev_type": target_record.ev_type,
        "electric_range": target_record.electric_range,
        "base_msrp": target_record.base_msrp,
        "cafv_eligibility": target_record.cafv_eligibility
    }}

@router.get("/detailed-report")
async def create_detailed_report(
    brand: str = Query(..., description="品牌"),
    model: str = Query(..., description="车型")
):
    """提交详细报告生成任务（异步，基于CSV数据）"""
    # 验证车型是否存在（使用CSV查询工具）
    brand_records = EVDataQuery.get_by_brand(brand)
    model_exists = any(
        r.model and r.model.lower() == model.lower() 
        for r in brand_records
    )
    
    if not model_exists:
        raise HTTPException(status_code=404, detail="未找到该车型数据，无法生成报告")
    
    # 提交Celery任务（传递品牌和车型）
    task = generate_detailed_report.delay(brand, model)
    return {
        "success": True,
        "task_id": task.id,
        "message": "详细报告生成任务已提交，正在处理中（基于CSV数据）"
    }