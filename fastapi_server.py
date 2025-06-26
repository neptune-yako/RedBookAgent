"""
小红书文案生成智能体 - FastAPI后端服务
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, ConfigDict
from sse_starlette.sse import EventSourceResponse

from Agent.xiaohongshu_agent import XiaohongshuAgent, ContentRequest, ContentCategory

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局变量
agent_instance = None
user_sessions: Dict[str, Dict] = {}
active_connections: Dict[str, Dict] = {}  # 存储活跃的SSE连接

class SSEMessage:
    """SSE消息标准格式"""
    
    @staticmethod
    def format_message(data: Any, event: str = None, id: str = None, retry: int = None) -> str:
        """格式化SSE消息
        
        Args:
            data: 消息数据
            event: 事件类型
            id: 消息ID
            retry: 重连时间(毫秒)
        
        Returns:
            str: 格式化的SSE消息
        """
        message_parts = []
        
        if id:
            message_parts.append(f"id: {id}")
        
        if event:
            message_parts.append(f"event: {event}")
        
        if retry:
            message_parts.append(f"retry: {retry}")
        
        # 处理数据部分
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, ensure_ascii=False)
        else:
            data_str = str(data)
        
        # 处理多行数据
        for line in data_str.split('\n'):
            message_parts.append(f"data: {line}")
        
        return '\n'.join(message_parts) + '\n\n'
    
    @staticmethod
    def heartbeat() -> str:
        """心跳消息"""
        return SSEMessage.format_message(
            data={"type": "heartbeat", "timestamp": datetime.now().isoformat()},
            event="heartbeat"
        )
    
    @staticmethod
    def error(error_msg: str, error_code: str = None) -> str:
        """错误消息"""
        return SSEMessage.format_message(
            data={
                "type": "error",
                "message": error_msg,
                "code": error_code,
                "timestamp": datetime.now().isoformat()
            },
            event="error"
        )
    
    @staticmethod
    def content_chunk(chunk: str, chunk_type: str = "content", metadata: Dict = None) -> str:
        """内容块消息"""
        data = {
            "type": "chunk",
            "chunk": chunk,
            "chunk_type": chunk_type,
            "timestamp": datetime.now().isoformat()
        }
        if metadata:
            data.update(metadata)
        
        return SSEMessage.format_message(data=data, event="chunk")
    
    @staticmethod
    def complete(result_data: Dict = None) -> str:
        """完成消息"""
        data = {
            "type": "complete",
            "timestamp": datetime.now().isoformat()
        }
        if result_data:
            data.update(result_data)
        
        return SSEMessage.format_message(data=data, event="complete")
    
    @staticmethod
    def status(status: str, message: str = None, progress: float = None) -> str:
        """状态消息"""
        data = {
            "type": "status",
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        if message:
            data["message"] = message
        if progress is not None:
            data["progress"] = progress
        
        return SSEMessage.format_message(data=data, event="status")

class SSEConnectionManager:
    """SSE连接管理器"""
    
    def __init__(self):
        self.connections: Dict[str, Dict] = {}
    
    def add_connection(self, connection_id: str, user_id: str, connection_type: str = "general"):
        """添加连接"""
        self.connections[connection_id] = {
            "user_id": user_id,
            "connection_type": connection_type,
            "connected_at": datetime.now(),
            "last_heartbeat": datetime.now(),
            "status": "active",
            "message_count": 0
        }
        logger.info(f"新增 SSE 连接: {connection_id} (用户: {user_id}, 类型: {connection_type})")
    
    def remove_connection(self, connection_id: str):
        """移除连接"""
        if connection_id in self.connections:
            connection_info = self.connections[connection_id]
            logger.info(f"移除 SSE 连接: {connection_id} (用户: {connection_info['user_id']})")
            del self.connections[connection_id]
    
    def get_user_connections(self, user_id: str) -> List[str]:
        """获取用户的所有连接"""
        return [
            conn_id for conn_id, info in self.connections.items()
            if info["user_id"] == user_id
        ]
    
    def update_heartbeat(self, connection_id: str):
        """更新心跳时间"""
        if connection_id in self.connections:
            self.connections[connection_id]["last_heartbeat"] = datetime.now()
            self.connections[connection_id]["message_count"] += 1
    
    def check_connection_health(self, connection_id: str) -> bool:
        """检查连接健康状态"""
        if connection_id not in self.connections:
            return False
        
        connection = self.connections[connection_id]
        last_heartbeat = connection["last_heartbeat"]
        time_diff = (datetime.now() - last_heartbeat).total_seconds()
        
        # 超过 60 秒没有心跳认为连接不健康
        if time_diff > 60:
            connection["status"] = "inactive"
            return False
        
        connection["status"] = "active"
        return True
    
    def get_connection_status(self, connection_id: str) -> Dict:
        """获取连接详细状态"""
        if connection_id not in self.connections:
            return {"status": "not_found"}
        
        connection = self.connections[connection_id]
        time_diff = (datetime.now() - connection["last_heartbeat"]).total_seconds()
        
        return {
            "connection_id": connection_id,
            "user_id": connection["user_id"],
            "connection_type": connection["connection_type"],
            "status": connection["status"],
            "connected_at": connection["connected_at"].isoformat(),
            "last_heartbeat": connection["last_heartbeat"].isoformat(),
            "seconds_since_heartbeat": time_diff,
            "message_count": connection["message_count"],
            "is_healthy": time_diff <= 60
        }
    
    def get_all_connections_status(self) -> Dict:
        """获取所有连接状态统计"""
        total_connections = len(self.connections)
        active_connections = 0
        inactive_connections = 0
        users = set()
        
        for conn_id, info in self.connections.items():
            users.add(info["user_id"])
            if self.check_connection_health(conn_id):
                active_connections += 1
            else:
                inactive_connections += 1
        
        return {
            "total_connections": total_connections,
            "active_connections": active_connections,
            "inactive_connections": inactive_connections,
            "unique_users": len(users),
            "connection_details": [
                self.get_connection_status(conn_id) 
                for conn_id in self.connections.keys()
            ]
        }
    
    def cleanup_inactive_connections(self) -> int:
        """清理不活跃的连接"""
        inactive_connections = []
        
        for conn_id in list(self.connections.keys()):
            if not self.check_connection_health(conn_id):
                inactive_connections.append(conn_id)
        
        for conn_id in inactive_connections:
            self.remove_connection(conn_id)
        
        if inactive_connections:
            logger.info(f"清理了 {len(inactive_connections)} 个不活跃连接")
        
        return len(inactive_connections)

# 全局连接管理器
sse_manager = SSEConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global agent_instance
    try:
        logger.info("正在初始化小红书智能体...")
        agent_instance = XiaohongshuAgent(enable_stream=True, enable_thinking=True)
        logger.info("智能体初始化完成")
        
        # 启动心跳任务
        asyncio.create_task(heartbeat_task())
        
    except Exception as e:
        logger.error(f"智能体初始化失败: {e}")
        agent_instance = None
    
    yield
    logger.info("正在关闭服务...")

async def heartbeat_task():
    """心跳任务，定期清理断开的连接并监控连接状态"""
    while True:
        try:
            # 清理不活跃的连接
            cleaned_count = sse_manager.cleanup_inactive_connections()
            
            # 获取连接状态统计
            status = sse_manager.get_all_connections_status()
            
            # 记录连接状态日志（仅在有连接时）
            if status["total_connections"] > 0:
                logger.info(
                    f"SSE 连接状态: 总连接 {status['total_connections']}, "
                    f"活跃 {status['active_connections']}, "
                    f"不活跃 {status['inactive_connections']}, "
                    f"用户数 {status['unique_users']}"
                )
            
            # 如果清理了连接，记录详细信息
            if cleaned_count > 0:
                logger.warning(f"本次清理了 {cleaned_count} 个不活跃连接")
            
            await asyncio.sleep(30)  # 每30秒检查一次
            
        except Exception as e:
            logger.error(f"心跳任务错误: {e}")
            await asyncio.sleep(30)

# 创建FastAPI应用
app = FastAPI(
    title="小红书文案生成智能体 API",
    description="""
    ## 小红书文案生成智能体 API
    
    基于大语言模型的智能小红书文案生成服务，提供完整的文案创作、优化和对话功能。
    
    ### 主要功能
    - 🎯 **智能文案生成**: 根据主题和风格要求生成高质量小红书文案
    - 🔄 **内容优化**: 对现有文案进行智能优化和改进
    - 💬 **对话聊天**: 与AI助手进行自然对话交流
    - 📝 **反馈回环**: 基于用户反馈持续改进生成质量
    - 📚 **版本管理**: 支持多版本内容管理和历史记录
    - 🔄 **实时流式**: 支持SSE实时流式输出
    
    ### 使用指南
    1. 选择合适的内容分类和语调风格
    2. 提供清晰的主题描述和目标受众
    3. 使用反馈功能持续优化内容质量
    4. 利用版本管理功能对比不同版本
    
    ### 技术特色
    - Server-Sent Events (SSE) 实时流式输出
    - 智能反馈回环机制
    - 多版本内容管理
    - 用户会话状态管理
    
    ### API版本: v1.0.0
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    tags_metadata=[
        {
            "name": "基础信息",
            "description": "API基础信息和健康检查"
        },
        {
            "name": "内容生成", 
            "description": "小红书文案生成相关接口"
        },
        {
            "name": "内容优化",
            "description": "文案内容优化和改进接口"
        },
        {
            "name": "对话聊天",
            "description": "AI对话聊天接口"
        },
        {
            "name": "智能反馈",
            "description": "基于用户反馈的智能回环处理"
        },
        {
            "name": "版本管理",
            "description": "内容版本历史管理"
        },
        {
            "name": "SSE连接",
            "description": "Server-Sent Events 实时流式连接管理"
        }
    ]
)

