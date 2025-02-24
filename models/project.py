from sqlalchemy import Column, Integer, String, DECIMAL, BigInteger, Boolean, DateTime, Text, func, case
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from config.database import Base
from typing import List, Optional
from sqlalchemy.orm import Session
import math
import random
import logging

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
        1. 平台基础权重：sexy平台项目获得最高权重(100000)，pump平台项目获得较低权重(100)
        2. 时间权重：越新的项目权重越高，使用时间衰减因子
        3. 活跃度权重：综合考虑分享数、点赞数、launched后点赞数和评论数
        4. 随机因子：在最终分数上增加少量随机波动，避免排序过于固定
        """
        
        try:
            # 构建权重计算表达式
            platform_weight = case(
                (cls.dapp == 'sexy', 100000),  # 极高权重确保优先显示
                (cls.dapp == 'pump', 100),
                else_=0
            ).label('platform_weight')
            
            # 时间权重（基于创建时间）- 简化计算
            time_weight = (
                (func.unix_timestamp(cls.created_at) / 86400) * 
                func.exp(-0.05 * func.datediff(func.now(), cls.created_at))
            ).label('time_weight')
            
            # 活跃度权重 - 简化计算
            activity_weight = (
                func.log(1 + cls.share_num) * 5 +
                func.log(1 + cls.like) * 3 +
                func.log(1 + cls.launched_like) +
                func.log(1 + cls.comment)
            ).label('activity_weight')
            
            # 计算分页
            offset = (page - 1) * per_page
            
            # 构建查询
            query = db.query(cls)
            
            # 添加状态过滤
            if status is not None:
                query = query.filter(cls.status == status)
            
            # 添加排序条件
            query = query.order_by(
                platform_weight.desc(),
                time_weight.desc(),
                activity_weight.desc()
            )
            
            # 执行查询
            return query.offset(offset).limit(per_page).all()
            
        except Exception as e:
            logging.error(f"查询加权项目时出错: {str(e)}")
            raise

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