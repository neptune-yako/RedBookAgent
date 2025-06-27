"""
国际化相关路由
"""

from fastapi import APIRouter, Query
from typing import Dict, Any

from ..models import ApiResponse
from ..i18n import Language, MESSAGES, get_message

router = APIRouter(prefix="/i18n", tags=["internationalization"])


@router.get("/languages", response_model=ApiResponse)
async def get_supported_languages(language: Language = Query(default=Language.ZH_CN, description="接口语言")):
    """获取支持的语言列表"""
    language_info = {
        Language.ZH_CN: {
            "code": "zh-CN",
            "name": "简体中文",
            "native_name": "简体中文"
        },
        Language.EN_US: {
            "code": "en-US", 
            "name": "English (US)",
            "native_name": "English (US)"
        },
        Language.ZH_TW: {
            "code": "zh-TW",
            "name": "繁體中文",
            "native_name": "繁體中文"
        },
        Language.JA_JP: {
            "code": "ja-JP",
            "name": "日本語",
            "native_name": "日本語"
        }
    }
    
    return ApiResponse(
        success=True,
        message=get_message("api_running", language),
        data={
            "supported_languages": language_info,
            "default_language": Language.ZH_CN,
            "total_languages": len(language_info)
        }
    )


@router.get("/messages", response_model=ApiResponse)
async def get_messages(language: Language = Query(default=Language.ZH_CN, description="接口语言")):
    """获取指定语言的所有消息"""
    return ApiResponse(
        success=True,
        message=get_message("api_running", language),
        data={
            "language": language,
            "messages": MESSAGES.get(language, {})
        }
    ) 