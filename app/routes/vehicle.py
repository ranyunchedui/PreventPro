"""车辆信息API路由模块

提供车辆信息查询、分页、排序和统计功能，聚合多个集合数据
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any, List
from app.database import Database
from app.models import VehicleInfo
from app.utils.query_utils import get_common_vehicle_pipeline

# 创建车辆信息API路由，前缀/vehicles，标签vehicles用于API文档分组
router = APIRouter(prefix="/vehicles", tags=["vehicles"])

# 获取数据库单例实例
# 使用Database类的静态方法get_db()确保全局只有一个数据库连接
db = Database.get_db()

@router.get("/", response_model=Dict[str, Any])
def get_vehicles(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=100, description="每页条数"),
    sort_by: str = Query("登记日期", description="排序字段"),
    sort_order: int = Query(-1, description="排序方向，1为升序，-1为降序")
):
    """获取车辆信息列表（支持分页、排序）

    聚合查询多个集合数据，返回格式化的车辆信息列表及分页 metadata

    Args:
        page: 页码，默认为1，最小值为1
        limit: 每页记录数，默认为10，取值范围1-100
        sort_by: 排序字段，默认为"登记日期"
        sort_order: 排序方向，1为升序，-1为降序（默认）

    Returns:
        Dict[str, Any]: 包含车辆数据和分页信息的字典
        - data: 车辆信息列表
        - pagination: 分页元数据（page, limit, total, pages）

    Raises:
        HTTPException: 500错误，当数据库查询失败时抛出
    """
    try:
        # 获取公共聚合管道并添加分页和排序
        pipeline: List[Dict[str, Any]] = get_common_vehicle_pipeline()
        # 添加排序阶段：根据请求参数对结果进行排序
        pipeline.append({"$sort": {sort_by: sort_order}})
        # 计算分页偏移量：(页码-1)*每页条数
        skip = (page - 1) * limit
        # 添加分页跳过阶段
        pipeline.append({"$skip": skip})
        # 添加分页限制阶段
        pipeline.append({"$limit": limit})

        # 执行聚合查询并获取结果列表
        # 查询车辆牌照信息集合，执行聚合管道
        if db is None:
            raise HTTPException(status_code=500, detail="数据库连接未初始化")
        vehicles = list(db["Vehicle_License_Info"].aggregate(pipeline))
        total = 0

        return {
            "data": vehicles,  # 车辆信息列表
            "pagination": {
                "page": page,       # 当前页码
                "limit": limit,     # 每页条数
                "total": total,     # 总记录数
                "pages": (total + limit - 1) // limit  # 总页数，向上取整公式
            }
        }
    except Exception as e:
        # 处理数据库查询异常，返回500错误及详细信息
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")