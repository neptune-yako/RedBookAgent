#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ollama_client import OllamaClient

def simple_chat():
    """
    简单的聊天示例
    """
    print("🤖 Qwen3-Redbook 聊天机器人")
    print("=" * 40)
    
    # 创建客户端
    client = OllamaClient()
    
    # 检查连接和模型
    if not client.check_connection():
        print("❌ 无法连接到Ollama服务")
        print("请先启动Ollama服务: ollama serve")
        return
    
    if not client.check_model_exists():
        print(f"❌ 模型 {client.model_name} 不存在")
        print("请先拉取模型: ollama pull qwen3-redbook-q8:latest")
        return
    
    print("✅ 连接成功! 开始聊天吧!")
    print("输入 'quit' 或 '退出' 来结束对话\n")
    
    # 开始对话
    conversation = []
    
    while True:
        try:
            user_input = input("💬 你: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("👋 再见!")
                break
            
            if not user_input:
                continue
            
            conversation.append({"role": "user", "content": user_input})
            
            print("🤖 助手: ", end="", flush=True)
            response = client.chat(conversation, stream=True)
            
            if response:
                conversation.append({"role": "assistant", "content": response})
            else:
                print("抱歉，生成回复时出现了错误。")
                
        except KeyboardInterrupt:
            print("\n\n👋 再见!")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")

if __name__ == "__main__":
    simple_chat() 