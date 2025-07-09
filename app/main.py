from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Database
from app.routes.vehicle import router as vehicle_router

# 启动时初始化数据库连接
async def lifespan(app: FastAPI):
    Database.initialize()
    yield

app = FastAPI(title="Vehicle Information API", lifespan=lifespan)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(vehicle_router)

# 根路由
@app.get("/")
def read_root():
    return {"message": "欢迎使用车辆信息查询API，请访问/docs查看文档"}

# 健康检查路由
@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}