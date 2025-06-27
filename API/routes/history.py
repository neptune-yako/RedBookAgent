"""
历史记录相关路由
"""

from fastapi import APIRouter, HTTPException, Query

from ..models import ApiResponse, VersionRestoreRequest
from ..services import session_service
from ..config import logger
from ..i18n import Language, get_message, get_error_message, get_success_message

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/{user_id}", response_model=ApiResponse)
async def get_version_history(user_id: str, language: Language = Query(default=Language.ZH_CN, description="接口语言")):
    """获取版本历史"""
    try:
        session = session_service.get_user_session(user_id)
        
        return ApiResponse(
            success=True,
            message=get_success_message("version_history_retrieved", language),
            data={
                "content_history": session["content_history"],
                "current_version_index": session["current_version_index"],
                "total_versions": len(session["content_history"])
            }
        )
        
    except Exception as e:
        logger.error(f"获取版本历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore", response_model=ApiResponse)
async def restore_version(request: VersionRestoreRequest):
    """恢复指定版本"""
    try:
        session = session_service.get_user_session(request.user_id)
        
        if 0 <= request.version_index < len(session["content_history"]):
            session["current_version_index"] = request.version_index
            restored_content = session["content_history"][request.version_index]["content"]
            session["last_generated_content"] = restored_content
            
            return ApiResponse(
                success=True,
                message=get_success_message("version_restore_success", request.language),
                data={
                    "content": restored_content,
                    "version": request.version_index + 1,
                    "version_info": session["content_history"][request.version_index]
                }
            )
        else:
            raise HTTPException(status_code=400, detail=get_error_message("invalid_version_index", request.language))
            
    except Exception as e:
        logger.error(f"版本恢复失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}", response_model=ApiResponse)
async def clear_history(user_id: str, language: Language = Query(default=Language.ZH_CN, description="接口语言")):
    """清空用户历史"""
    try:
        session_service.clear_user_session(user_id)
        
        return ApiResponse(
            success=True,
            message=get_success_message("history_cleared", language),
            data={"user_id": user_id}
        )
        
    except Exception as e:
        logger.error(f"清空历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 