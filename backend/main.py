from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import logging
from backend.routes import model_routes, region_routes, task_routes
from backend.config.database import init_ev_data
import uvicorn

# 1. 初始化FastAPI应用
app = FastAPI(
    title="美国电动汽车数据分析API",
    description="提供电动汽车品牌、车型及区域数据查询接口，支持异步任务处理，基于CSV数据驱动",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 2. 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("ev_data_api")

# 3. 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. 挂载前端静态文件（修复路径解析）
# 基于当前文件绝对路径计算：main.py -> backend目录 -> 项目根目录 -> frontend目录
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if not frontend_dir.exists():
    logger.warning(f"前端目录 {frontend_dir.resolve()} 不存在，静态文件服务已禁用")
else:
    app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")
    logger.info(f"已挂载前端静态文件目录：{frontend_dir.resolve()}")

# 5. 注册路由
app.include_router(model_routes.router)
app.include_router(region_routes.router)
app.include_router(task_routes.router)
logger.info("路由模块注册完成")

# 6. 初始化CSV数据（启动时加载）
try:
    init_ev_data()
    logger.info("CSV数据初始化成功，服务可正常提供数据查询")
except Exception as e:
    logger.error(f"CSV数据初始化失败：{str(e)}", exc_info=True)

# 7. 根路径接口
@app.get("/", response_class=HTMLResponse, tags=["首页"])
async def read_root():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>EV Data API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                a { color: #007bff; text-decoration: none; }
                a:hover { text-decoration: underline; }
                .status { margin: 15px 0; padding: 10px; border-radius: 4px; }
                .success { background-color: #d4edda; color: #155724; }
                .warning { background-color: #fff3cd; color: #856404; }
            </style>
        </head>
        <body>
            <h1>美国电动汽车数据分析API服务</h1>
            <div class="status success">服务运行中</div>
            <p>前端页面: <a href="/frontend/01.html">/frontend/01.html</a>（若前端目录存在）</p>
            <p>Swagger文档: <a href="/docs">/docs</a>（推荐开发调试使用）</p>
            <p>ReDoc文档: <a href="/redoc">/redoc</a>（API文档另一种格式）</p>
        </body>
    </html>
    """

# 8. 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail} | 路径: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "error_code": exc.status_code, "path": str(request.url.path)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"未捕获异常: {str(exc)} | 路径: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误，请稍后重试",
            "error_code": 500,
            "path": str(request.url.path)
        }
    )

# 9. 服务启动入口
if __name__ == "__main__":
    logger.info("启动开发环境服务...")
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        reload_dirs=["backend", "../frontend"]
    )