# 配置CORS，特别为SSE添加支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# =================== 数据模型 ===================

class ContentGenerationRequest(BaseModel):
    """内容生成请求模型"""
    category: str = Field(
        ..., 
        description="内容分类",
        example="美食探店",
        examples=[
            "美妆护肤", "时尚穿搭", "美食探店", "旅行攻略", "生活方式",
            "健身运动", "家居装饰", "学习分享", "职场干货", "好物推荐"
        ]
    )
    topic: str = Field(
        ..., 
        description="主题内容",
        example="新开的日式料理店体验"
    )
    tone: str = Field(
        default="活泼可爱", 
        description="""语调风格 - 控制生成文案的语言风格和表达方式
        可选值：
        • 活泼可爱 - 年轻化、emoji丰富、互动性强（如：姐妹们！这家店绝了！😍）
        • 温馨治愈 - 温暖、舒缓、情感丰富（如：在忙碌生活中找到温暖角落...）
        • 专业详细 - 客观、专业、信息量大（如：经实地体验，该餐厅表现优异）
        • 幽默搞笑 - 轻松、有趣、调侃式（如：本吃货又被套路了😂）
        • 简洁明了 - 直接、简练、要点突出（如：新店推荐，值得一试）""",
        example="活泼可爱"
    )
    length: str = Field(
        default="中等", 
        description="""内容长度 - 控制生成文案的篇幅
        可选值：
        • 短 - 100-200字，适合朋友圈分享、简单推荐
        • 中等 - 200-500字，适合标准小红书笔记，详略得当
        • 长 - 500-800字，适合深度测评、攻略分享，内容详尽""",
        example="中等"
    )
    keywords: Optional[List[str]] = Field(
        default=None, 
        description="关键词列表 - 希望在文案中重点体现的词汇",
        example=["日式料理", "新店", "美味", "性价比"]
    )
    target_audience: str = Field(
        default="年轻女性", 
        description="""目标受众 - 影响语言风格、关注点和内容重点
        常见选项：
        • 年轻女性 (18-30岁) - 关注颜值、性价比、拍照效果，语言活泼感性
        • 职场白领 (25-40岁) - 关注效率、品质、便利性，语言理性简洁
        • 学生群体 (16-25岁) - 关注性价比、潮流、实用性，语言年轻化
        • 宝妈群体 (25-45岁) - 关注安全性、实用性、家庭适用，语言温馨实用
        • 美食爱好者 - 专注美食体验，注重口味描述和专业评价
        • 时尚达人 - 关注潮流趋势，语言前卫时髦""",
        example="年轻女性"
    )
    special_requirements: str = Field(
        default="", 
        description="""特殊要求 - 用于精细化控制生成内容的额外需求
        常见要求示例：
        • "要有个人体验感" - 增加第一人称体验描述，如"我觉得"、"亲测"
        • "突出性价比" - 强调价格优势，对比同类产品
        • "适合拍照打卡" - 突出视觉效果、环境美观度
        • "包含使用教程" - 添加详细的操作步骤和使用方法
        • "强调安全性" - 突出产品的安全特点和保障
        • "注重环保理念" - 强调可持续发展、环保材料
        • "适合送礼" - 突出礼品属性、包装精美
        • "制造紧迫感" - 如限时优惠、数量有限等""",
        example="要有个人体验感，适合拍照打卡"
    )
    user_id: str = Field(
        ..., 
        description="用户ID - 用于会话管理和内容历史记录",
        example="user_001"
    )

