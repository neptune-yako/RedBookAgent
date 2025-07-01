"""
内容生成相关路由
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from Agent.xiaohongshu_agent import ContentRequest

from ..models import ApiResponse, ContentGenerationRequest, ContentOptimizationRequest
from ..services import agent_service, session_service, stream_service
from ..config import logger
from ..i18n import get_message, get_error_message, get_success_message

router = APIRouter(tags=["content"])


@router.post("/generate", response_model=ApiResponse)
async def generate_content(request: ContentGenerationRequest):
    """生成小红书文案"""
    try:
        agent = agent_service.check_ready()
        
        content_req = ContentRequest(
            category=agent_service.parse_content_category(request.category),
            topic=request.topic,
            tone=request.tone,
            length=request.length,
            keywords=request.keywords or [],
            target_audience=request.target_audience,
            special_requirements=request.special_requirements,
            language=request.language
        )
        
        result = agent.generate_complete_post(content_req)
        
        if result["success"]:
            # 保存到用户会话
            session = session_service.get_user_session(request.user_id)
            session["current_request"] = request.dict()
            session_service.add_content_to_history(request.user_id, result["content"], get_message("initial_generation", request.language))
            
            return ApiResponse(
                success=True,
                message=get_success_message("content_generation_success", request.language),
                data={
                    "content": result["content"],
                    "version": session["current_version_index"] + 1,
                    "history_count": len(session["content_history"])
                }
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", get_error_message("generation_failed", request.language)))
            
    except Exception as e:
        logger.error(f"生成文案失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/async", response_model=ApiResponse)
async def generate_content_async(request: ContentGenerationRequest):
    """异步生成小红书文案（智能体线程池）"""
    try:
        agent = agent_service.check_ready()
        
        def generate_task():
            """在智能体工作线程中执行的生成任务"""
            content_req = ContentRequest(
                category=agent_service.parse_content_category(request.category),
                topic=request.topic,
                tone=request.tone,
                length=request.length,
                keywords=request.keywords or [],
                target_audience=request.target_audience,
                special_requirements=request.special_requirements,
                language=request.language
            )
            
            result = agent.generate_complete_post(content_req)
            
            if result["success"]:
                # 保存到用户会话（线程安全）
                session = session_service.get_user_session(request.user_id)
                session["current_request"] = request.dict()
                session_service.add_content_to_history(
                    request.user_id, 
                    result["content"], 
                    get_message("initial_generation", request.language)
                )
                
                return {
                    "content": result["content"],
                    "version": session["current_version_index"] + 1,
                    "history_count": len(session["content_history"])
                }
            else:
                raise Exception(result.get("error", "生成失败"))
        
        # 提交到智能体专用线程池
        task_id = agent_service.submit_agent_task(
            task_type="generate",
            user_id=request.user_id,
            task_func=generate_task,
            priority=1  # 生成任务高优先级
        )
        
        return ApiResponse(
            success=True,
            message=get_success_message("task_submitted", request.language),
            data={
                "task_id": task_id,
                "status": "pending",
                "message": get_message("generation_started", request.language),
                "pool": "agent"  # 标明使用的线程池
            }
        )
        
    except Exception as e:
        logger.error(f"提交生成任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/stream")
async def generate_content_stream(request: ContentGenerationRequest):
    """流式生成内容（SSE）- 直接执行"""
    try:
        agent = agent_service.check_ready()
        
        content_req = ContentRequest(
            category=agent_service.parse_content_category(request.category),
            topic=request.topic,
            tone=request.tone,
            length=request.length,
            keywords=request.keywords or [],
            target_audience=request.target_audience,
            special_requirements=request.special_requirements,
            language=request.language
        )
        
        # 保存当前请求到会话
        session = session_service.get_user_session(request.user_id)
        session["current_request"] = request.dict()
        
        # 使用SSE包装器，直接传递thinking参数给智能体
        async def sse_generate_stream():
            # 直接传递enable_thinking参数，不修改全局状态
            generator = agent.generate_complete_post_stream(content_req, enable_thinking=request.enable_thinking)
            async for message in stream_service.generate_with_sse(generator, request.user_id, get_message("initial_generation", request.language)):
                yield message
        
        return EventSourceResponse(sse_generate_stream())
        
    except Exception as e:
        logger.error(f"流式生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/stream/async")
async def generate_content_stream_async(request: ContentGenerationRequest):
    """智能流式生成内容（SSE）- 空闲时直接执行，忙碌时使用线程池"""
    try:
        agent = agent_service.check_ready()
        
        # 语言判断和验证
        from ..i18n import Language
        
        try:
            # 验证语言参数是否有效
            target_language = Language(request.language)
            logger.info(f"用户 {request.user_id} 请求语言: {target_language.value}")
        except ValueError:
            # 如果语言无效，使用默认语言
            target_language = Language.ZH_CN
            logger.warning(f"用户 {request.user_id} 使用了无效语言 '{request.language}'，已切换到默认语言: {target_language.value}")
        
        # 保存当前请求到会话，并记录目标语言
        session = session_service.get_user_session(request.user_id)
        session["current_request"] = request.dict()
        session["target_language"] = target_language.value
        
        def stream_generator_func():
            """流式生成器函数"""
            content_req = ContentRequest(
                category=agent_service.parse_content_category(request.category),
                topic=request.topic,
                tone=request.tone,
                length=request.length,
                keywords=request.keywords or [],
                target_audience=request.target_audience,
                special_requirements=request.special_requirements,
                language=target_language.value  # 使用验证后的语言
            )
            
            # 返回流式生成器
            return agent.generate_complete_post_stream(content_req, enable_thinking=request.enable_thinking)
        
        # 使用智能路由进行流式生成
        async def sse_smart_stream():
            async for message in stream_service.generate_with_sse_smart(
                generator_func=stream_generator_func,
                user_id=request.user_id,
                action=get_message("initial_generation", target_language)  # 使用目标语言获取消息
            ):
                yield message
        
        return EventSourceResponse(sse_smart_stream())
        
    except Exception as e:
        logger.error(f"智能流式生成任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize", response_model=ApiResponse)
async def optimize_content(request: ContentOptimizationRequest):
    """优化内容"""
    try:
        agent = agent_service.check_ready()
        
        result = agent.optimize_content(request.content, request.language)
        
        if result["success"]:
            # 保存到历史
            session_service.add_content_to_history(request.user_id, result["content"], get_message("intelligent_optimization", request.language))
            session = session_service.get_user_session(request.user_id)
            
            return ApiResponse(
                success=True,
                message=get_success_message("content_optimization_success", request.language),
                data={
                    "content": result["content"],
                    "version": session["current_version_index"] + 1,
                    "history_count": len(session["content_history"])
                }
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", get_error_message("optimization_failed", request.language)))
            
    except Exception as e:
        logger.error(f"优化内容失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize/async", response_model=ApiResponse)
async def optimize_content_async(request: ContentOptimizationRequest):
    """异步优化内容（智能体线程池）"""
    try:
        agent = agent_service.check_ready()
        
        def optimize_task():
            """在智能体工作线程中执行的优化任务"""
            result = agent.optimize_content(request.content, request.language)
            
            if result["success"]:
                # 保存到历史（线程安全）
                session_service.add_content_to_history(
                    request.user_id, 
                    result["content"], 
                    get_message("intelligent_optimization", request.language)
                )
                session = session_service.get_user_session(request.user_id)
                
                return {
                    "content": result["content"],
                    "version": session["current_version_index"] + 1,
                    "history_count": len(session["content_history"])
                }
            else:
                raise Exception(result.get("error", "优化失败"))
        
        # 提交到智能体专用线程池
        task_id = agent_service.submit_agent_task(
            task_type="optimize",
            user_id=request.user_id,
            task_func=optimize_task,
            priority=2  # 优化任务中等优先级
        )
        
        return ApiResponse(
            success=True,
            message=get_success_message("task_submitted", request.language),
            data={
                "task_id": task_id,
                "status": "pending",
                "message": get_message("optimization_started", request.language),
                "pool": "agent"  # 标明使用的线程池
            }
        )
        
    except Exception as e:
        logger.error(f"提交优化任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize/stream")
async def optimize_content_stream(request: ContentOptimizationRequest):
    """流式优化内容（SSE）- 直接执行"""
    try:
        agent = agent_service.check_ready()
        
        # 使用SSE包装器，直接传递thinking参数给智能体
        async def sse_optimize_stream():
            # 直接传递enable_thinking参数，不修改全局状态
            generator = agent.optimize_content_stream(request.content, request.language, enable_thinking=request.enable_thinking)
            async for message in stream_service.generate_with_sse(generator, request.user_id, get_message("intelligent_optimization", request.language)):
                yield message
        
        return EventSourceResponse(sse_optimize_stream())
        
    except Exception as e:
        logger.error(f"流式优化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize/stream/async")
async def optimize_content_stream_async(request: ContentOptimizationRequest):
    """智能流式优化内容（SSE）- 空闲时直接执行，忙碌时使用线程池"""
    try:
        agent = agent_service.check_ready()
        
        # 语言判断和验证
        from ..i18n import Language
        
        try:
            # 验证语言参数是否有效
            target_language = Language(request.language)
            logger.info(f"用户 {request.user_id} 优化请求语言: {target_language.value}")
        except ValueError:
            # 如果语言无效，使用默认语言
            target_language = Language.ZH_CN
            logger.warning(f"用户 {request.user_id} 使用了无效语言 '{request.language}'，已切换到默认语言: {target_language.value}")
        
        def stream_optimizer_func():
            """流式优化器函数"""
            # 返回流式优化生成器，使用验证后的语言
            return agent.optimize_content_stream(request.content, target_language.value, enable_thinking=request.enable_thinking)
        
        # 使用智能路由进行流式优化
        async def sse_smart_stream():
            async for message in stream_service.generate_with_sse_smart(
                generator_func=stream_optimizer_func,
                user_id=request.user_id,
                action=get_message("intelligent_optimization", target_language)  # 使用目标语言获取消息
            ):
                yield message
        
        return EventSourceResponse(sse_smart_stream())
        
    except Exception as e:
        logger.error(f"智能流式优化任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch/generate", response_model=ApiResponse)
async def batch_generate_content(
    requests: list[ContentGenerationRequest],
    language: str = Query("zh-CN", description="语言代码")
):
    """批量生成内容（智能体线程池）"""
    try:
        agent = agent_service.check_ready()
        
        if len(requests) > 10:  # 限制批量请求数量
            raise HTTPException(
                status_code=400, 
                detail=get_error_message("batch_too_large", language, str(len(requests)))
            )
        
        task_ids = []
        
        for i, request in enumerate(requests):
            def generate_task(req=request):
                """批量生成任务"""
                content_req = ContentRequest(
                    category=agent_service.parse_content_category(req.category),
                    topic=req.topic,
                    tone=req.tone,
                    length=req.length,
                    keywords=req.keywords or [],
                    target_audience=req.target_audience,
                    special_requirements=req.special_requirements,
                    language=req.language
                )
                
                result = agent.generate_complete_post(content_req)
                
                if result["success"]:
                    # 保存到用户会话
                    session = session_service.get_user_session(req.user_id)
                    session_service.add_content_to_history(
                        req.user_id, 
                        result["content"], 
                        f"{get_message('batch_generation', req.language)} {i+1}"
                    )
                    
                    return {
                        "content": result["content"],
                        "request_index": i,
                        "topic": req.topic
                    }
                else:
                    raise Exception(result.get("error", "生成失败"))
            
            # 提交任务到智能体线程池，批量任务使用较低优先级
            task_id = agent_service.submit_agent_task(
                task_type="batch_generate",
                user_id=request.user_id,
                task_func=generate_task,
                priority=3
            )
            task_ids.append(task_id)
        
        return ApiResponse(
            success=True,
            message=get_success_message("batch_tasks_submitted", language),
            data={
                "task_ids": task_ids,
                "total_tasks": len(task_ids),
                "message": get_message("batch_generation_started", language),
                "pool": "agent"  # 标明使用的线程池
            }
        )
        
    except Exception as e:
        logger.error(f"批量生成任务提交失败: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 