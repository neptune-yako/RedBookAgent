#!/usr/bin/env python3
"""
FastAPI服务启动脚本
"""

import uvicorn
import logging
import sys
import os
import importlib.util

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """检查关键依赖是否正确安装"""
    required_packages = {
        'fastapi': '0.108.0',
        'uvicorn': '0.24.0',
        'pydantic': '2.5.0'
    }
    
    missing_packages = []
    
    for package, min_version in required_packages.items():
        try:
            spec = importlib.util.find_spec(package)
            if spec is None:
                missing_packages.append(f"{package}>={min_version}")
            else:
                # 尝试导入包来检查是否有冲突
                try:
                    importlib.import_module(package)
                except ImportError as e:
                    print(f"⚠️  {package} 导入失败: {e}")
                    missing_packages.append(f"{package}>={min_version}")
        except Exception as e:
            print(f"⚠️  检查 {package} 时出错: {e}")
            missing_packages.append(f"{package}>={min_version}")
    
    if missing_packages:
        print("❌ 以下依赖包缺失或版本不兼容:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n🔧 请运行以下命令安装/更新依赖:")
        print("   pip install -r requirements.txt --upgrade")
        return False
    
    print("✅ 依赖检查通过")
    return True

def check_python_version():
    """检查Python版本兼容性"""
    if sys.version_info < (3, 8):
        print(f"❌ Python版本太低: {sys.version}")
        print("   需要Python 3.8或更高版本")
        return False
    
    print(f"✅ Python版本检查通过: {sys.version}")
    return True

def main():
    """启动FastAPI服务"""
    logging.basicConfig(level=logging.INFO)
    
    print("🔍 正在进行启动前检查...")
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    print("🚀 启动小红书文案生成智能体 FastAPI 服务...")
    print("📝 访问 http://localhost:8000 查看API")
    print("📚 访问 http://localhost:8000/docs 查看API文档")
    print("🔧 访问 http://localhost:8000/redoc 查看ReDoc文档")
    print("=" * 50)
    
    try:
        # 检查是否存在新的API模块
        if os.path.exists("API/main.py"):
            print("🎯 使用新的模块化API")
            uvicorn.run(
                "API.main:app",
                host="0.0.0.0",
                port=8000,
                reload=True,
                log_level="info",
                access_log=True,
                reload_dirs=["./"],
                reload_excludes=["*.pyc", "__pycache__", ".git"],
            )
        else:
            print("🔄 使用传统单体API")
            uvicorn.run(
                "fastapi_server:app",
                host="0.0.0.0",
                port=8000,
                reload=True,
                log_level="info",
                access_log=True,
                reload_dirs=["./"],
                reload_excludes=["*.pyc", "__pycache__", ".git"],
            )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 建议:")
        print("   1. 检查是否正确安装了所有依赖: pip install -r requirements.txt")
        print("   2. 检查Python和包版本兼容性")
        print("   3. 尝试重新创建虚拟环境")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("💡 详细错误信息:")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 