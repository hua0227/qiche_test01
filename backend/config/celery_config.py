import os
from celery import Celery
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置默认Django设置（Celery兼容）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.config.settings')  # 非必须，仅兼容用

# 初始化Celery应用
app = Celery('ev_data_platform')

# 移除循环引用的配置加载（修复点）
# app.config_from_object('backend.config.celery_config')

# 配置Broker（消息队列）和Backend（结果存储）
app.conf.broker_url = os.getenv('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//')  # RabbitMQ默认地址
app.conf.result_backend = os.getenv('CELERY_RESULT_BACKEND', 'rpc://')  # 结果存储

# 自动发现任务模块
app.autodiscover_tasks(['backend.tasks'])

# 任务序列化配置
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']