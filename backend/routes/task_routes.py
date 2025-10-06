from fastapi import APIRouter, Path, HTTPException
from typing import Dict, Any
from backend.config.celery_config import app as celery_app

router = APIRouter(
    prefix="/api/tasks",
    tags=["异步任务"],
    responses={404: {"description": "任务未找到"}, 400: {"description": "无效的任务ID"}}
)

@router.get("/{task_id}", response_model=Dict[str, Any])
async def get_task_result(
    task_id: str = Path(..., 
                       description="Celery异步任务的唯一标识ID",
                       min_length=32,  # 通常Celery任务ID长度为36位左右，增加基本校验
                       max_length=40)
):
    """查询异步任务的执行状态和结果
    
    支持的任务状态：
    - pending: 任务等待执行
    - running: 任务正在执行
    - success: 任务执行成功（返回结果）
    - failure: 任务执行失败（返回错误信息）
    - revoked: 任务被取消
    - retry: 任务正在重试
    """
    try:
        task = celery_app.AsyncResult(task_id)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"无效的任务ID: {str(e)}"
        )

    # 统一返回结构处理
    response = {
        "success": True,
        "task_id": task_id,
        "status": task.state.lower()
    }

    if task.state == "PENDING":
        response["message"] = "任务已提交，等待执行中"
    elif task.state == "RUNNING":
        response["message"] = "任务正在执行中"
    elif task.state == "SUCCESS":
        response["message"] = "任务执行成功"
        response["result"] = task.result  # 仅成功状态返回结果
    elif task.state == "FAILURE":
        response["success"] = False
        response["message"] = f"任务执行失败: {str(task.result) if task.result else '未知错误'}"
    elif task.state == "REVOKED":
        response["success"] = False
        response["message"] = "任务已被取消"
    elif task.state == "RETRY":
        response["message"] = f"任务正在重试（第{task.request.retries + 1}次）"
    else:
        response["message"] = f"任务处于{task.state}状态"

    return response