class ContentOptimizationRequest(BaseModel):
    """内容优化请求模型"""
    content: str = Field(
        ..., 
        description="待优化的内容",
        example="今天去了一家新开的日式料理店，味道不错，环境也很好。"
    )
    user_id: str = Field(
        ..., 
        description="用户ID",
        example="user_001"
    )

class ChatRequest(BaseModel):
    """对话聊天请求模型"""
    message: str = Field(
        ..., 
        description="用户消息",
        example="你好，请帮我写一篇关于新开咖啡店的小红书文案"
    )
    user_id: str = Field(
        ..., 
        description="用户ID",
        example="user_001"
    )

class FeedbackRequest(BaseModel):
    """智能反馈请求模型"""
    content: str = Field(
        ..., 
        description="当前内容 - 需要处理的文案内容",
        example="今天去了一家新开的日式料理店，味道不错，环境也很好。"
    )
    feedback: str = Field(
        ..., 
        description="""用户反馈类型
        可选值：
        • "不满意" - 完全重新生成新的文案
        • "满意" - 在当前基础上进行优化
        • "需要优化" - 保持主体内容，进行细节优化
        • "完全满意" - 结束处理流程""",
        example="需要优化"
    )
    user_id: str = Field(
        ..., 
        description="用户ID - 用于会话管理和内容历史记录",
        example="user_001"
    )
    original_request: Optional[ContentGenerationRequest] = Field(
        default=None, 
        description="原始请求 - 用于重新生成时参考原始参数（tone、length、target_audience等）"
    )

