"""
SSE连接相关路由
"""

import asyncio
from datetime import datetime

from fastapi import APIRouter, Query
from sse_starlette.sse import EventSourceResponse

from ..models import ApiResponse, SSEConnectionRequest
from ..sse import SSEMessage, sse_manager
from ..config import logger, SSE_CONFIG
from ..i18n import Language, get_message, get_success_message

router = APIRouter(prefix="/sse", tags=["sse"])


@router.post("/connect")
async def create_sse_connection(request: SSEConnectionRequest):
    """创建SSE连接"""
    connection_id = f"{request.user_id}_{datetime.now().timestamp()}"
    
    async def sse_stream():
        try:
            # 添加连接
            sse_manager.add_connection(connection_id, request.user_id)
            
            # 发送连接确认
            yield SSEMessage.format_message(
                data={
                    "type": "connected",
                    "connection_id": connection_id,
                    "user_id": request.user_id,
                    "timestamp": datetime.now().isoformat()
                },
                event="connected"
            )
            
            # 保持连接活跃，定期发送心跳
            while True:
                yield SSEMessage.heartbeat()
                sse_manager.update_heartbeat(connection_id)
                await asyncio.sleep(SSE_CONFIG["heartbeat_interval"])
                
        except asyncio.CancelledError:
            logger.info(f"SSE连接 {connection_id} 被取消")
        except Exception as e:
            logger.error(f"SSE连接错误: {e}")
            yield SSEMessage.error(f"连接错误: {str(e)}")
        finally:
            sse_manager.remove_connection(connection_id)
    
    return EventSourceResponse(sse_stream())


@router.get("/status/{user_id}")
async def get_sse_status(user_id: str, language: Language = Query(default=Language.ZH_CN, description="接口语言")):
    """获取用户的SSE连接状态"""
    connections = sse_manager.get_user_connections(user_id)
    return ApiResponse(
        success=True,
        message=get_success_message("sse_connection_status_retrieved", language),
        data={
            "user_id": user_id,
            "active_connections": len(connections),
            "connection_ids": connections,
            "total_connections": len(sse_manager.connections)
        }
    ) 