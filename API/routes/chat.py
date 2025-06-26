"""
聊天相关路由
"""

import asyncio
from datetime import datetime

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from ..models import ApiResponse, ChatRequest
from ..services import agent_service
from ..sse import SSEMessage, sse_manager
from ..config import logger

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ApiResponse)
async def chat(request: ChatRequest):
    """对话聊天"""
    try:
        agent = agent_service.check_ready()
        
        response = agent.chat(request.message)
        
        return ApiResponse(
            success=True,
            message="对话成功",
            data={"response": response}
        )
        
    except Exception as e:
        logger.error(f"对话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """流式对话聊天（SSE）"""
    try:
        agent = agent_service.check_ready()
        
        async def sse_chat_stream():
            try:
                connection_id = f"{request.user_id}_chat_{datetime.now().timestamp()}"
                sse_manager.add_connection(connection_id, request.user_id)
                
                # 发送开始状态
                yield SSEMessage.status("started", "开始对话...")
                
                response_content = ""
                chunk_count = 0
                
                # 处理对话流
                for chunk in agent.chat_stream(request.message):
                    if chunk:
                        response_content += chunk
                        chunk_count += 1
                        
                        # 发送内容块
                        yield SSEMessage.content_chunk(
                            chunk=chunk,
                            chunk_type="chat",
                            metadata={
                                "action": "对话",
                                "chunk_count": chunk_count,
                                "total_length": len(response_content)
                            }
                        )
                        
                        # 更新心跳
                        sse_manager.update_heartbeat(connection_id)
                        await asyncio.sleep(0.01)
                
                # 发送完成状态
                yield SSEMessage.complete({
                    "response": response_content,
                    "action": "对话",
                    "total_chunks": chunk_count,
                    "total_length": len(response_content)
                })
                
            except Exception as e:
                logger.error(f"对话过程中出错: {e}")
                yield SSEMessage.error(f"对话失败: {str(e)}")
            finally:
                sse_manager.remove_connection(connection_id)
        
        return EventSourceResponse(sse_chat_stream())
        
    except Exception as e:
        logger.error(f"流式对话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 