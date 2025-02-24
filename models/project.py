from sqlalchemy import Column, Integer, String, DECIMAL, BigInteger, Boolean, DateTime, Text, func, case
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from config.database import Base
from typing import List, Optional
from sqlalchemy.orm import Session
import math
import random

class Project(Base):
    __tablename__ = 'project'
    
    # 基础字段
    id = Column(BigInteger, primary_key=True)
    dapp = Column(String(64), nullable=False, default='sexy', name='DApp')
    time = Column(BigInteger, nullable=False, default=0)
    share_num = Column(BigInteger, nullable=False, default=0)
    like = Column(BigInteger, nullable=False, default=0, name='like')
    launched_like = Column(BigInteger, nullable=False, default=0)
    comment = Column(BigInteger, nullable=False, default=0)
    status = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_weighted_projects(cls, 
                            db: Session, 
                            page: int = 1, 
                            per_page: int = 20,
                            status: Optional[int] = None) -> List["Project"]:
        """
        获取加权排序的项目列表
        
        排序算法说明：
        1. 平台权重：sexy平台项目获得最高权重(100000)，pump平台项目获得较低权重(100)
        2. 时间权重：越新的项目权重越高，使用时间衰减因子
        3. 活跃度权重：综合考虑分享数、点赞数、launched后点赞数和评论数
        4. 随机因子：在最终分数上增加少量随机波动，避免排序过于固定
        
        完整的SQL语句解释：
        WITH project_scores AS (
            SELECT *,
                -- 基础平台权重
                CASE 
                    WHEN DApp = 'sexy' THEN 2000
                    WHEN DApp = 'pump' THEN 500
                    ELSE 0 
                END +
                -- 时间权重（使用指数衰减）
                (UNIX_TIMESTAMP(created_at) / 86400) * 200 * EXP(-0.05 * DATEDIFF(NOW(), created_at)) +
                -- 分享权重（使用对数缩放）
                (LOG(1 + share_num) * 50) +
                -- 点赞权重
                (LOG(1 + `like`) * 30) +
                -- launched后点赞权重
                (LOG(1 + launched_like) * 10) +
                -- 评论权重
                (LOG(1 + comment) * 10) +
                -- 随机因子（增加5%随机波动）
                (RAND() * 0.05 * (
                    CASE 
                        WHEN DApp = 'sexy' THEN 2000
                        WHEN DApp = 'pump' THEN 500
                        ELSE 0 
                    END
                )) as weight_score
            FROM project
            WHERE status = :status  -- 可选的状态过滤
        )
        SELECT *
        FROM project_scores
        ORDER BY weight_score DESC
        LIMIT :offset, :limit
        """
        
        # 构建权重计算表达式
        platform_weight = case(
            (cls.dapp == 'sexy', 100000),  # 极高权重确保优先显示
            (cls.dapp == 'pump', 100),
            else_=0
        )
        
        # 时间权重（基于创建时间）
        time_weight = (
            func.unix_timestamp(cls.created_at) / 86400 * 10 * 
            func.exp(-0.05 * func.datediff(func.now(), cls.created_at))
        )
        
        # 活跃度权重
        activity_weight = (
            func.log(1 + cls.share_num) * 5 +  # 分享权重
            func.log(1 + cls.like) * 3 +       # 点赞权重
            func.log(1 + cls.launched_like) +   # launched后点赞权重
            func.log(1 + cls.comment)          # 评论权重
        )
        
        weight_score = (
            platform_weight +  # 平台基础权重
            time_weight +     # 时间权重
            activity_weight + # 活跃度权重
            func.rand() * 0.01 * platform_weight  # 极小的随机波动
        ).label('weight_score')
        
        # 构建基础查询
        query = db.query(cls, weight_score)

        # 添加状态过滤
        if status is not None:
            query = query.filter(cls.status == status)

        # 计算分页
        offset = (page - 1) * per_page
        
        # 执行查询
        results = query.order_by(weight_score.desc()).offset(offset).limit(per_page).all()
        
        # 提取Project对象（不包含weight_score）
        projects = [result[0] for result in results]
        
        return projects

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'id': self.id,
            'dapp': self.dapp,
            'time': self.time,
            'share_num': self.share_num,
            'like': self.like,
            'launched_like': self.launched_like,
            'comment': self.comment,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        } 