class VersionRestoreRequest(BaseModel):
    """版本恢复请求模型"""
    user_id: str = Field(
        ..., 
        description="用户ID",
        example="user_001"
    )
    version_index: int = Field(
        ..., 
        description="版本索引（从0开始）",
        example=0,
        ge=0
    )

class SSEConnectionRequest(BaseModel):
    """SSE连接请求模型"""
    user_id: str = Field(
        ..., 
        description="用户ID",
        example="user_001"
    )
    connection_type: str = Field(
        default="general", 
        description="连接类型",
        example="general",
        examples=["general", "content", "chat", "feedback"]
    )

class ApiResponse(BaseModel):
    """标准API响应模型"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    success: bool = Field(
        ..., 
        description="请求是否成功",
        example=True
    )
    message: str = Field(
        ..., 
        description="响应消息",
        example="操作成功"
    )
    data: Optional[Any] = Field(
        default=None, 
        description="响应数据",
        example={"content": "生成的小红书文案内容..."}
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(), 
        description="响应时间"
    )

# =================== 辅助函数 ===================

def get_user_session(user_id: str) -> Dict:
    """获取用户会话"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "content_history": [],
            "current_version_index": -1,
            "feedback_round": 0,
            "last_generated_content": "",
            "current_request": None,
            "created_at": datetime.now()
        }
    return user_sessions[user_id]

def add_content_to_history(user_id: str, content: str, action: str = "生成"):
    """添加内容到版本历史"""
    session = get_user_session(user_id)
    version_info = {
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "version": len(session["content_history"]) + 1
    }
    session["content_history"].append(version_info)
    session["current_version_index"] = len(session["content_history"]) - 1
    session["last_generated_content"] = content

def check_agent_ready():
    if agent_instance is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    return agent_instance

def parse_content_category(category_str: str) -> ContentCategory:
    category_map = {
        "美妆护肤": ContentCategory.BEAUTY,
        "时尚穿搭": ContentCategory.FASHION,
        "美食探店": ContentCategory.FOOD,
        "旅行攻略": ContentCategory.TRAVEL,
        "生活方式": ContentCategory.LIFESTYLE,
        "健身运动": ContentCategory.FITNESS,
        "家居装饰": ContentCategory.HOME,
        "学习分享": ContentCategory.STUDY,
        "职场干货": ContentCategory.WORK,
        "好物推荐": ContentCategory.SHOPPING,
    }
    return category_map.get(category_str, ContentCategory.LIFESTYLE)

