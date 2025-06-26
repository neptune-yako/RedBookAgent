"""
SSE (Server-Sent Events) 相关功能
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any

from .config import logger, SSE_CONFIG


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
    
    def add_connection(self, connection_id: str, user_id: str):
        """添加连接"""
        self.connections[connection_id] = {
            "user_id": user_id,
            "connected_at": datetime.now(),
            "last_heartbeat": datetime.now()
        }
    
    def remove_connection(self, connection_id: str):
        """移除连接"""
        if connection_id in self.connections:
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
    
    async def cleanup_expired_connections(self):
        """清理过期连接"""
        current_time = datetime.now()
        expired_connections = []
        
        for conn_id, info in self.connections.items():
            # 如果超过配置的超时时间没有心跳，认为连接已断开
            if (current_time - info["last_heartbeat"]).seconds > SSE_CONFIG["connection_timeout"]:
                expired_connections.append(conn_id)
        
        for conn_id in expired_connections:
            self.remove_connection(conn_id)
            logger.info(f"清理过期连接: {conn_id}")


# 全局连接管理器实例
sse_manager = SSEConnectionManager()


async def heartbeat_task():
    """心跳任务，定期清理断开的连接"""
    while True:
        try:
            await sse_manager.cleanup_expired_connections()
            await asyncio.sleep(SSE_CONFIG["cleanup_interval"])
            
        except Exception as e:
            logger.error(f"心跳任务错误: {e}")
            await asyncio.sleep(SSE_CONFIG["cleanup_interval"]) 