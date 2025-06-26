"""
小红书文案生成智能体 - FastAPI后端服务（修复版）
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, ConfigDict
from sse_starlette.sse import EventSourceResponse

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局变量
agent_instance = None
user_sessions = {}

# =================== 数据模型 ===================

class ContentGenerationRequest(BaseModel):
    """内容生成请求模型"""
    category: str = Field(..., description="内容分类", example="美食探店")
    topic: str = Field(..., description="主题内容", example="新开的日式料理店体验")
    tone: str = Field(default="活泼可爱", description="语调风格", example="活泼可爱")
    length: str = Field(default="中等", description="内容长度", example="中等")
    keywords: Optional[List[str]] = Field(default=None, description="关键词列表")
    target_audience: str = Field(default="年轻女性", description="目标受众")
    special_requirements: str = Field(default="", description="特殊要求")
    user_id: str = Field(..., description="用户ID", example="user_001")

class ContentOptimizationRequest(BaseModel):
    """内容优化请求模型"""
    content: str = Field(..., description="待优化的内容")
    user_id: str = Field(..., description="用户ID")

class ChatRequest(BaseModel):
    """对话聊天请求模型"""
    message: str = Field(..., description="用户消息")
    user_id: str = Field(..., description="用户ID")

class ApiResponse(BaseModel):
    """标准API响应模型"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(), description="响应时间")

# =================== 工具函数 ===================

def get_user_session(user_id: str):
    """获取用户会话"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "content_history": [],
            "current_version_index": -1,
            "current_request": None
        }
    return user_sessions[user_id]

def check_agent_ready():
    """检查智能体是否准备就绪"""
    if agent_instance is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    return agent_instance

def parse_content_category(category_str: str):
    """解析内容分类字符串"""
    # 延迟导入，避免OpenAPI生成时的依赖问题
    try:
        from Agent.xiaohongshu_agent import ContentCategory
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
    except ImportError:
        # 如果导入失败，返回字符串
        return category_str

# =================== 应用生命周期 ===================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global agent_instance
    try:
        logger.info("正在初始化小红书智能体...")
        # 延迟导入，避免OpenAPI生成时的依赖问题
        from Agent.xiaohongshu_agent import XiaohongshuAgent
        agent_instance = XiaohongshuAgent(enable_stream=True, enable_thinking=True)
        logger.info("智能体初始化完成")
    except Exception as e:
        logger.error(f"智能体初始化失败: {e}")
        agent_instance = None
    
    yield
    logger.info("正在关闭服务...")

# =================== FastAPI应用 ===================

app = FastAPI(
    title="小红书文案生成智能体 API",
    description="基于大语言模型的智能小红书文案生成服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================== API路由 ===================

@app.get("/", response_model=ApiResponse, tags=["基础信息"])
async def root():
    """API基本信息"""
    return ApiResponse(
        success=True,
        message="小红书文案生成智能体 API 服务运行中",
        data={
            "version": "1.0.0",
            "status": "running",
            "agent_ready": agent_instance is not None
        }
    )

@app.get("/health", response_model=ApiResponse, tags=["基础信息"])
async def health_check():
    """健康检查"""
    try:
        agent = check_agent_ready()
        agent_status = True
        try:
            agent_status = agent.check_setup()
        except:
            agent_status = False
        
        return ApiResponse(
            success=True,
            message="服务健康",
            data={
                "agent_ready": agent_status,
                "active_sessions": len(user_sessions)
            }
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            message=f"服务异常: {str(e)}",
            data={"agent_ready": False}
        )

@app.post("/generate", response_model=ApiResponse, tags=["内容生成"])
async def generate_content(request: ContentGenerationRequest):
    """生成小红书文案"""
    try:
        agent = check_agent_ready()
        
        # 延迟导入Agent类型
        try:
            from Agent.xiaohongshu_agent import ContentRequest
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
        except ImportError:
            # 降级处理：直接传递字符串参数
            result = {
                "success": False,
                "error": "Agent模块导入失败，请检查环境配置"
            }
        
        if result.get("success"):
            session = get_user_session(request.user_id)
            session["current_request"] = request.dict()
            
            return ApiResponse(
                success=True,
                message="文案生成成功",
                data={"content": result["content"]}
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "生成失败"))
            
    except Exception as e:
        logger.error(f"生成文案失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize", response_model=ApiResponse, tags=["内容优化"])
async def optimize_content(request: ContentOptimizationRequest):
    """优化内容"""
    try:
        agent = check_agent_ready()
        
        result = agent.optimize_content(request.content)
        
        if result.get("success"):
            return ApiResponse(
                success=True,
                message="内容优化成功",
                data={"content": result["content"]}
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "优化失败"))
            
    except Exception as e:
        logger.error(f"优化内容失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ApiResponse, tags=["对话聊天"])
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

# =================== 流式端点（简化版） ===================

@app.post("/generate/stream", tags=["内容生成"])
async def generate_content_stream(request: ContentGenerationRequest):
    """流式生成小红书文案"""
    try:
        agent = check_agent_ready()
        
        async def sse_stream():
            try:
                # 延迟导入
                from Agent.xiaohongshu_agent import ContentRequest
                content_req = ContentRequest(
                    category=parse_content_category(request.category),
                    topic=request.topic,
                    tone=request.tone,
                    length=request.length,
                    keywords=request.keywords or [],
                    target_audience=request.target_audience,
                    special_requirements=request.special_requirements
                )
                
                # 流式生成
                content = ""
                for chunk in agent.generate_complete_post_stream(content_req):
                    if chunk:
                        content += chunk
                        yield f"data: {json.dumps({'chunk': chunk, 'type': 'content'}, ensure_ascii=False)}\n\n"
                        await asyncio.sleep(0.01)
                
                # 完成
                yield f"data: {json.dumps({'type': 'complete', 'content': content}, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
        
        return EventSourceResponse(sse_stream())
        
    except Exception as e:
        logger.error(f"流式生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 