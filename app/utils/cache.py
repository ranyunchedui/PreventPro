import redis
import json
from dotenv import load_dotenv
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

class RedisCache:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                cls._instance.client = redis.Redis(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", 6379)),
                    db=int(os.getenv("REDIS_DB", 0)),
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                # 测试连接
                cls._instance.client.ping()
                logger.info("Redis连接成功建立")
            except redis.RedisError as e:
                logger.error(f"Redis连接失败: {str(e)}")
                cls._instance = None
        return cls._instance
    
    def get(self, key):
        try:
            return self.client.get(key)
        except redis.RedisError as e:
            logger.error(f"Redis读取错误: {str(e)}")
            return None
    
    def setex(self, key, expiry, value):
        try:
            return self.client.setex(key, expiry, value)
        except redis.RedisError as e:
            logger.error(f"Redis写入错误: {str(e)}")
            return False
    
    def delete(self, key):
        try:
            return self.client.delete(key)
        except redis.RedisError as e:
            logger.error(f"Redis删除错误: {str(e)}")
            return False

# 创建缓存实例
def get_cache():
    return RedisCache()