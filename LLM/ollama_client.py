import requests
import json
import sys
from typing import Optional, Dict, Any, Generator


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        初始化Ollama客户端
        
        Args:
            base_url: Ollama服务器的URL，默认为本地11434端口
        """
        self.base_url = base_url
        self.model_name = "qwen3-redbook-q8:latest"
    
    def check_connection(self) -> bool:
        """
        检查Ollama服务连接状态
        
        Returns:
            bool: 连接成功返回True，否则返回False
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def list_models(self) -> Optional[Dict[str, Any]]:
        """
        获取可用模型列表
        
        Returns:
            Dict: 模型列表，失败返回None
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException:
            return None
    
    def check_model_exists(self) -> bool:
        """
        检查qwen3-redbook-q8:latest模型是否存在
        
        Returns:
            bool: 模型存在返回True，否则返回False
        """
        models = self.list_models()
        if models and 'models' in models:
            for model in models['models']:
                if model['name'] == self.model_name:
                    return True
        return False
    
    def pull_model(self) -> bool:
        """
        拉取模型（如果不存在）
        
        Returns:
            bool: 成功返回True，失败返回False
        """
        try:
            print(f"正在拉取模型 {self.model_name}...")
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": self.model_name},
                stream=True
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        if 'status' in data:
                            print(f"状态: {data['status']}")
                        if data.get('completed'):
                            print("模型拉取完成!")
                            return True
                return True
            return False
        except requests.exceptions.RequestException as e:
            print(f"拉取模型失败: {e}")
            return False
    
    def generate_stream(self, prompt: str) -> Generator[str, None, None]:
        """
        生成文本回复的流式生成器
        
        Args:
            prompt: 输入提示词
            
        Yields:
            str: 生成的文本片段
        """
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": True
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=(10, 60)  # (连接超时, 读取超时)
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        if 'response' in data:
                            chunk = data['response']
                            yield chunk
                        if data.get('done'):
                            break
        except requests.exceptions.RequestException as e:
            yield f"生成文本失败: {e}"
    
    def generate(self, prompt: str, stream: bool = False) -> Optional[str]:
        """
        生成文本回复
        
        Args:
            prompt: 输入提示词
            stream: 是否流式输出
            
        Returns:
            str: 生成的文本，失败返回None
        """
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": stream
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=stream
            )
            
            if response.status_code == 200:
                if stream:
                    # 流式输出
                    full_response = ""
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line)
                            if 'response' in data:
                                chunk = data['response']
                                print(chunk, end='', flush=True)
                                full_response += chunk
                            if data.get('done'):
                                print()  # 换行
                                return full_response
                    return full_response
                else:
                    # 非流式输出
                    result = response.json()
                    return result.get('response', '')
            return None
        except requests.exceptions.RequestException as e:
            print(f"生成文本失败: {e}")
            return None
    
    def chat_stream(self, messages: list) -> Generator[str, None, None]:
        """
        对话模式的流式生成器
        
        Args:
            messages: 对话历史，格式为[{"role": "user", "content": "..."}]
            
        Yields:
            str: 助手回复的文本片段
        """
        try:
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": True
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=True,
                timeout=(10, 60)  # (连接超时, 读取超时)
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        if 'message' in data and 'content' in data['message']:
                            chunk = data['message']['content']
                            yield chunk
                        if data.get('done'):
                            break
        except requests.exceptions.RequestException as e:
            yield f"对话失败: {e}"
    
    def chat(self, messages: list, stream: bool = False) -> Optional[str]:
        """
        对话模式
        
        Args:
            messages: 对话历史，格式为[{"role": "user", "content": "..."}]
            stream: 是否流式输出
            
        Returns:
            str: 助手回复，失败返回None
        """
        try:
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": stream
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=stream
            )
            
            if response.status_code == 200:
                if stream:
                    # 流式输出
                    full_response = ""
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line)
                            if 'message' in data and 'content' in data['message']:
                                chunk = data['message']['content']
                                print(chunk, end='', flush=True)
                                full_response += chunk
                            if data.get('done'):
                                print()  # 换行
                                return full_response
                    return full_response
                else:
                    # 非流式输出
                    result = response.json()
                    return result.get('message', {}).get('content', '')
            return None
        except requests.exceptions.RequestException as e:
            print(f"对话失败: {e}")
            return None


def main():
    """
    主函数，演示如何使用OllamaClient
    """
    # 创建客户端
    client = OllamaClient()
    
    # 检查连接
    print("检查Ollama服务连接...")
    if not client.check_connection():
        print("❌ 无法连接到Ollama服务。请确保Ollama正在运行。")
        print("启动命令: ollama serve")
        return
    
    print("✅ Ollama服务连接成功!")
    
    # 检查模型是否存在
    print(f"检查模型 {client.model_name} 是否存在...")
    if not client.check_model_exists():
        print("❌ 模型不存在，正在尝试拉取...")
        if not client.pull_model():
            print("❌ 模型拉取失败")
            return
    
    print("✅ 模型可用!")
    
    # 示例：简单生成
    print("\n=== 简单文本生成示例 ===")
    prompt = "请写一篇关于小红书的营销策略的短文"
    print(f"提示词: {prompt}")
    print("回复:")
    response = client.generate(prompt, stream=True)
    
    # 示例：对话模式
    print("\n\n=== 对话模式示例 ===")
    messages = [
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ]
    print("用户: 你好，请介绍一下你自己")
    print("助手: ", end="")
    response = client.chat(messages, stream=True)
    
    # 交互式对话
    print("\n\n=== 交互式对话 (输入 'quit' 退出) ===")
    conversation = []
    
    while True:
        user_input = input("\n你: ").strip()
        if user_input.lower() in ['quit', 'exit', '退出']:
            break
        
        conversation.append({"role": "user", "content": user_input})
        print("助手: ", end="")
        assistant_response = client.chat(conversation, stream=True)
        
        if assistant_response:
            conversation.append({"role": "assistant", "content": assistant_response})


if __name__ == "__main__":
    main() 