async def generate_with_sse(generator, user_id: str, action: str = "生成"):
    """通用的SSE生成器包装器"""
    connection_id = f"{user_id}_{datetime.now().timestamp()}"
    
    try:
        # 添加连接
        sse_manager.add_connection(connection_id, user_id, action)
        
        # 发送开始状态
        yield SSEMessage.status("started", f"开始{action}...")
        
        content = ""
        chunk_count = 0
        
        # 处理生成器内容（同步生成器）
        try:
            for chunk in generator:
                if chunk:
                    content += chunk
                    chunk_count += 1
                    
                    # 发送内容块
                    yield SSEMessage.content_chunk(
                        chunk=chunk,
                        metadata={
                            "action": action,
                            "chunk_count": chunk_count,
                            "total_length": len(content)
                        }
                    )
                    
                    # 更新心跳
                    sse_manager.update_heartbeat(connection_id)
                    
                    # 小延迟，避免发送过快
                    await asyncio.sleep(0.01)
        except StopIteration:
            pass  # 生成器正常结束
        
        # 保存到历史
        if content:
            add_content_to_history(user_id, content, action)
            session = get_user_session(user_id)
            
            # 发送完成状态
            yield SSEMessage.complete({
                "content": content,
                "action": action,
                "version": session["current_version_index"] + 1,
                "total_chunks": chunk_count,
                "total_length": len(content)
            })
        else:
            yield SSEMessage.error("生成内容为空")
            
    except Exception as e:
        logger.error(f"{action}过程中出错: {e}")
        yield SSEMessage.error(f"{action}失败: {str(e)}")
    
    finally:
        # 移除连接
        sse_manager.remove_connection(connection_id)

# =================== SSE连接管理 ===================

@app.post("/sse/connect", tags=["SSE连接"], summary="创建SSE连接", description="创建Server-Sent Events连接用于实时消息推送")
async def create_sse_connection(request: SSEConnectionRequest):
    """创建SSE连接"""
    connection_id = f"{request.user_id}_{datetime.now().timestamp()}"
    
    async def sse_stream():
        try:
            # 添加连接
            sse_manager.add_connection(connection_id, request.user_id, request.connection_type)
            
            # 发送连接确认
            yield SSEMessage.format_message(
                data={
                    "type": "connected",
                    "connection_id": connection_id,
                    "user_id": request.user_id,
                    "timestamp": datetime.now().isoformat()
                },
                event="connected"
            )
            
            # 保持连接活跃，定期发送心跳
            while True:
                yield SSEMessage.heartbeat()
                sse_manager.update_heartbeat(connection_id)
                await asyncio.sleep(30)  # 每30秒发送心跳
                
        except asyncio.CancelledError:
            logger.info(f"SSE连接 {connection_id} 被取消")
        except Exception as e:
            logger.error(f"SSE连接错误: {e}")
            yield SSEMessage.error(f"连接错误: {str(e)}")
        finally:
            sse_manager.remove_connection(connection_id)
    
    return EventSourceResponse(sse_stream())

@app.get("/sse/status/{user_id}", tags=["SSE连接"], summary="获取用户SSE连接状态", description="获取指定用户的Server-Sent Events连接状态信息")
async def get_user_sse_status(user_id: str):
    """获取用户的SSE连接状态"""
    user_connections = sse_manager.get_user_connections(user_id)
    connection_details = []
    
    for conn_id in user_connections:
        status = sse_manager.get_connection_status(conn_id)
        connection_details.append(status)
    
    return ApiResponse(
        success=True,
        message="获取用户连接状态成功",
        data={
            "user_id": user_id,
            "connection_count": len(user_connections),
            "connection_details": connection_details,
            "has_active_connections": any(detail.get("is_healthy", False) for detail in connection_details)
        }
    )

@app.get("/sse/status", tags=["SSE连接"], summary="获取所有SSE连接状态", description="获取系统中所有Server-Sent Events连接的状态统计信息")
async def get_all_sse_status():
    """获取所有SSE连接状态"""
    status = sse_manager.get_all_connections_status()
    return ApiResponse(
        success=True,
        message="获取所有连接状态成功",
        data=status
    )

