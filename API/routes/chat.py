"""
聊天相关路由
"""

import asyncio
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from sse_starlette.sse import EventSourceResponse

from ..models import ApiResponse, ChatRequest
from ..services import agent_service
from ..sse import SSEMessage, sse_manager
from ..config import logger
from ..i18n import get_message, get_error_message, get_success_message

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ApiResponse)
async def chat(request: ChatRequest):
    """对话聊天"""
    try:
        agent = agent_service.check_ready()
        
        response = agent.chat(request.message, request.language)
        
        return ApiResponse(
            success=True,
            message=get_success_message("chat_success", request.language),
            data={"response": response}
        )
        
    except Exception as e:
        logger.error(f"对话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/async", response_model=ApiResponse)
async def chat_async(request: ChatRequest):
    """异步对话聊天（智能体线程池）"""
    try:
        agent = agent_service.check_ready()
        
        def chat_task():
            """在智能体工作线程中执行的聊天任务"""
            response = agent.chat(request.message, request.language)
            return {"response": response}
        
        # 提交到智能体专用线程池
        task_id = agent_service.submit_agent_task(
            task_type="chat",
            user_id=request.user_id,
            task_func=chat_task,
            priority=1  # 聊天任务最高优先级
        )
        
        return ApiResponse(
            success=True,
            message=get_success_message("task_submitted", request.language),
            data={
                "task_id": task_id,
                "status": "pending",
                "message": get_message("chat_started", request.language),
                "pool": "agent"  # 标明使用的线程池
            }
        )
        
    except Exception as e:
        logger.error(f"提交聊天任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """流式对话聊天（SSE）- 直接执行"""
    try:
        agent = agent_service.check_ready()
        
        async def sse_chat_stream():
            try:
                connection_id = f"{request.user_id}_chat_{datetime.now().timestamp()}"
                sse_manager.add_connection(connection_id, request.user_id)
                
                # 发送开始状态
                yield SSEMessage.status("started", get_message("chat_started", request.language))
                
                response_content = ""
                chunk_count = 0
                
                # 直接传递enable_thinking参数给智能体，不修改全局状态
                for chunk in agent.chat_stream(request.message, request.language, enable_thinking=request.enable_thinking):
                    if chunk:
                        response_content += chunk
                        chunk_count += 1
                        
                        # 发送内容块
                        yield SSEMessage.content_chunk(
                            chunk=chunk,
                            chunk_type="chat",
                            metadata={
                                "action": get_message("chat", request.language),
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
                    "action": get_message("chat", request.language),
                    "total_chunks": chunk_count,
                    "total_length": len(response_content)
                })
                
            except Exception as e:
                logger.error(f"对话过程中出错: {e}")
                yield SSEMessage.error(get_error_message("chat_failed", request.language, str(e)))
            finally:
                sse_manager.remove_connection(connection_id)
        
        return EventSourceResponse(sse_chat_stream())
        
    except Exception as e:
        logger.error(f"流式对话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream/async")
async def chat_stream_async(request: ChatRequest):
    """流式对话聊天（SSE + 线程池）- 在线程池中执行"""
    try:
        agent = agent_service.check_ready()
        
        def stream_chat_func():
            """在线程池中执行的流式聊天函数"""
            # 返回流式聊天生成器
            return agent.chat_stream(request.message, request.language, enable_thinking=request.enable_thinking)
        
        # 提交流式任务到智能体线程池
        task_id = agent_service.submit_stream_task(
            task_type="chat_stream",
            user_id=request.user_id,
            generator_func=stream_chat_func,
            priority=1  # 聊天流式任务高优先级
        )
        
        # 使用任务结果生成SSE流
        async def sse_task_stream():
            async for message in stream_service.generate_with_sse_from_task(
                task_id, 
                request.user_id, 
                get_message("chat", request.language)
            ):
                yield message
        
        return EventSourceResponse(sse_task_stream())
        
    except Exception as e:
        logger.error(f"提交流式聊天任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=ApiResponse)
async def batch_chat(
    messages: list[str],
    user_id: str,
    language: str = Query("zh-CN", description="语言代码")
):
    """批量对话（智能体线程池）"""
    try:
        agent = agent_service.check_ready()
        
        if len(messages) > 5:  # 限制批量聊天数量
            raise HTTPException(
                status_code=400,
                detail=get_error_message("batch_chat_too_large", language, str(len(messages)))
            )
        
        task_ids = []
        
        for i, message in enumerate(messages):
            def chat_task(msg=message, index=i):
                """批量聊天任务"""
                response = agent.chat(msg, language)
                return {
                    "message": msg,
                    "response": response,
                    "message_index": index
                }
            
            # 提交任务到智能体线程池
            task_id = agent_service.submit_agent_task(
                task_type="batch_chat",
                user_id=user_id,
                task_func=chat_task,
                priority=2  # 批量聊天中等优先级
            )
            task_ids.append(task_id)
        
        return ApiResponse(
            success=True,
            message=get_success_message("batch_tasks_submitted", language),
            data={
                "task_ids": task_ids,
                "total_tasks": len(task_ids),
                "message": get_message("batch_chat_started", language),
                "pool": "agent"  # 标明使用的线程池
            }
        )
        
    except Exception as e:
        logger.error(f"批量对话任务提交失败: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 