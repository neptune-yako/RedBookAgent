#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速测试 Ollama 连接和模型状态
"""

from ollama_client import OllamaClient

def test_connection():
    """
    测试 Ollama 连接和模型状态
    """
    print("🔍 测试 Ollama 连接状态...")
    print("=" * 50)
    
    client = OllamaClient()
    
    # 1. 测试连接
    print("1️⃣ 检查 Ollama 服务连接...")
    if client.check_connection():
        print("   ✅ Ollama 服务连接正常")
    else:
        print("   ❌ Ollama 服务连接失败")
        print("   💡 请确保 Ollama 正在运行: ollama serve")
        return False
    
    # 2. 列出所有模型
    print("\n2️⃣ 获取已安装的模型列表...")
    models = client.list_models()
    if models and 'models' in models:
        print(f"   📋 发现 {len(models['models'])} 个已安装的模型:")
        for i, model in enumerate(models['models'], 1):
            name = model.get('name', 'Unknown')
            size = model.get('size', 0)
            size_gb = size / (1024**3) if size > 0 else 0
            print(f"   {i}. {name} ({size_gb:.1f}GB)")
    else:
        print("   ⚠️ 未找到已安装的模型")
    
    # 3. 检查目标模型
    print(f"\n3️⃣ 检查目标模型 '{client.model_name}'...")
    if client.check_model_exists():
        print("   ✅ 目标模型已安装并可用")
        
        # 4. 测试简单生成
        print("\n4️⃣ 测试模型响应...")
        test_prompt = "你好"
        print(f"   📝 测试提示词: '{test_prompt}'")
        print("   🤖 模型回复: ", end="", flush=True)
        
        try:
            response = client.generate(test_prompt, stream=False)
            if response:
                print(f"'{response[:50]}{'...' if len(response) > 50 else ''}'")
                print("   ✅ 模型响应正常")
            else:
                print("\n   ❌ 模型未返回响应")
                return False
        except Exception as e:
            print(f"\n   ❌ 模型测试失败: {e}")
            return False
            
    else:
        print("   ❌ 目标模型未安装")
        print(f"   💡 请运行: ollama pull {client.model_name}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过! 您可以开始使用 Qwen3-Redbook 模型了!")
    print("\n📖 使用方法:")
    print("   • 完整演示: python ollama_client.py")
    print("   • 简单聊天: python simple_chat.py")
    return True

if __name__ == "__main__":
    test_connection() 