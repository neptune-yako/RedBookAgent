"""
Swagger文档示例配置
为FastAPI应用提供详细的API文档示例
"""

# 内容生成请求示例
CONTENT_GENERATION_EXAMPLES = {
    "美食探店": {
        "summary": "美食探店文案生成",
        "description": "生成一篇关于新开日式料理店的小红书文案",
        "value": {
            "category": "美食探店",
            "topic": "新开的日式料理店初体验",
            "tone": "活泼可爱",
            "length": "中等",
            "keywords": ["日式料理", "新店", "美味", "性价比", "环境"],
            "target_audience": "年轻女性",
            "special_requirements": "要有个人体验感，适合拍照打卡",
            "user_id": "user_001"
        }
    },
    "时尚穿搭": {
        "summary": "时尚穿搭文案生成",
        "description": "生成一篇关于秋季穿搭的小红书文案",
        "value": {
            "category": "时尚穿搭",
            "topic": "秋季温柔风穿搭指南",
            "tone": "温馨治愈",
            "length": "长",
            "keywords": ["秋季", "温柔风", "搭配", "显瘦", "气质"],
            "target_audience": "职场白领",
            "special_requirements": "突出实用性和职场适用性",
            "user_id": "user_002"
        }
    },
    "美妆护肤": {
        "summary": "美妆护肤文案生成",
        "description": "生成一篇关于护肤品测评的小红书文案",
        "value": {
            "category": "美妆护肤",
            "topic": "敏感肌友好面霜测评",
            "tone": "专业详细",
            "length": "长",
            "keywords": ["敏感肌", "面霜", "测评", "成分", "效果"],
            "target_audience": "美妆爱好者",
            "special_requirements": "注重成分分析和使用感受",
            "user_id": "user_003"
        }
    }
}

# 内容优化请求示例
CONTENT_OPTIMIZATION_EXAMPLES = {
    "基础优化": {
        "summary": "基础内容优化",
        "description": "对简单文案进行优化",
        "value": {
            "content": "今天去了一家新开的日式料理店，味道不错，环境也很好。推荐大家去试试。",
            "user_id": "user_001"
        }
    },
    "详细优化": {
        "summary": "详细内容优化",
        "description": "对较详细的文案进行优化",
        "value": {
            "content": "这家新开的咖啡店在市中心，装修很有设计感，咖啡味道也不错，价格中等，适合和朋友聊天或者工作。店员服务态度很好，WiFi也很稳定。",
            "user_id": "user_002"
        }
    }
}

# 对话聊天请求示例
CHAT_EXAMPLES = {
    "文案咨询": {
        "summary": "文案创作咨询",
        "description": "咨询如何写好小红书文案",
        "value": {
            "message": "你好，我想写一篇关于新开咖啡店的小红书文案，但不知道从哪里开始，能给我一些建议吗？",
            "user_id": "user_001"
        }
    },
    "风格询问": {
        "summary": "写作风格询问",
        "description": "询问不同写作风格的特点",
        "value": {
            "message": "活泼可爱和温馨治愈这两种语调有什么区别？我应该选择哪种？",
            "user_id": "user_002"
        }
    },
    "优化建议": {
        "summary": "内容优化建议",
        "description": "寻求内容改进建议",
        "value": {
            "message": "我觉得我写的文案不够吸引人，你能帮我分析一下原因吗？",
            "user_id": "user_003"
        }
    }
}

# 反馈请求示例
FEEDBACK_EXAMPLES = {
    "不满意重生成": {
        "summary": "内容不满意，重新生成",
        "description": "对当前内容不满意，需要重新生成",
        "value": {
            "content": "今天去了一家新开的日式料理店，味道不错。",
            "feedback": "不满意",
            "user_id": "user_001",
            "original_request": {
                "category": "美食探店",
                "topic": "新开的日式料理店初体验",
                "tone": "活泼可爱",
                "length": "中等",
                "keywords": ["日式料理", "新店"],
                "target_audience": "年轻女性",
                "special_requirements": "要有个人体验感",
                "user_id": "user_001"
            }
        }
    },
    "需要优化": {
        "summary": "内容需要优化",
        "description": "对当前内容基本满意，但需要优化",
        "value": {
            "content": "这家日式料理店真的超级棒！环境很不错，菜品也很精致，服务员态度也很好。推荐大家去试试！",
            "feedback": "需要优化",
            "user_id": "user_001"
        }
    },
    "满意优化": {
        "summary": "内容满意，进一步优化",
        "description": "对当前内容满意，希望进一步优化",
        "value": {
            "content": "姐妹们！发现了一家超棒的日式料理店🍱✨ 环境超级有氛围感，每道菜都精致得像艺术品！服务小哥哥也超贴心～ 这颜值和味道并存的组合，简直是约会首选啊！📸拍照也超出片的～",
            "feedback": "满意",
            "user_id": "user_001"
        }
    }
}

