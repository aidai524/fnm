from fastapi import FastAPI
from routes import project
from config.database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="Project Ranking API",
    description="项目排序API，实现基于多维度权重的智能排序",
    version="1.0.0"
)

# 注册路由
app.include_router(project.router)

@app.get("/")
async def root():
    return {"message": "Project Ranking API is running"} 