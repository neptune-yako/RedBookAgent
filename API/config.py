"""
应用配置和常量
"""

import logging

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 应用配置
APP_CONFIG = {
    "title": "小红书文案生成智能体 API",
    "description": "基于大语言模型的智能小红书文案生成服务",
    "version": "1.0.0"
}

# CORS配置
CORS_CONFIG = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
    "expose_headers": ["*"]
}

# SSE配置
SSE_CONFIG = {
    "heartbeat_interval": 30,  # 心跳间隔（秒）
    "connection_timeout": 60,  # 连接超时（秒）
    "cleanup_interval": 30     # 清理间隔（秒）
}

# API端点信息
API_ENDPOINTS = [
    "GET / - API信息",
    "GET /health - 健康检查",
    "POST /generate - 生成文案",
    "POST /generate/stream - SSE流式生成文案",
    "POST /optimize - 优化内容",
    "POST /optimize/stream - SSE流式优化内容",
    "POST /chat - 对话聊天",
    "POST /chat/stream - SSE流式对话",
    "POST /feedback - 智能反馈回环",
    "POST /feedback/stream - SSE流式反馈处理",
    "POST /sse/connect - 创建SSE连接",
    "GET /sse/status/{user_id} - 获取SSE连接状态",
    "GET /history/{user_id} - 获取版本历史",
    "POST /history/restore - 恢复指定版本",
    "DELETE /history/{user_id} - 清空用户历史"
]

# SSE功能特性
SSE_FEATURES = {
    "heartbeat": "30秒心跳检测",
    "connection_management": "自动连接管理",
    "error_handling": "完整错误处理",
    "message_format": "标准SSE消息格式"
} 