# 版本恢复请求示例
VERSION_RESTORE_EXAMPLES = {
    "恢复第一版": {
        "summary": "恢复第一个版本",
        "description": "将内容恢复到第一个生成的版本",
        "value": {
            "user_id": "user_001",
            "version_index": 0
        }
    },
    "恢复优化版": {
        "summary": "恢复优化后的版本",
        "description": "将内容恢复到某个优化后的版本",
        "value": {
            "user_id": "user_001",
            "version_index": 2
        }
    }
}

# SSE连接请求示例
SSE_CONNECTION_EXAMPLES = {
    "通用连接": {
        "summary": "创建通用SSE连接",
        "description": "创建一个通用的SSE连接用于接收各种消息",
        "value": {
            "user_id": "user_001",
            "connection_type": "general"
        }
    },
    "内容生成连接": {
        "summary": "创建内容生成SSE连接",
        "description": "专门用于接收内容生成相关消息的SSE连接",
        "value": {
            "user_id": "user_001",
            "connection_type": "content"
        }
    }
}

# API响应示例
API_RESPONSE_EXAMPLES = {
    "成功响应": {
        "summary": "成功响应示例",
        "description": "API调用成功时的响应格式",
        "value": {
            "success": True,
            "message": "文案生成成功",
            "data": {
                "content": "姐妹们！今天发现了一家超级棒的日式料理店🍱✨...",
                "version": 1,
                "history_count": 1
            },
            "timestamp": "2024-01-15T10:30:00"
        }
    },
    "错误响应": {
        "summary": "错误响应示例", 
        "description": "API调用失败时的响应格式",
        "value": {
            "success": False,
            "message": "生成失败：输入参数不完整",
            "data": None,
            "timestamp": "2024-01-15T10:30:00"
        }
    }
}

# SSE消息格式示例
SSE_MESSAGE_EXAMPLES = {
    "内容块消息": """
event: chunk
data: {
data:   "type": "chunk",
data:   "chunk": "姐妹们！今天发现了一家",
data:   "chunk_type": "content",
data:   "timestamp": "2024-01-15T10:30:00.123Z",
data:   "action": "初始生成",
data:   "chunk_count": 1,
data:   "total_length": 12
data: }
""",
    "完成消息": """
event: complete
data: {
data:   "type": "complete",
data:   "content": "完整的生成内容...",
data:   "action": "初始生成",
data:   "version": 1,
data:   "total_chunks": 25,
data:   "total_length": 380,
data:   "timestamp": "2024-01-15T10:30:05.456Z"
data: }
""",
    "错误消息": """
event: error
data: {
data:   "type": "error",
data:   "message": "生成过程中出现错误",
data:   "code": "GENERATION_ERROR",
data:   "timestamp": "2024-01-15T10:30:02.789Z"
data: }
""",
    "心跳消息": """
event: heartbeat
data: {
data:   "type": "heartbeat",
data:   "timestamp": "2024-01-15T10:30:00.000Z"
data: }
"""
}

# 完整的文档配置
SWAGGER_CONFIG = {
    "content_generation_examples": CONTENT_GENERATION_EXAMPLES,
    "content_optimization_examples": CONTENT_OPTIMIZATION_EXAMPLES,
    "chat_examples": CHAT_EXAMPLES,
    "feedback_examples": FEEDBACK_EXAMPLES,
    "version_restore_examples": VERSION_RESTORE_EXAMPLES,
    "sse_connection_examples": SSE_CONNECTION_EXAMPLES,
    "api_response_examples": API_RESPONSE_EXAMPLES,
    "sse_message_examples": SSE_MESSAGE_EXAMPLES
} 