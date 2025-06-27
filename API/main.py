"""
小红书文案生成智能体 - FastAPI主应用
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import APP_CONFIG, CORS_CONFIG, logger
from .services import agent_service, session_service
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
        
        # 启动定期清理任务
        async def cleanup_task():
            """定期清理任务"""
            while True:
                try:
                    await asyncio.sleep(3600)  # 每小时执行一次
                    
                    # 清理旧任务记录（两个线程池）
                    agent_service.cleanup_old_tasks(max_age_hours=24)
                    
                    # 清理不活跃的用户会话
                    session_service.cleanup_inactive_sessions(max_inactive_hours=24)
                    
                    logger.info("定期清理任务完成")
                    
                except Exception as e:
                    logger.error(f"定期清理任务失败: {e}")
        
        asyncio.create_task(cleanup_task())
        
        logger.info("应用启动完成")
        logger.info(f"智能体线程池: 3工作线程, 20队列容量")
        logger.info(f"系统线程池: 5工作线程, 50队列容量")
        
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
    
    yield
    
    logger.info("正在关闭应用...")
    
    try:
        # 关闭所有线程池
        agent_service.shutdown()
        logger.info("所有线程池已关闭")
        
        # 清理会话数据
        session_service.user_sessions.clear()
        logger.info("会话数据已清理")
        
    except Exception as e:
        logger.error(f"应用关闭过程中出错: {e}")
    
    logger.info("应用已关闭")


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
from .routes import i18n
app.include_router(i18n.router) 