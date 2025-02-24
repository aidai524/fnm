from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from typing import Generator
from config.settings import DATABASE_URL, DATABASE_CONFIG

# 创建同步引擎
engine = create_engine(
    DATABASE_URL,
    **DATABASE_CONFIG
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类，用于声明模型
Base = declarative_base()

def get_db() -> Generator:
    """
    获取数据库会话的依赖函数
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 