@app.get("/sse/connection/{connection_id}", tags=["SSE连接"], summary="获取单个连接状态", description="获取指定连接ID的详细状态信息")
async def get_connection_status(connection_id: str):
    """获取单个连接的详细状态"""
    status = sse_manager.get_connection_status(connection_id)
    
    if status.get("status") == "not_found":
        return ApiResponse(
            success=False,
            message="连接不存在",
            data={"connection_id": connection_id, "status": "not_found"}
        )
    
    return ApiResponse(
        success=True,
        message="获取连接状态成功",
        data=status
    )

@app.post("/sse/cleanup", tags=["SSE连接"], summary="清理不活跃连接", description="手动触发清理不活跃的SSE连接")
async def cleanup_sse_connections():
    """手动清理不活跃的SSE连接"""
    cleaned_count = sse_manager.cleanup_inactive_connections()
    return ApiResponse(
        success=True,
        message=f"清理完成，共清理了 {cleaned_count} 个不活跃连接",
        data={
            "cleaned_connections": cleaned_count,
            "remaining_connections": len(sse_manager.connections)
        }
    )

# =================== API路由 ===================

@app.get("/", response_model=ApiResponse, tags=["基础信息"], summary="API基本信息", description="获取API的基本信息、状态和可用端点列表")
async def root():
    return ApiResponse(
        success=True,
        message="小红书文案生成智能体 API 服务运行中",
        data={
            "version": "1.0.0",
            "status": "running",
            "agent_ready": agent_instance is not None,
            "endpoints": [
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
                "GET /sse/status - 获取所有SSE连接状态",
                "GET /sse/status/{user_id} - 获取用户SSE连接状态",
                "GET /sse/connection/{connection_id} - 获取单个连接状态",
                "POST /sse/cleanup - 清理不活跃连接",
                "GET /history/{user_id} - 获取版本历史",
                "POST /history/restore - 恢复指定版本",
                "DELETE /history/{user_id} - 清空用户历史"
            ],
            "sse_features": {
                "heartbeat": "30秒心跳检测",
                "connection_management": "自动连接管理",
                "error_handling": "完整错误处理",
                "message_format": "标准SSE消息格式"
            }
        }
    )

@app.get("/health", response_model=ApiResponse, tags=["基础信息"], summary="健康检查", description="检查API服务和智能体的运行状态")
async def health_check():
    """健康检查"""
    agent = check_agent_ready()
    agent_status = agent.check_setup()
    
    return ApiResponse(
        success=True,
        message="服务健康",
        data={
            "agent_ready": agent_status,
            "active_sessions": len(user_sessions),
            "uptime": "运行中"
        }
    )

