#!/usr/bin/env python3
"""
SSE客户端示例
演示如何使用小红书文案生成智能体的SSE API
"""

import requests
import json
import time
from typing import Dict, Any, Generator
import sseclient  # pip install sseclient-py


class XiaohongshuSSEClient:
    """小红书智能体SSE客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
        # 设置SSE相关的请求头
        self.session.headers.update({
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        })
    
    def create_sse_connection(self, user_id: str) -> Generator[Dict[str, Any], None, None]:
        """创建SSE连接
        
        Args:
            user_id: 用户ID
            
        Yields:
            Dict: SSE消息
        """
        try:
            response = self.session.post(
                f"{self.base_url}/sse/connect",
                json={"user_id": user_id},
                stream=True
            )
            
            if response.status_code == 200:
                client = sseclient.SSEClient(response)
                for event in client.events():
                    try:
                        data = json.loads(event.data)
                        yield {
                            "event": event.event,
                            "data": data,
                            "id": event.id,
                            "retry": event.retry
                        }
                    except json.JSONDecodeError:
                        # 处理非JSON数据
                        yield {
                            "event": event.event,
                            "data": event.data,
                            "raw": True
                        }
            else:
                print(f"连接失败: {response.status_code}")
                
        except Exception as e:
            print(f"SSE连接错误: {e}")
    
    def generate_content_stream(self, request_data: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """流式生成内容
        
        Args:
            request_data: 生成请求数据
            
        Yields:
            Dict: SSE消息
        """
        try:
            response = self.session.post(
                f"{self.base_url}/generate/stream",
                json=request_data,
                stream=True
            )
            
            if response.status_code == 200:
                client = sseclient.SSEClient(response)
                for event in client.events():
                    try:
                        data = json.loads(event.data)
                        yield {
                            "event": event.event,
                            "data": data
                        }
                    except json.JSONDecodeError:
                        continue
            else:
                print(f"生成失败: {response.status_code}")
                
        except Exception as e:
            print(f"生成错误: {e}")
    
    def chat_stream(self, request_data: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """流式对话
        
        Args:
            request_data: 对话请求数据
            
        Yields:
            Dict: SSE消息
        """
        try:
            response = self.session.post(
                f"{self.base_url}/chat/stream",
                json=request_data,
                stream=True
            )
            
            if response.status_code == 200:
                client = sseclient.SSEClient(response)
                for event in client.events():
                    try:
                        data = json.loads(event.data)
                        yield {
                            "event": event.event,
                            "data": data
                        }
                    except json.JSONDecodeError:
                        continue
            else:
                print(f"对话失败: {response.status_code}")
                
        except Exception as e:
            print(f"对话错误: {e}")
    
    def optimize_content_stream(self, request_data: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """流式优化内容
        
        Args:
            request_data: 优化请求数据
            
        Yields:
            Dict: SSE消息
        """
        try:
            response = self.session.post(
                f"{self.base_url}/optimize/stream",
                json=request_data,
                stream=True
            )
            
            if response.status_code == 200:
                client = sseclient.SSEClient(response)
                for event in client.events():
                    try:
                        data = json.loads(event.data)
                        yield {
                            "event": event.event,
                            "data": data
                        }
                    except json.JSONDecodeError:
                        continue
            else:
                print(f"优化失败: {response.status_code}")
                
        except Exception as e:
            print(f"优化错误: {e}")
    
    def feedback_stream(self, request_data: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """流式反馈处理
        
        Args:
            request_data: 反馈请求数据
            
        Yields:
            Dict: SSE消息
        """
        try:
            response = self.session.post(
                f"{self.base_url}/feedback/stream",
                json=request_data,
                stream=True
            )
            
            if response.status_code == 200:
                client = sseclient.SSEClient(response)
                for event in client.events():
                    try:
                        data = json.loads(event.data)
                        yield {
                            "event": event.event,
                            "data": data
                        }
                    except json.JSONDecodeError:
                        continue
            else:
                print(f"反馈处理失败: {response.status_code}")
                
        except Exception as e:
            print(f"反馈处理错误: {e}")
    
    def get_sse_status(self, user_id: str) -> Dict[str, Any]:
        """获取SSE连接状态
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 连接状态信息
        """
        try:
            response = self.session.get(f"{self.base_url}/sse/status/{user_id}")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"状态码: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}


def demo_content_generation():
    """演示内容生成"""
    print("🎯 演示SSE流式内容生成")
    print("=" * 50)
    
    client = XiaohongshuSSEClient()
    
    # 生成请求 - 启用思考模式
    request_data = {
        "category": "美食探店",
        "topic": "新开的日式料理店体验",
        "tone": "活泼可爱",
        "length": "中等",
        "keywords": ["日式料理", "新店", "美味"],
        "target_audience": "年轻女性",
        "special_requirements": "要有个人体验感",
        "user_id": "demo_user_001",
        "enable_thinking": True  # 启用思考模式，显示AI思考过程
    }
    
    print("📝 正在生成内容...")
    content = ""
    
    for message in client.generate_content_stream(request_data):
        event_type = message.get("event", "unknown")
        data = message.get("data", {})
        
        if event_type == "status":
            print(f"📊 状态: {data.get('status')} - {data.get('message', '')}")
        
        elif event_type == "chunk":
            chunk = data.get('chunk', '')
            content += chunk
            print(chunk, end='', flush=True)
        
        elif event_type == "complete":
            print(f"\n\n✅ 生成完成!")
            print(f"📈 统计: {data.get('total_chunks', 0)} 个块，总长度 {data.get('total_length', 0)} 字符")
            print(f"📝 版本: {data.get('version', 0)}")
        
        elif event_type == "error":
            print(f"\n❌ 错误: {data.get('message', '')}")
            break


def demo_chat():
    """演示对话功能"""
    print("\n💬 演示SSE流式对话")
    print("=" * 50)
    
    client = XiaohongshuSSEClient()
    
    request_data = {
        "message": "你好，我想要一些写小红书文案的技巧",
        "user_id": "demo_user_001",
        "enable_thinking": False  # 关闭思考模式，直接输出结果
    }
    
    print("🤖 AI回复:")
    
    for message in client.chat_stream(request_data):
        event_type = message.get("event", "unknown")
        data = message.get("data", {})
        
        if event_type == "status":
            print(f"📊 {data.get('message', '')}")
        
        elif event_type == "chunk":
            chunk = data.get('chunk', '')
            print(chunk, end='', flush=True)
        
        elif event_type == "complete":
            print(f"\n\n✅ 对话完成!")
        
        elif event_type == "error":
            print(f"\n❌ 错误: {data.get('message', '')}")
            break


def demo_thinking_mode():
    """演示思考模式的差异"""
    print("\n🧠 演示思考模式差异")
    print("=" * 50)
    
    client = XiaohongshuSSEClient()
    
    # 测试内容优化 - 启用思考模式
    print("1️⃣ 启用思考模式的优化:")
    print("-" * 30)
    
    request_data_thinking = {
        "content": "这家店很好吃，环境也不错",
        "user_id": "demo_user_001",
        "enable_thinking": True  # 启用思考模式
    }
    
    for message in client.optimize_content_stream(request_data_thinking):
        event_type = message.get("event", "unknown")
        data = message.get("data", {})
        
        if event_type == "chunk":
            chunk = data.get('chunk', '')
            print(chunk, end='', flush=True)
        elif event_type == "complete":
            print("\n✅ 思考模式优化完成!\n")
            break
        elif event_type == "error":
            print(f"\n❌ 错误: {data.get('message', '')}")
            break
    
    # 测试内容优化 - 关闭思考模式
    print("2️⃣ 关闭思考模式的优化:")
    print("-" * 30)
    
    request_data_no_thinking = {
        "content": "这家店很好吃，环境也不错",
        "user_id": "demo_user_002",
        "enable_thinking": False  # 关闭思考模式
    }
    
    for message in client.optimize_content_stream(request_data_no_thinking):
        event_type = message.get("event", "unknown")
        data = message.get("data", {})
        
        if event_type == "chunk":
            chunk = data.get('chunk', '')
            print(chunk, end='', flush=True)
        elif event_type == "complete":
            print("\n✅ 无思考模式优化完成!")
            break
        elif event_type == "error":
            print(f"\n❌ 错误: {data.get('message', '')}")
            break


def demo_connection_management():
    """演示连接管理"""
    print("\n🔗 演示SSE连接管理")
    print("=" * 50)
    
    client = XiaohongshuSSEClient()
    user_id = "demo_user_001"
    
    # 获取连接状态
    status = client.get_sse_status(user_id)
    print(f"📊 当前连接状态: {json.dumps(status, indent=2, ensure_ascii=False)}")
    
    print("\n🔄 创建SSE连接 (运行5秒后断开)...")
    
    connection_count = 0
    start_time = time.time()
    
    for message in client.create_sse_connection(user_id):
        event_type = message.get("event", "unknown")
        data = message.get("data", {})
        
        if event_type == "connected":
            print(f"✅ 连接建立: {data.get('connection_id')}")
        
        elif event_type == "heartbeat":
            connection_count += 1
            print(f"💓 心跳 #{connection_count}: {data.get('timestamp')}")
        
        # 5秒后断开连接
        if time.time() - start_time > 5:
            print("⏰ 5秒时间到，断开连接")
            break


def main():
    """主演示程序"""
    print("🚀 小红书智能体 SSE 客户端演示")
    print("=" * 60)
    
    try:
        # 演示内容生成
        demo_content_generation()
        
        # 演示对话
        demo_chat()
        
        # 演示思考模式差异
        demo_thinking_mode()
        
        # 演示连接管理
        demo_connection_management()
        
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {e}")
    
    print("\n🎉 演示结束！")


if __name__ == "__main__":
    main() 