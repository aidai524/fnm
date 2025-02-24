import os
from sqlalchemy import create_engine, text
import logging
import urllib.parse
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_db_connection():
    """获取数据库连接"""
    user = os.getenv("DB_USER")
    password = urllib.parse.quote_plus(os.getenv("DB_PASSWORD", ""))
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "3306")
    database = os.getenv("DB_NAME")
    
    connection_str = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    return create_engine(connection_str)

def check_platform_distribution():
    """检查平台数据分布情况"""
    engine = get_db_connection()
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT DApp as platform, COUNT(*) as count 
                FROM project 
                GROUP BY DApp 
                ORDER BY count DESC
            """))
            
            print("\n平台数据分布情况：")
            print("=" * 40)
            print(f"{'平台':<15} {'数量':<10}")
            print("-" * 40)
            
            for row in result:
                print(f"{row.platform:<15} {row.count:<10}")
                
            print("=" * 40)
            
    except Exception as e:
        logging.error(f"查询数据时出错: {str(e)}")
        raise

if __name__ == "__main__":
    check_platform_distribution() 