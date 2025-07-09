import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import os
from fastapi import HTTPException

load_dotenv()

class Database:
    _client = None
    _db = None

    @classmethod
    def initialize(cls):
        if cls._client is None:
            max_retries = 3
            retry_delay = 2
            for attempt in range(max_retries):
                try:
                    cls._client = MongoClient(os.getenv("MONGODB_URI"))
                    cls._client.admin.command("ping")
                    cls._db = cls._client["vehicle_info"]
                    print("MongoDB连接成功")
                    return
                except ConnectionFailure:
                    if attempt < max_retries - 1:
                        print(f"MongoDB连接失败，第 {attempt + 1} 次重试，等待 {retry_delay} 秒...")
                        time.sleep(retry_delay)
                    else:
                        print("MongoDB连接失败，达到最大重试次数")
                        raise HTTPException(status_code=500, detail="数据库连接失败")

    @classmethod
    def get_db(cls):
        if cls._db is None:
            cls.initialize()
        return cls._db