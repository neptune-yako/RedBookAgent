#!/usr/bin/env python
"""
小红书文案生成智能体 - Web界面启动脚本
"""

import sys
import os
import subprocess
from pathlib import Path

def check_requirements():
    """检查依赖是否安装"""
    try:
        import streamlit
        import langchain
        import requests
        import pydantic
        print("✅ 所有依赖包已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_ollama():
    """检查Ollama服务状态"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama服务正在运行")
            return True
        else:
            print("❌ Ollama服务响应异常")
            return False
    except Exception:
        print("❌ 无法连接到Ollama服务")
        print("请确保Ollama正在运行: ollama serve")
        return False

def main():
    """主函数"""
    print("🚀 启动小红书文案生成智能体Web界面")
    print("=" * 50)
    
    # 检查依赖
    print("🔍 检查依赖包...")
    if not check_requirements():
        return
    
    # 检查Ollama
    print("🔍 检查Ollama服务...")
    if not check_ollama():
        print("\n💡 如果Ollama未安装，请访问: https://ollama.ai/")
        print("💡 启动Ollama: ollama serve")
        print("💡 下载模型: ollama pull qwen3-redbook-q8:latest")
        
        choice = input("\n是否继续启动Web界面？(y/n): ").lower()
        if choice != 'y':
            return
    
    # 启动Streamlit
    print("\n🎉 启动Web界面...")
    agent_path = Path(__file__).parent / "Agent" / "web_interface.py"
    
    if not agent_path.exists():
        print("❌ 找不到web_interface.py文件")
        return
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(agent_path), 
            "--server.port=8501",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 感谢使用小红书文案生成智能体！")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main() 