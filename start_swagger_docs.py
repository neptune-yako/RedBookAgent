#!/usr/bin/env python3
"""
启动小红书文案生成智能体 API 服务器并打开Swagger文档
"""

import subprocess
import time
import webbrowser
import sys
import os
import signal

def start_server():
    """启动FastAPI服务器"""
    print("🚀 正在启动 FastAPI 服务器...")
    
    try:
        # 启动服务器进程
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "fastapi_server:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("⏳ 等待服务器启动...")
        time.sleep(3)  # 等待服务器启动
        
        return process
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")
        return None

def check_server():
    """检查服务器是否正常运行"""
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def open_docs():
    """打开Swagger文档"""
    docs_urls = [
        ("Swagger UI", "http://localhost:8000/docs"),
        ("ReDoc", "http://localhost:8000/redoc")
    ]
    
    print("\n📚 打开API文档...")
    for name, url in docs_urls:
        print(f"   - {name}: {url}")
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"   ⚠️  无法自动打开 {name}: {e}")
    
    print("\n💡 如果浏览器没有自动打开，请手动访问上述链接")

def main():
    """主函数"""
    print("=" * 60)
    print("🎯 小红书文案生成智能体 API 文档启动器")
    print("=" * 60)
    
    # 检查是否已有服务器运行
    if check_server():
        print("✅ 检测到API服务器已在运行")
        choice = input("是否打开文档? (y/n): ").lower().strip()
        if choice in ['y', 'yes', '']:
            open_docs()
        return
    
    # 启动服务器
    process = start_server()
    if not process:
        print("❌ 无法启动服务器")
        return
    
    try:
        # 检查服务器状态
        max_retries = 10
        for i in range(max_retries):
            if check_server():
                print("✅ API服务器启动成功!")
                break
            print(f"⏳ 等待服务器启动... ({i+1}/{max_retries})")
            time.sleep(2)
        else:
            print("❌ 服务器启动超时")
            process.terminate()
            return
        
        # 打开文档
        open_docs()
        
        print("\n" + "=" * 60)
        print("🎉 API 文档已启动! 主要功能:")
        print("   🎯 智能文案生成 - 根据主题和风格生成小红书文案")
        print("   🔄 内容优化 - 智能优化现有文案")
        print("   💬 对话聊天 - 与AI助手对话")
        print("   📝 反馈回环 - 基于反馈持续改进")
        print("   📚 版本管理 - 多版本内容管理")
        print("   🔄 实时流式 - SSE实时输出")
        print("=" * 60)
        print("\n📖 访问链接:")
        print("   Swagger UI: http://localhost:8000/docs")
        print("   ReDoc:      http://localhost:8000/redoc")
        print("   API根路径:  http://localhost:8000/")
        print("\n⌨️  按 Ctrl+C 停止服务器")
        
        # 保持服务器运行
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n\n🛑 正在停止服务器...")
            process.terminate()
            process.wait()
            print("✅ 服务器已停止")
    
    except Exception as e:
        print(f"❌ 运行过程中出错: {e}")
        if process:
            process.terminate()

if __name__ == "__main__":
    main() 