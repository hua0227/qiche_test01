# 基础镜像：选择稳定的 Python 版本（如 3.9）
FROM python:3.9-slim

# 设置工作目录（容器内的代码存放路径）
WORKDIR /app

# 复制依赖清单并安装（利用 Docker 缓存，加速后续构建）
COPY requirements.txt .
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
    
# 复制后端所有代码到容器内的 /app 目录
COPY . .

# 暴露后端服务端口（与代码中启动的端口一致，如 FastAPI 常用 8000）
EXPOSE 8000

# 启动命令：用 Uvicorn 运行 main.py 中的 app（假设 main.py 是入口，定义了 app = FastAPI()）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]