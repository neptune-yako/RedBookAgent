"""
基础路由
"""

from fastapi import APIRouter

from ..models import ApiResponse
from ..services import agent_service, session_service
from ..config import APP_CONFIG, API_ENDPOINTS, SSE_FEATURES

router = APIRouter()


@router.get("/", response_model=ApiResponse)
async def root():
    """API根路径"""
    return ApiResponse(
        success=True,
        message="小红书文案生成智能体 API 服务运行中",
        data={
            "version": APP_CONFIG["version"],
            "status": "running",
            "agent_ready": agent_service.agent is not None,
            "endpoints": API_ENDPOINTS,
            "sse_features": SSE_FEATURES
        }
    )


@router.get("/health", response_model=ApiResponse)
async def health_check():
    """健康检查"""
    agent = agent_service.check_ready()
    agent_status = agent.check_setup()
    
    return ApiResponse(
        success=True,
        message="服务健康",
        data={
            "agent_ready": agent_status,
            "active_sessions": len(session_service.user_sessions),
            "uptime": "运行中"
        }
    ) 