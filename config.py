"""
配置文件 - 从环境变量读取配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).parent

# 数据目录
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
DATA_DIR.mkdir(exist_ok=True)

# Streamlit 配置
STREAMLIT_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
STREAMLIT_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")

# 存储配置
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(50 * 1024 * 1024)))  # 50MB
MAX_NODES_PER_FILE = int(os.getenv("MAX_NODES_PER_FILE", "10000"))

# 应用配置
APP_NAME = os.getenv("APP_NAME", "原神知识图谱管理系统")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = Path(os.getenv("LOG_FILE", "logs/app.log"))
LOG_FILE.parent.mkdir(exist_ok=True)

# 创建必要的目录
(DATA_DIR / "backups").mkdir(exist_ok=True)
(DATA_DIR / "parts").mkdir(exist_ok=True)
