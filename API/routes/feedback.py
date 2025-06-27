"""
反馈相关路由
"""

import asyncio
from datetime import datetime

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from Agent.xiaohongshu_agent import ContentRequest

from ..models import ApiResponse, FeedbackRequest
from ..services import agent_service, session_service
from ..sse import SSEMessage, sse_manager
from ..config import logger
from ..i18n import get_message, get_error_message, get_success_message

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=ApiResponse)
async def handle_feedback(request: FeedbackRequest):
    """智能反馈回环处理"""
    try:
        agent = agent_service.check_ready()
        session = session_service.get_user_session(request.user_id)
        
        # 构造原始请求
        original_req = None
        if request.original_request:
            original_req = ContentRequest(
                category=agent_service.parse_content_category(request.original_request.category),
                topic=request.original_request.topic,
                tone=request.original_request.tone,
                length=request.original_request.length,
                keywords=request.original_request.keywords or [],
                target_audience=request.original_request.target_audience,
                special_requirements=request.original_request.special_requirements
            )
        
        # 处理反馈
        if request.feedback == "不满意":
            if original_req:
                result = agent.regenerate_with_improvements(original_req, request.content)
            else:
                result = agent.regenerate_from_content(request.content, request.language)
            action = get_message("regeneration", request.language)
        elif request.feedback in ["需要优化", "满意"]:
            result = agent.optimize_content(request.content)
            action = get_message("intelligent_optimization", request.language)
        else:
            return ApiResponse(
                success=True,
                message=get_success_message("feedback_processing_complete", request.language),
                data={"action": get_message("completion", request.language), "content": request.content}
            )
        
        if result["success"]:
            # 保存到历史
            session_service.add_content_to_history(request.user_id, result["content"], action)
            session["feedback_round"] = session.get("feedback_round", 0) + 1
            
            return ApiResponse(
                success=True,
                message=get_success_message("feedback_processing_complete", request.language),
                data={
                    "content": result["content"],
                    "action": action,
                    "version": session["current_version_index"] + 1,
                    "feedback_round": session["feedback_round"]
                }
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", get_error_message("feedback_processing_failed", request.language)))
            
    except Exception as e:
        logger.error(f"反馈处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def handle_feedback_stream(request: FeedbackRequest):
    """流式智能反馈回环处理（SSE）"""
    try:
        agent = agent_service.check_ready()
        session = session_service.get_user_session(request.user_id)
        
        async def sse_feedback_stream():
            try:
                connection_id = f"{request.user_id}_feedback_{datetime.now().timestamp()}"
                sse_manager.add_connection(connection_id, request.user_id)
                
                # 构造原始请求
                original_req = None
                if request.original_request:
                    original_req = ContentRequest(
                        category=agent_service.parse_content_category(request.original_request.category),
                        topic=request.original_request.topic,
                        tone=request.original_request.tone,
                        length=request.original_request.length,
                        keywords=request.original_request.keywords or [],
                        target_audience=request.original_request.target_audience,
                        special_requirements=request.original_request.special_requirements
                    )
                
                content = ""
                action = ""
                
                # 处理反馈
                if request.feedback == "不满意":
                    action = get_message("regeneration", request.language)
                    yield SSEMessage.status(get_message("processing", request.language), f"{get_message('feedback_regenerating', request.language)}...")
                    if original_req:
                        stream_generator = agent.regenerate_with_improvements_stream(original_req, request.content)
                    else:
                        stream_generator = agent.regenerate_from_content_stream(request.content, request.language)
                elif request.feedback in ["需要优化", "满意"]:
                    action = get_message("intelligent_optimization", request.language)
                    yield SSEMessage.status(get_message("processing", request.language), f"{get_message('feedback_optimizing', request.language)}...")
                    stream_generator = agent.optimize_content_stream(request.content)
                else:
                    yield SSEMessage.complete({
                        "action": get_message("completion", request.language),
                        "content": request.content,
                        "message": get_message("feedback_processing_complete", request.language)
                    })
                    return
                
                chunk_count = 0
                
                # 处理流式响应
                for chunk in stream_generator:
                    if chunk:
                        content += chunk
                        chunk_count += 1
                        
                        # 发送内容块
                        yield SSEMessage.content_chunk(
                            chunk=chunk,
                            chunk_type="feedback",
                            metadata={
                                "action": action,
                                "feedback_type": request.feedback,
                                "chunk_count": chunk_count,
                                "total_length": len(content)
                            }
                        )
                        
                        # 更新心跳
                        sse_manager.update_heartbeat(connection_id)
                        await asyncio.sleep(0.01)
                
                # 保存到历史
                if content:
                    session_service.add_content_to_history(request.user_id, content, action)
                    session["feedback_round"] = session.get("feedback_round", 0) + 1
                    
                    # 发送完成状态
                    yield SSEMessage.complete({
                        "action": action,
                        "content": content,
                        "version": session['current_version_index'] + 1,
                        "feedback_round": session['feedback_round'],
                        "total_chunks": chunk_count,
                        "total_length": len(content)
                    })
                else:
                    yield SSEMessage.error("生成内容为空")
                
            except Exception as e:
                logger.error(f"反馈处理过程中出错: {e}")
                yield SSEMessage.error(f"反馈处理失败: {str(e)}")
            finally:
                sse_manager.remove_connection(connection_id)
        
        return EventSourceResponse(sse_feedback_stream())
        
    except Exception as e:
        logger.error(f"流式反馈处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 