"""
业务逻辑服务
"""

import asyncio
from datetime import datetime
from typing import Dict, AsyncGenerator

from fastapi import HTTPException

from Agent.xiaohongshu_agent import XiaohongshuAgent, ContentRequest, ContentCategory
from .sse import SSEMessage, sse_manager
from .config import logger


class AgentService:
    """智能体服务"""
    
    def __init__(self):
        self.agent = None
    
    async def initialize(self):
        """初始化智能体"""
        try:
            logger.info("正在初始化小红书智能体...")
            self.agent = XiaohongshuAgent(enable_stream=True, enable_thinking=True)
            logger.info("智能体初始化完成")
            return True
        except Exception as e:
            logger.error(f"智能体初始化失败: {e}")
            return False
    
    def check_ready(self):
        """检查智能体是否准备就绪"""
        if self.agent is None:
            raise HTTPException(status_code=503, detail="智能体未初始化")
        return self.agent
    
    def parse_content_category(self, category_str: str) -> ContentCategory:
        """解析内容分类"""
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


class SessionService:
    """用户会话服务"""
    
    def __init__(self):
        self.user_sessions: Dict[str, Dict] = {}
    
    def get_user_session(self, user_id: str) -> Dict:
        """获取用户会话"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "content_history": [],
                "current_version_index": -1,
                "feedback_round": 0,
                "last_generated_content": "",
                "current_request": None,
                "created_at": datetime.now()
            }
        return self.user_sessions[user_id]
    
    def add_content_to_history(self, user_id: str, content: str, action: str = "生成"):
        """添加内容到版本历史"""
        session = self.get_user_session(user_id)
        version_info = {
            "content": content,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "version": len(session["content_history"]) + 1
        }
        session["content_history"].append(version_info)
        session["current_version_index"] = len(session["content_history"]) - 1
        session["last_generated_content"] = content
    
    def clear_user_session(self, user_id: str):
        """清空用户会话"""
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]


class StreamService:
    """流式处理服务"""
    
    def __init__(self, session_service: SessionService):
        self.session_service = session_service
    
    async def generate_with_sse(self, generator, user_id: str, action: str = "生成") -> AsyncGenerator[str, None]:
        """通用的SSE生成器包装器"""
        connection_id = f"{user_id}_{datetime.now().timestamp()}"
        
        try:
            # 添加连接
            sse_manager.add_connection(connection_id, user_id)
            
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
                self.session_service.add_content_to_history(user_id, content, action)
                session = self.session_service.get_user_session(user_id)
                
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


# 全局服务实例
agent_service = AgentService()
session_service = SessionService()
stream_service = StreamService(session_service) 