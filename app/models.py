"""
数据模型定义模块

该模块包含应用程序中使用的数据验证模型，基于Pydantic构建，
确保API请求和响应的数据格式正确。
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class PlateColor(str, Enum):
    """车牌颜色枚举类型"""
    BLUE = "蓝色"
    YELLOW = "黄色"
    BLACK = "黑色"
    WHITE = "白色"
    GREEN = "绿色"

class VehicleInfo(BaseModel):
    """
    车辆信息数据模型

    对应MongoDB中的Vehicle_License_Info集合，用于车辆信息的序列化和验证。
    所有字段均为可选，以适应部分查询场景。
    """
    license_plate_number: Optional[str] = Field(None, alias="号牌号码", description="车辆唯一登记编号，如'粤A12345'")
    registration_date: Optional[datetime] = Field(None, alias="登记日期", description="车辆登记日期")
    plate_color: Optional[PlateColor] = Field(None, alias="车牌颜色", description="车牌颜色")
    operation_scope: Optional[str] = Field(None, alias="经营范围", description="车辆经营范围，如'货运'、'客运'")
    tonnage: Optional[float] = Field(None, alias="吨(座)位", description="车辆核定载质量，单位为吨")
    vehicle_type: Optional[str] = Field(None, alias="车辆类型", description="车辆类型，如'小型汽车'、'大型货车'")