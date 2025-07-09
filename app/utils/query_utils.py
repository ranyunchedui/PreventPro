from typing import List, Dict, Any
import logging

# 配置日志
logger = logging.getLogger(__name__)

def get_common_vehicle_pipeline() -> List[Dict[str, Any]]:
    """获取车辆信息查询的公共聚合管道

    该管道执行以下操作：
    1. 过滤存在号牌号码的文档
    2. 关联车辆登记信息( Vehicle_Registration_Info )
    3. 关联道路运输许可证信息( Road_Transport_License_Info )
    4. 合并并投影所需字段

    Returns:
        List[Dict[str, Any]]: MongoDB聚合管道

    Raises:
        ValueError: 当管道配置无效时
    """
    try:
        return [
            {"$match": {"号牌号码": {"$exists": True}}},

            {"$lookup": {
                "from": "Vehicle_Registration_Info",
                "localField": "车辆识别代号",
                "foreignField": "车辆识别代号/车架号",
                "as": "registration_info",
                "pipeline": [
                    {"$match": {"登记日期": {"$exists": True}}},
                    {"$project": {"登记日期": 1, "车牌颜色": 1, "_id": 0}}
                ]
            }},
            {"$unwind": {
                "path": "$registration_info",
                "preserveNullAndEmptyArrays": True
            }},
            {"$lookup": {
                "from": "Road_Transport_License_Info",
                "localField": "号牌号码",
                "foreignField": "车牌号码",
                "as": "transport_info",
                "pipeline": [
                    {"$match": {"吨(座)位": {"$exists": True}}},
                    {"$project": {"经营范围": 1, "吨(座)位": 1, "_id": 0}}
                ]
            }},
            {"$unwind": {
                "path": "$transport_info",
                "preserveNullAndEmptyArrays": True
            }},
            {"$match": {
                "$or": [
                    {"号牌号码": {"$ne": None}},
                    {"registration_info.登记日期": {"$ne": None}},
                    {"registration_info.车牌颜色": {"$ne": None}},
                    {"transport_info.经营范围": {"$ne": None}},
                    {"transport_info.吨(座)位": {"$ne": None}}
                ]
            }},
            {"$project": {
                "号牌号码": {"$ifNull": ["$号牌号码", None]},
                "登记日期": {"$ifNull": ["$registration_info.登记日期", None]},
                "车牌颜色": {"$ifNull": ["$registration_info.车牌颜色", None]},
                "经营范围": {"$ifNull": ["$transport_info.经营范围", None]},
                "吨(座)位": {"$ifNull": ["$transport_info.吨(座)位", None]},
                "_id": 0
            }}
        ]
    except Exception as e:
        logger.error(f"构建车辆查询管道失败: {str(e)}", exc_info=True)
        raise ValueError(f"查询管道配置错误: {str(e)}") from e