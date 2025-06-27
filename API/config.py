"""
应用配置和常量
"""

import logging
import os

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 应用配置
APP_CONFIG = {
    "title": "小红书文案生成智能体 API",
    "description": "基于大语言模型的智能小红书文案生成服务（支持多线程处理和HTTP/2.0）",
    "version": "1.2.0"
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

# 多线程配置
THREAD_CONFIG = {
    # 智能体专用线程池配置
    "agent_pool": {
        "max_workers": 3,      # 智能体任务最大工作线程数（AI任务需要更多资源）
        "queue_size": 20,      # 智能体任务队列大小
        "task_timeout": 300,   # 任务超时时间（秒）
    },
    # 系统功能专用线程池配置
    "system_pool": {
        "max_workers": 5,      # 系统任务最大工作线程数
        "queue_size": 50,      # 系统任务队列大小
        "task_timeout": 60,    # 系统任务超时时间（秒）
    },
    # 通用配置
    "cleanup_interval": 3600,  # 清理间隔（秒）
    "max_task_age_hours": 24,  # 任务记录保留时间（小时）
    "max_session_inactive_hours": 24  # 会话不活跃清理时间（小时）
}

# HTTP/2.0 和 SSL 配置
HTTP2_CONFIG = {
    "enabled": True,           # 是否启用HTTP/2.0
    "port": 8000,             # HTTP端口
    "ssl_port": 8443,         # HTTPS端口
    "ssl_enabled": False,     # 是否启用SSL/TLS（生产环境建议启用）
    "ssl_keyfile": "certs/key.pem",      # SSL私钥文件路径
    "ssl_certfile": "certs/cert.pem",    # SSL证书文件路径
    "ssl_ca_certs": None,     # CA证书文件路径（可选）
    "ssl_verify_mode": "CERT_NONE",      # SSL验证模式
    "http2_max_concurrent_streams": 100,  # HTTP/2最大并发流数
    "http2_initial_window_size": 65535,   # HTTP/2初始窗口大小
    "http2_max_frame_size": 16384,        # HTTP/2最大帧大小
    "alpn_protocols": ["h2", "http/1.1"], # ALPN协议列表
}

# 服务器配置
SERVER_CONFIG = {
    "host": "0.0.0.0",
    "workers": 1,             # 工作进程数（HTTP/2建议单进程）
    "backlog": 2048,          # 连接队列大小
    "timeout_keep_alive": 5,  # Keep-Alive超时
    "timeout_graceful_shutdown": 30,  # 优雅关闭超时
    "limit_concurrency": 1000,        # 最大并发连接数
    "limit_max_requests": 10000,      # 最大请求数
    "access_log": True,       # 是否启用访问日志
    "server_header": True,    # 是否发送Server头
    "date_header": True,      # 是否发送Date头
}

# API端点列表
API_ENDPOINTS = [
    "GET / - API信息",
    "GET /health - 健康检查", 
    "POST /content/generate - 同步生成文案",
    "POST /content/generate/async - 异步生成文案",
    "POST /content/generate/stream - 流式生成文案（直接执行）",
    "POST /content/generate/stream/async - 流式生成文案（线程池执行）",
    "POST /content/optimize - 同步优化内容",
    "POST /content/optimize/async - 异步优化内容",
    "POST /content/optimize/stream - 流式优化内容（直接执行）",
    "POST /content/optimize/stream/async - 流式优化内容（线程池执行）",
    "POST /chat - 同步对话聊天",
    "POST /chat/async - 异步对话聊天",
    "POST /chat/stream - 流式对话聊天（直接执行）",
    "POST /chat/stream/async - 流式对话聊天（线程池执行）",
    "POST /content/batch/generate - 批量生成文案",
    "POST /chat/batch - 批量对话",
    "GET /tasks/{task_id}/status - 任务状态查询",
    "DELETE /tasks/{task_id} - 取消任务",
    "GET /system/status - 系统状态监控",
    "GET /system/pools - 线程池状态",
    "POST /system/cleanup - 系统清理",
    "POST /sse/connect - 创建SSE连接",
    "GET /sse/status - SSE连接状态",
    "POST /feedback - 智能反馈",
    "GET /history/{user_id} - 获取历史记录",
    "POST /history/restore - 恢复历史版本",
    "GET /i18n/languages - 获取支持的语言",
    "GET /i18n/messages - 获取翻译消息"
]

# SSE功能特性
SSE_FEATURES = {
    "heartbeat": "30秒心跳检测",
    "connection_management": "自动连接管理", 
    "error_handling": "完整错误处理",
    "message_format": "标准SSE消息格式",
    "http2_support": "HTTP/2.0多路复用支持"
}

# 环境变量支持
def get_env_config():
    """从环境变量获取配置"""
    return {
        "ssl_enabled": os.getenv("SSL_ENABLED", "false").lower() == "true",
        "ssl_keyfile": os.getenv("SSL_KEYFILE", HTTP2_CONFIG["ssl_keyfile"]),
        "ssl_certfile": os.getenv("SSL_CERTFILE", HTTP2_CONFIG["ssl_certfile"]),
        "http2_enabled": os.getenv("HTTP2_ENABLED", "true").lower() == "true",
        "port": int(os.getenv("PORT", HTTP2_CONFIG["port"])),
        "ssl_port": int(os.getenv("SSL_PORT", HTTP2_CONFIG["ssl_port"])),
        "workers": int(os.getenv("WORKERS", SERVER_CONFIG["workers"])),
    }

# 获取运行时配置
RUNTIME_CONFIG = get_env_config()

# 多线程功能特性
THREAD_FEATURES = {
    "dual_thread_pools": "智能体和系统双线程池架构",
    "async_processing": "异步任务处理",
    "stream_task_support": "流式任务线程池支持",
    "batch_operations": "批量操作支持",
    "priority_queue": "优先级任务队列",
    "task_management": "完整任务生命周期管理",
    "thread_safety": "线程安全的会话管理",
    "automatic_cleanup": "自动清理机制",
    "system_monitoring": "系统状态监控",
    "load_balancing": "智能负载均衡"
} 