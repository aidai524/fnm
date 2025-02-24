from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from config.database import get_db
from models.project import Project
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/projects", tags=["projects"])

class ProjectResponse(BaseModel):
    id: int
    dapp: str
    time: int
    share_num: int
    like: int
    launched_like: int
    comment: int
    status: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.get("/weighted", response_model=List[ProjectResponse])
async def get_weighted_projects(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[int] = Query(None, description="项目状态过滤"),
    db: Session = Depends(get_db)
):
    """
    获取加权排序的项目列表
    
    排序规则：
    1. 平台优先级：sexy > 其他 > pump
    2. 时间衰减：越新的项目权重越高
    3. 活跃度指标：分享数 > 点赞数 > launched后点赞数 = 评论数
    4. 随机因子：增加10%随机波动
    
    权重计算公式：
    - 平台基础分：sexy=1000, pump=-500, 其他=0
    - 时间权重：(创建时间戳/86400) * 100 * exp(-0.1 * 距今天数)
    - 分享权重：log(1 + 分享数) * 50
    - 点赞权重：log(1 + 点赞数) * 30
    - launched点赞权重：log(1 + launched点赞数) * 10
    - 评论权重：log(1 + 评论数) * 10
    - 随机波动：rand() * 0.1 * 平台基础分
    
    最终分数 = 平台基础分 + 时间权重 + 分享权重 + 点赞权重 + launched点赞权重 + 评论权重 + 随机波动
    """
    try:
        projects = Project.get_weighted_projects(
            db=db,
            page=page,
            per_page=per_page,
            status=status
        )
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 