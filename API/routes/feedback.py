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
        
        # 语言判断和验证
        from ..i18n import Language
        
        try:
            # 验证语言参数是否有效
            target_language = Language(request.language)
            logger.info(f"用户 {request.user_id} 反馈请求语言: {target_language.value}")
        except ValueError:
            # 如果语言无效，使用默认语言
            target_language = Language.ZH_CN
            logger.warning(f"用户 {request.user_id} 使用了无效语言 '{request.language}'，已切换到默认语言: {target_language.value}")
        
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
                special_requirements=request.original_request.special_requirements,
                language=target_language.value
            )
        
        # 使用intelligent_loop方法处理反馈
        result = agent.intelligent_loop(
            content=request.content,
            user_feedback=request.feedback,
            content_request=original_req,
            language=target_language.value
        )
        
        if result["success"]:
            action = ""
            if result.get("action") == "regenerated":
                action = get_message("regeneration", target_language)
            elif result.get("action") == "ask_optimization":
                action = get_message("intelligent_optimization", target_language)
            elif result.get("action") == "completed":
                action = get_message("completion", target_language)
            else:
                action = get_message("feedback_processing", target_language)
            
            # 如果有新生成的内容，保存到历史
            if result.get("content"):
                session_service.add_content_to_history(request.user_id, result["content"], action)
                session["feedback_round"] = session.get("feedback_round", 0) + 1
            
            return ApiResponse(
                success=True,
                message=result.get("message", get_success_message("feedback_processing_complete", target_language)),
                data={
                    "content": result.get("content", request.content),
                    "action": result.get("action", "processed"),
                    "message": result.get("message", ""),
                    "options": result.get("options", []),
                    "version": session["current_version_index"] + 1 if result.get("content") else session.get("current_version_index", 1),
                    "feedback_round": session.get("feedback_round", 0)
                }
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", get_error_message("feedback_processing_failed", target_language)))
            
    except Exception as e:
        logger.error(f"反馈处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def handle_feedback_stream(request: FeedbackRequest):
    """流式智能反馈回环处理（SSE）"""
    try:
        agent = agent_service.check_ready()
        
        # 语言判断和验证
        from ..i18n import Language
        
        try:
            # 验证语言参数是否有效
            target_language = Language(request.language)
            logger.info(f"用户 {request.user_id} 反馈请求语言: {target_language.value}")
        except ValueError:
            # 如果语言无效，使用默认语言
            target_language = Language.ZH_CN
            logger.warning(f"用户 {request.user_id} 使用了无效语言 '{request.language}'，已切换到默认语言: {target_language.value}")
        
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
                        special_requirements=request.original_request.special_requirements,
                        language=target_language.value
                    )
                
                content = ""
                action = ""
                
                # 使用intelligent_loop_stream方法处理反馈
                processing_message = get_message("processing", target_language)
                feedback_message = get_message("feedback_processing", target_language)
                yield SSEMessage.status("processing", f"{processing_message} {feedback_message}...")
                
                stream_generator = agent.intelligent_loop_stream(
                    content=request.content,
                    user_feedback=request.feedback,
                    content_request=original_req,
                    language=target_language.value
                )
                
                # 确定操作类型
                if request.feedback == "不满意" or request.feedback == "重新生成":
                    action = get_message("regeneration", target_language)
                elif request.feedback == "需要优化":
                    action = get_message("intelligent_optimization", target_language)
                elif request.feedback == "满意":
                    action = get_message("satisfaction_inquiry", target_language)
                elif request.feedback == "不需要优化，已完成":
                    action = get_message("completion", target_language)
                else:
                    action = get_message("feedback_processing", target_language)
                
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
                if content and request.feedback in ["不满意", "重新生成", "需要优化"]:
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
                    # 对于询问或完成类的反馈，直接返回确认消息
                    yield SSEMessage.complete({
                        "action": action,
                        "content": content or request.content,
                        "message": content or get_message("feedback_processing_complete", target_language),
                        "version": session.get('current_version_index', 1),
                        "feedback_round": session.get('feedback_round', 0),
                        "total_chunks": chunk_count,
                        "total_length": len(content) if content else 0
                    })
                
            except Exception as e:
                logger.error(f"反馈处理过程中出错: {e}")
                yield SSEMessage.error(f"反馈处理失败: {str(e)}")
            finally:
                sse_manager.remove_connection(connection_id)
        
        return EventSourceResponse(sse_feedback_stream())
        
    except Exception as e:
        logger.error(f"流式反馈处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 