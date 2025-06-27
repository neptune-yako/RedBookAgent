"""
国际化支持模块
"""

from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field


class Language(str, Enum):
    """支持的语言枚举"""
    ZH_CN = "zh-CN"  # 简体中文
    EN_US = "en-US"  # 英语（美国）
    ZH_TW = "zh-TW"  # 繁体中文
    JA_JP = "ja-JP"  # 日语


class I18nMixin(BaseModel):
    """国际化混入类，为请求模型添加语言参数"""
    language: Language = Field(
        default=Language.ZH_CN,
        description="接口语言 / Interface Language / インターフェース言語",
        example=Language.ZH_CN
    )


# 多语言消息字典
MESSAGES: Dict[Language, Dict[str, str]] = {
    Language.ZH_CN: {
        # API响应消息
        "api_running": "小红书文案生成智能体 API 服务运行中",
        "service_healthy": "服务健康",
        "running": "运行中",
        "content_generation_success": "文案生成成功",
        "content_optimization_success": "内容优化成功",
        "chat_success": "对话成功",
        "chat": "对话",
        "chat_started": "开始对话...",
        "feedback_processing_complete": "反馈处理完成",
        "version_history_retrieved": "获取版本历史成功",
        "version_restore_success": "版本恢复成功",
        "history_cleared": "历史记录已清空",
        "sse_connection_status_retrieved": "获取连接状态成功",
        
        # 错误消息
        "generation_failed": "生成失败",
        "optimization_failed": "优化失败",
        "chat_failed": "对话失败",
        "feedback_processing_failed": "反馈处理失败",
        "version_restore_failed": "版本恢复失败",
        "history_clear_failed": "清空历史失败",
        "invalid_version_index": "无效的版本索引",
        
        # 状态消息
        "processing": "处理中",
        "completed": "完成",
        "regenerating": "重新生成中",
        "optimizing": "优化中",
        "feedback_regenerating": "根据反馈重新生成中",
        "feedback_optimizing": "根据反馈智能优化中",
        
        # 操作类型
        "initial_generation": "初始生成",
        "intelligent_optimization": "智能优化",
        "regeneration": "重新生成",
        "completion": "完成"
    },
    
    Language.EN_US: {
        # API response messages
        "api_running": "Xiaohongshu Content Generation AI Agent API Service Running",
        "service_healthy": "Service Healthy",
        "running": "Running",
        "content_generation_success": "Content generation successful",
        "content_optimization_success": "Content optimization successful",
        "chat_success": "Chat successful",
        "chat": "Chat",
        "chat_started": "Starting chat...",
        "feedback_processing_complete": "Feedback processing complete",
        "version_history_retrieved": "Version history retrieved successfully",
        "version_restore_success": "Version restore successful",
        "history_cleared": "History cleared",
        "sse_connection_status_retrieved": "Connection status retrieved successfully",
        
        # Error messages
        "generation_failed": "Generation failed",
        "optimization_failed": "Optimization failed", 
        "chat_failed": "Chat failed",
        "feedback_processing_failed": "Feedback processing failed",
        "version_restore_failed": "Version restore failed",
        "history_clear_failed": "History clear failed",
        "invalid_version_index": "Invalid version index",
        
        # Status messages
        "processing": "Processing",
        "completed": "Completed",
        "regenerating": "Regenerating",
        "optimizing": "Optimizing",
        "feedback_regenerating": "Regenerating based on feedback",
        "feedback_optimizing": "Optimizing based on feedback",
        
        # Operation types
        "initial_generation": "Initial Generation",
        "intelligent_optimization": "Intelligent Optimization", 
        "regeneration": "Regeneration",
        "completion": "Completion"
    },
    
    Language.ZH_TW: {
        # API響應訊息
        "api_running": "小紅書文案生成智慧體 API 服務運行中",
        "service_healthy": "服務健康",
        "running": "運行中",
        "content_generation_success": "文案生成成功",
        "content_optimization_success": "內容優化成功",
        "chat_success": "對話成功",
        "chat": "對話",
        "chat_started": "開始對話...",
        "feedback_processing_complete": "反饋處理完成",
        "version_history_retrieved": "獲取版本歷史成功",
        "version_restore_success": "版本恢復成功",
        "history_cleared": "歷史記錄已清空",
        "sse_connection_status_retrieved": "獲取連接狀態成功",
        
        # 錯誤訊息
        "generation_failed": "生成失敗",
        "optimization_failed": "優化失敗",
        "chat_failed": "對話失敗",
        "feedback_processing_failed": "反饋處理失敗",
        "version_restore_failed": "版本恢復失敗",
        "history_clear_failed": "清空歷史失敗",
        "invalid_version_index": "無效的版本索引",
        
        # 狀態訊息
        "processing": "處理中",
        "completed": "完成",
        "regenerating": "重新生成中",
        "optimizing": "優化中",
        "feedback_regenerating": "根據反饋重新生成中",
        "feedback_optimizing": "根據反饋智慧優化中",
        
        # 操作類型
        "initial_generation": "初始生成",
        "intelligent_optimization": "智慧優化",
        "regeneration": "重新生成",
        "completion": "完成"
    },
    
    Language.JA_JP: {
        # API応答メッセージ
        "api_running": "Xiaohongshu コンテンツ生成AIエージェント APIサービス実行中",
        "service_healthy": "サービス正常",
        "running": "実行中",
        "content_generation_success": "コンテンツ生成成功",
        "content_optimization_success": "コンテンツ最適化成功",
        "chat_success": "チャット成功",
        "chat": "チャット",
        "chat_started": "チャット開始中...",
        "feedback_processing_complete": "フィードバック処理完了",
        "version_history_retrieved": "バージョン履歴取得成功",
        "version_restore_success": "バージョン復元成功",
        "history_cleared": "履歴がクリアされました",
        "sse_connection_status_retrieved": "接続状態取得成功",
        
        # エラーメッセージ
        "generation_failed": "生成失敗",
        "optimization_failed": "最適化失敗",
        "chat_failed": "チャット失敗",
        "feedback_processing_failed": "フィードバック処理失敗",
        "version_restore_failed": "バージョン復元失敗",
        "history_clear_failed": "履歴クリア失敗",
        "invalid_version_index": "無効なバージョンインデックス",
        
        # ステータスメッセージ
        "processing": "処理中",
        "completed": "完了",
        "regenerating": "再生成中",
        "optimizing": "最適化中",
        "feedback_regenerating": "フィードバックに基づく再生成中",
        "feedback_optimizing": "フィードバックに基づく最適化中",
        
        # 操作タイプ
        "initial_generation": "初期生成",
        "intelligent_optimization": "インテリジェント最適化",
        "regeneration": "再生成",
        "completion": "完了"
    }
}


def get_message(key: str, language: Language = Language.ZH_CN) -> str:
    """
    获取指定语言的消息
    
    Args:
        key: 消息键
        language: 目标语言
    
    Returns:
        翻译后的消息，如果找不到则返回键本身
    """
    return MESSAGES.get(language, {}).get(key, key)


def get_error_message(error_key: str, language: Language = Language.ZH_CN, error_detail: str = None) -> str:
    """
    获取错误消息
    
    Args:
        error_key: 错误消息键
        language: 目标语言
        error_detail: 错误详情
        
    Returns:
        本地化的错误消息
    """
    message = get_message(error_key, language)
    if error_detail:
        return f"{message}: {error_detail}"
    return message


def get_success_message(success_key: str, language: Language = Language.ZH_CN) -> str:
    """
    获取成功消息
    
    Args:
        success_key: 成功消息键
        language: 目标语言
        
    Returns:
        本地化的成功消息
    """
    return get_message(success_key, language)


# 导出常用的语言常量和函数
__all__ = [
    "Language", 
    "I18nMixin", 
    "get_message", 
    "get_error_message", 
    "get_success_message",
    "MESSAGES"
] 