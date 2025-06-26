"""
内容生成相关路由
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from Agent.xiaohongshu_agent import ContentRequest

from ..models import ApiResponse, ContentGenerationRequest, ContentOptimizationRequest
from ..services import agent_service, session_service, stream_service
from ..config import logger

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
            special_requirements=request.special_requirements
        )
        
        result = agent.generate_complete_post(content_req)
        
        if result["success"]:
            # 保存到用户会话
            session = session_service.get_user_session(request.user_id)
            session["current_request"] = request.dict()
            session_service.add_content_to_history(request.user_id, result["content"], "初始生成")
            
            return ApiResponse(
                success=True,
                message="文案生成成功",
                data={
                    "content": result["content"],
                    "version": session["current_version_index"] + 1,
                    "history_count": len(session["content_history"])
                }
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "生成失败"))
            
    except Exception as e:
        logger.error(f"生成文案失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/stream")
async def generate_content_stream(request: ContentGenerationRequest):
    """流式生成小红书文案（SSE）"""
    try:
        agent = agent_service.check_ready()
        
        content_req = ContentRequest(
            category=agent_service.parse_content_category(request.category),
            topic=request.topic,
            tone=request.tone,
            length=request.length,
            keywords=request.keywords or [],
            target_audience=request.target_audience,
            special_requirements=request.special_requirements
        )
        
        # 保存当前请求到会话
        session = session_service.get_user_session(request.user_id)
        session["current_request"] = request.dict()
        
        # 使用SSE包装器
        async def sse_generate_stream():
            generator = agent.generate_complete_post_stream(content_req)
            async for message in stream_service.generate_with_sse(generator, request.user_id, "初始生成"):
                yield message
        
        return EventSourceResponse(sse_generate_stream())
        
    except Exception as e:
        logger.error(f"流式生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize", response_model=ApiResponse)
async def optimize_content(request: ContentOptimizationRequest):
    """优化内容"""
    try:
        agent = agent_service.check_ready()
        
        result = agent.optimize_content(request.content)
        
        if result["success"]:
            # 保存到历史
            session_service.add_content_to_history(request.user_id, result["content"], "智能优化")
            session = session_service.get_user_session(request.user_id)
            
            return ApiResponse(
                success=True,
                message="内容优化成功",
                data={
                    "content": result["content"],
                    "version": session["current_version_index"] + 1,
                    "history_count": len(session["content_history"])
                }
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "优化失败"))
            
    except Exception as e:
        logger.error(f"优化内容失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize/stream")
async def optimize_content_stream(request: ContentOptimizationRequest):
    """流式优化内容（SSE）"""
    try:
        agent = agent_service.check_ready()
        
        # 使用SSE包装器
        async def sse_optimize_stream():
            generator = agent.optimize_content_stream(request.content)
            async for message in stream_service.generate_with_sse(generator, request.user_id, "智能优化"):
                yield message
        
        return EventSourceResponse(sse_optimize_stream())
        
    except Exception as e:
        logger.error(f"流式优化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 