@app.post("/generate", response_model=ApiResponse, tags=["内容生成"], summary="生成小红书文案", description="根据指定的分类、主题、语调等参数生成小红书文案内容")
async def generate_content(request: ContentGenerationRequest):
    """生成小红书文案"""
    try:
        agent = check_agent_ready()
        
        content_req = ContentRequest(
            category=parse_content_category(request.category),
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
            session = get_user_session(request.user_id)
            session["current_request"] = request.dict()
            add_content_to_history(request.user_id, result["content"], "初始生成")
            
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

@app.post("/generate/stream", tags=["内容生成"], summary="流式生成小红书文案", description="使用Server-Sent Events实时流式生成小红书文案，支持实时查看生成进度")
async def generate_content_stream(request: ContentGenerationRequest):
    """流式生成小红书文案（SSE）"""
    try:
        agent = check_agent_ready()
        
        content_req = ContentRequest(
            category=parse_content_category(request.category),
            topic=request.topic,
            tone=request.tone,
            length=request.length,
            keywords=request.keywords or [],
            target_audience=request.target_audience,
            special_requirements=request.special_requirements
        )
        
        # 保存当前请求到会话
        session = get_user_session(request.user_id)
        session["current_request"] = request.dict()
        
        # 使用新的SSE包装器
        async def sse_generate_stream():
            generator = agent.generate_complete_post_stream(content_req)
            async for message in generate_with_sse(generator, request.user_id, "初始生成"):
                yield message
        
        return EventSourceResponse(sse_generate_stream())
        
    except Exception as e:
        logger.error(f"流式生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize", response_model=ApiResponse, tags=["内容优化"], summary="优化文案内容", description="对现有文案内容进行智能优化，改进语言表达和结构")
async def optimize_content(request: ContentOptimizationRequest):
    """优化内容"""
    try:
        agent = check_agent_ready()
        
        result = agent.optimize_content(request.content)
        
        if result["success"]:
            # 保存到历史
            add_content_to_history(request.user_id, result["content"], "智能优化")
            session = get_user_session(request.user_id)
            
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

@app.post("/optimize/stream", tags=["内容优化"], summary="流式优化文案内容", description="使用Server-Sent Events实时流式优化文案内容")
async def optimize_content_stream(request: ContentOptimizationRequest):
    """流式优化内容（SSE）"""
    try:
        agent = check_agent_ready()
        
        # 使用新的SSE包装器
        async def sse_optimize_stream():
            generator = agent.optimize_content_stream(request.content)
            async for message in generate_with_sse(generator, request.user_id, "智能优化"):
                yield message
        
        return EventSourceResponse(sse_optimize_stream())
        
    except Exception as e:
        logger.error(f"流式优化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ApiResponse, tags=["对话聊天"], summary="对话聊天", description="与AI智能体进行自然语言对话交流")
async def chat(request: ChatRequest):
    """对话聊天"""
    try:
        agent = check_agent_ready()
        
        response = agent.chat(request.message)
        
        return ApiResponse(
            success=True,
            message="对话成功",
            data={"response": response}
        )
        
    except Exception as e:
        logger.error(f"对话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream", tags=["对话聊天"], summary="流式对话聊天", description="使用Server-Sent Events进行实时流式对话聊天")
async def chat_stream(request: ChatRequest):
    """流式对话聊天（SSE）"""
    try:
        agent = check_agent_ready()
        
        async def sse_chat_stream():
            try:
                connection_id = f"{request.user_id}_chat_{datetime.now().timestamp()}"
                sse_manager.add_connection(connection_id, request.user_id, "chat")
                
                # 发送开始状态
                yield SSEMessage.status("started", "开始对话...")
                
                response_content = ""
                chunk_count = 0
                
                # 处理对话流
                for chunk in agent.chat_stream(request.message):
                    if chunk:
                        response_content += chunk
                        chunk_count += 1
                        
                        # 发送内容块
                        yield SSEMessage.content_chunk(
                            chunk=chunk,
                            chunk_type="chat",
                            metadata={
                                "action": "对话",
                                "chunk_count": chunk_count,
                                "total_length": len(response_content)
                            }
                        )
                        
                        # 更新心跳
                        sse_manager.update_heartbeat(connection_id)
                        await asyncio.sleep(0.01)
                
                # 发送完成状态
                yield SSEMessage.complete({
                    "response": response_content,
                    "action": "对话",
                    "total_chunks": chunk_count,
                    "total_length": len(response_content)
                })
                
            except Exception as e:
                logger.error(f"对话过程中出错: {e}")
                yield SSEMessage.error(f"对话失败: {str(e)}")
            finally:
                sse_manager.remove_connection(connection_id)
        
        return EventSourceResponse(sse_chat_stream())
        
    except Exception as e:
        logger.error(f"流式对话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback", response_model=ApiResponse, tags=["智能反馈"], summary="智能反馈处理", description="基于用户反馈对内容进行重新生成或优化处理")
async def handle_feedback(request: FeedbackRequest):
    """智能反馈回环处理"""
    try:
        agent = check_agent_ready()
        session = get_user_session(request.user_id)
        
        # 构造原始请求
        original_req = None
        if request.original_request:
            original_req = ContentRequest(
                category=parse_content_category(request.original_request.category),
                topic=request.original_request.topic,
                tone=request.original_request.tone,
                length=request.original_request.length,
                keywords=request.original_request.keywords or [],
                target_audience=request.original_request.target_audience,
                special_requirements=request.original_request.special_requirements
            )
        
        # 处理反馈
        if request.feedback == "不满意":
            if original_req:
                result = agent.regenerate_with_improvements(original_req, request.content)
            else:
                result = agent.regenerate_from_content(request.content)
            action = "重新生成"
        elif request.feedback in ["需要优化", "满意"]:
            result = agent.optimize_content(request.content)
            action = "智能优化"
        else:
            return ApiResponse(
                success=True,
                message="反馈处理完成",
                data={"action": "完成", "content": request.content}
            )
        
        if result["success"]:
            # 保存到历史
            add_content_to_history(request.user_id, result["content"], action)
            session["feedback_round"] = session.get("feedback_round", 0) + 1
            
            return ApiResponse(
                success=True,
                message=f"{action}成功",
                data={
                    "content": result["content"],
                    "action": action,
                    "version": session["current_version_index"] + 1,
                    "feedback_round": session["feedback_round"]
                }
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", f"{action}失败"))
            
    except Exception as e:
        logger.error(f"反馈处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback/stream", tags=["智能反馈"], summary="流式智能反馈处理", description="使用Server-Sent Events进行实时流式反馈处理")
async def handle_feedback_stream(request: FeedbackRequest):
    """流式智能反馈回环处理（SSE）"""
    try:
        agent = check_agent_ready()
        session = get_user_session(request.user_id)
        
        async def sse_feedback_stream():
            try:
                connection_id = f"{request.user_id}_feedback_{datetime.now().timestamp()}"
                sse_manager.add_connection(connection_id, request.user_id, "feedback")
                
                # 构造原始请求
                original_req = None
                if request.original_request:
                    original_req = ContentRequest(
                        category=parse_content_category(request.original_request.category),
                        topic=request.original_request.topic,
                        tone=request.original_request.tone,
                        length=request.original_request.length,
                        keywords=request.original_request.keywords or [],
                        target_audience=request.original_request.target_audience,
                        special_requirements=request.original_request.special_requirements
                    )
                
                content = ""
                action = ""
                
                # 处理反馈
                if request.feedback == "不满意":
                    action = "重新生成"
                    yield SSEMessage.status("processing", f"根据反馈{action}中...")
                    if original_req:
                        stream_generator = agent.regenerate_with_improvements_stream(original_req, request.content)
                    else:
                        stream_generator = agent.regenerate_from_content_stream(request.content)
                elif request.feedback in ["需要优化", "满意"]:
                    action = "智能优化"
                    yield SSEMessage.status("processing", f"根据反馈{action}中...")
                    stream_generator = agent.optimize_content_stream(request.content)
                else:
                    yield SSEMessage.complete({
                        "action": "完成",
                        "content": request.content,
                        "message": "处理完成"
                    })
                    return
                
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
                if content:
                    add_content_to_history(request.user_id, content, action)
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
                    yield SSEMessage.error("生成内容为空")
                
            except Exception as e:
                logger.error(f"反馈处理过程中出错: {e}")
                yield SSEMessage.error(f"反馈处理失败: {str(e)}")
            finally:
                sse_manager.remove_connection(connection_id)
        
        return EventSourceResponse(sse_feedback_stream())
        
    except Exception as e:
        logger.error(f"流式反馈处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{user_id}", response_model=ApiResponse, tags=["版本管理"], summary="获取版本历史", description="获取指定用户的内容版本历史记录")
async def get_version_history(user_id: str):
    """获取版本历史"""
    try:
        session = get_user_session(user_id)
        
        return ApiResponse(
            success=True,
            message="获取版本历史成功",
            data={
                "content_history": session["content_history"],
                "current_version_index": session["current_version_index"],
                "total_versions": len(session["content_history"])
            }
        )
        
    except Exception as e:
        logger.error(f"获取版本历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/history/restore", response_model=ApiResponse, tags=["版本管理"], summary="恢复指定版本", description="将用户内容恢复到指定的历史版本")
async def restore_version(request: VersionRestoreRequest):
    """恢复指定版本"""
    try:
        session = get_user_session(request.user_id)
        
        if 0 <= request.version_index < len(session["content_history"]):
            session["current_version_index"] = request.version_index
            restored_content = session["content_history"][request.version_index]["content"]
            session["last_generated_content"] = restored_content
            
            return ApiResponse(
                success=True,
                message="版本恢复成功",
                data={
                    "content": restored_content,
                    "version": request.version_index + 1,
                    "version_info": session["content_history"][request.version_index]
                }
            )
        else:
            raise HTTPException(status_code=400, detail="无效的版本索引")
            
    except Exception as e:
        logger.error(f"版本恢复失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/history/{user_id}", response_model=ApiResponse, tags=["版本管理"], summary="清空用户历史", description="清空指定用户的所有历史记录和版本数据")
async def clear_history(user_id: str):
    """清空用户历史"""
    try:
        if user_id in user_sessions:
            del user_sessions[user_id]
        
        return ApiResponse(
            success=True,
            message="历史记录已清空",
            data={"user_id": user_id}
        )
        
    except Exception as e:
        logger.error(f"清空历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_server:app", host="0.0.0.0", port=8000, reload=True) 