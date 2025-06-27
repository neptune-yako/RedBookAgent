"""
基础路由 - 健康检查、系统信息等
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from ..models import ApiResponse
from ..services import agent_service, session_service
from ..config import logger, APP_CONFIG, API_ENDPOINTS, SSE_FEATURES
from ..i18n import get_message, get_success_message, get_error_message

router = APIRouter(tags=["base"])


@router.get("/", response_model=ApiResponse)
async def root(language: str = Query("zh-CN", description="语言代码")):
    """API基本信息"""
    try:
        return ApiResponse(
            success=True,
            message=get_success_message("api_info", language),
            data={
                "app": APP_CONFIG,
                "endpoints": API_ENDPOINTS,
                "sse_features": SSE_FEATURES,
                "language": language
            }
        )
    except Exception as e:
        logger.error(f"获取API信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=ApiResponse)
async def health_check(language: str = Query("zh-CN", description="语言代码")):
    """健康检查"""
    try:
        # 检查智能体状态
        agent_ready = agent_service.agent is not None
        
        # 获取系统状态
        system_status = agent_service.get_system_status()
        
        return ApiResponse(
            success=True,
            message=get_success_message("health_check_success", language),
            data={
                "agent_ready": agent_ready,
                "system_status": system_status,
                "language": language
            }
        )
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/status", response_model=ApiResponse)
async def get_system_status(language: str = Query("zh-CN", description="语言代码")):
    """获取系统详细状态"""
    try:
        system_status = agent_service.get_system_status()
        
        return ApiResponse(
            success=True,
            message=get_success_message("system_status_success", language),
            data=system_status
        )
        
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}/status", response_model=ApiResponse)
async def get_task_status(
    task_id: str, 
    language: str = Query("zh-CN", description="语言代码")
):
    """获取任务状态"""
    try:
        task_result = agent_service.get_task_status(task_id)
        
        if task_result is None:
            raise HTTPException(
                status_code=404, 
                detail=get_error_message("task_not_found", language, task_id)
            )
        
        return ApiResponse(
            success=True,
            message=get_success_message("task_status_success", language),
            data={
                "task_id": task_result.task_id,
                "status": task_result.status.value,
                "result": task_result.result,
                "error": task_result.error,
                "started_at": task_result.started_at.isoformat() if task_result.started_at else None,
                "completed_at": task_result.completed_at.isoformat() if task_result.completed_at else None,
                "execution_time": task_result.execution_time
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tasks/{task_id}", response_model=ApiResponse)
async def cancel_task(
    task_id: str,
    language: str = Query("zh-CN", description="语言代码")
):
    """取消任务"""
    try:
        success = agent_service.cancel_task(task_id)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=get_error_message("task_cancel_failed", language, task_id)
            )
        
        return ApiResponse(
            success=True,
            message=get_success_message("task_cancel_success", language),
            data={"task_id": task_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system/cleanup", response_model=ApiResponse)
async def cleanup_system(
    language: str = Query("zh-CN", description="语言代码"),
    max_age_hours: int = Query(24, description="清理多少小时前的数据")
):
    """清理系统数据（系统线程池）"""
    try:
        def cleanup_task():
            """在系统线程中执行的清理任务"""
            # 清理旧任务
            agent_service.cleanup_old_tasks(max_age_hours)
            
            # 清理不活跃的会话
            session_service.cleanup_inactive_sessions(max_age_hours)
            
            return {"cleaned_hours": max_age_hours}
        
        # 提交到系统专用线程池
        task_id = agent_service.submit_system_task(
            task_type="cleanup",
            user_id="system",
            task_func=cleanup_task,
            priority=1  # 系统清理高优先级
        )
        
        return ApiResponse(
            success=True,
            message=get_success_message("task_submitted", language),
            data={
                "task_id": task_id,
                "status": "pending",
                "message": get_message("cleanup_started", language),
                "pool": "system"  # 标明使用的线程池
            }
        )
        
    except Exception as e:
        logger.error(f"提交系统清理任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system/cleanup/sync", response_model=ApiResponse)
async def cleanup_system_sync(
    language: str = Query("zh-CN", description="语言代码"),
    max_age_hours: int = Query(24, description="清理多少小时前的数据")
):
    """同步清理系统数据（立即执行）"""
    try:
        # 清理旧任务
        agent_service.cleanup_old_tasks(max_age_hours)
        
        # 清理不活跃的会话
        session_service.cleanup_inactive_sessions(max_age_hours)
        
        return ApiResponse(
            success=True,
            message=get_success_message("cleanup_success", language),
            data={"cleaned_hours": max_age_hours}
        )
        
    except Exception as e:
        logger.error(f"系统清理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/pools", response_model=ApiResponse)
async def get_thread_pools_status(language: str = Query("zh-CN", description="语言代码")):
    """获取线程池详细状态"""
    try:
        status = agent_service.get_system_status()
        
        # 分别展示两个线程池的状态
        return ApiResponse(
            success=True,
            message=get_success_message("thread_pools_status", language),
            data={
                "agent_pool": {
                    "pool_name": "智能体线程池",
                    "max_workers": status["agent_pool"]["max_workers"],
                    "active_threads": status["agent_pool"]["active_threads"],
                    "queue_size": status["agent_pool"]["queue_size"],
                    "tasks_completed": status["agent_pool"]["tasks_completed"],
                    "tasks_failed": status["agent_pool"]["tasks_failed"],
                    "tasks_pending": status["agent_pool"]["tasks_pending"]
                },
                "system_pool": {
                    "pool_name": "系统线程池", 
                    "max_workers": status["system_pool"]["max_workers"],
                    "active_threads": status["system_pool"]["active_threads"],
                    "queue_size": status["system_pool"]["queue_size"],
                    "tasks_completed": status["system_pool"]["tasks_completed"],
                    "tasks_failed": status["system_pool"]["tasks_failed"],
                    "tasks_pending": status["system_pool"]["tasks_pending"]
                },
                "system_info": {
                    "total_tasks_completed": status["agent_pool"]["tasks_completed"] + status["system_pool"]["tasks_completed"],
                    "total_tasks_failed": status["agent_pool"]["tasks_failed"] + status["system_pool"]["tasks_failed"],
                    "total_tasks_pending": status["agent_pool"]["tasks_pending"] + status["system_pool"]["tasks_pending"],
                    "uptime": status.get("uptime", "unknown")
                }
            }
        )
        
    except Exception as e:
        logger.error(f"获取线程池状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 