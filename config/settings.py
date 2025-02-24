from typing import Dict, Any
from pathlib import Path
import os
from dotenv import load_dotenv
import urllib.parse

# 加载环境变量
load_dotenv()

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 环境设置
ENV = os.getenv("ENV", "development")  # 默认为开发环境

# 数据库配置
DATABASE_CONFIGS = {
    "development": {
        "driver": "mysql+pymysql",
        "user": os.getenv("DB_USER"),
        "password": urllib.parse.quote_plus(os.getenv("DB_PASSWORD", "")),
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "database": os.getenv("DB_NAME"),
        "charset": "utf8mb4",
        "pool_size": int(os.getenv("DB_POOL_SIZE", "20")),
        "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "300")),
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "1800")),
        "pool_pre_ping": True,
        "connect_timeout": 60,
    },
    "production": {
        "driver": "mysql+pymysql",
        "user": os.getenv("DB_USER"),
        "password": urllib.parse.quote_plus(os.getenv("DB_PASSWORD", "")),
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "database": os.getenv("DB_NAME"),
        "charset": "utf8mb4",
        "pool_size": int(os.getenv("DB_POOL_SIZE", "20")),
        "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "300")),
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "1800")),
        "pool_pre_ping": True,
        "connect_timeout": 60,
    }
}

def get_database_url() -> str:
    """
    根据当前环境获取数据库连接URL
    """
    config = DATABASE_CONFIGS[ENV]
    return (
        f"{config['driver']}://{config['user']}:{config['password']}"
        f"@{config['host']}:{config['port']}/{config['database']}"
        f"?charset={config['charset']}"
        f"&connect_timeout={config['connect_timeout']}"
    )

def get_database_config() -> Dict[str, Any]:
    """
    获取数据库配置
    """
    config = DATABASE_CONFIGS[ENV]
    return {
        "pool_size": config["pool_size"],
        "max_overflow": 10,
        "pool_timeout": config["pool_timeout"],
        "pool_recycle": config["pool_recycle"],
        "pool_pre_ping": config["pool_pre_ping"],
        "echo": ENV == "development",  # 只在开发环境打印SQL语句
    }

# 导出配置
DATABASE_URL = get_database_url()
DATABASE_CONFIG = get_database_config() 