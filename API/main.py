"""
小红书文案生成智能体 - FastAPI主应用
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import APP_CONFIG, CORS_CONFIG, logger
from .services import agent_service
from .sse import heartbeat_task

# 导入所有路由
from .routes import base, content, chat, feedback, sse, history


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    try:
        logger.info("正在启动应用...")
        
        # 初始化智能体
        await agent_service.initialize()
        
        # 启动心跳任务
        asyncio.create_task(heartbeat_task())
        
        logger.info("应用启动完成")
        
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
    
    yield
    
    logger.info("正在关闭应用...")


# 创建FastAPI应用
app = FastAPI(
    title=APP_CONFIG["title"],
    description=APP_CONFIG["description"],
    version=APP_CONFIG["version"],
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    **CORS_CONFIG
)

# 注册路由
app.include_router(base.router)
app.include_router(content.router)
app.include_router(chat.router)
app.include_router(feedback.router)
app.include_router(sse.router)
app.include_router(history.router) 