#!/usr/bin/env python3
"""
环境检查脚本 - 快速诊断常见问题
"""

import sys
import socket
import subprocess
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version >= (3, 8):
        logger.info(f"✓ Python版本 {version.major}.{version.minor}.{version.micro} 满足要求")
        return True
    else:
        logger.error(f"✗ Python版本 {version.major}.{version.minor}.{version.micro} 过低，需要3.8+")
        return False

def check_port_availability(port=8000):
    """检查端口可用性"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            if result != 0:
                logger.info(f"✓ 端口 {port} 可用")
                return True
            else:
                logger.warning(f"✗ 端口 {port} 已被占用")
                return False
    except Exception as e:
        logger.error(f"检查端口时出错: {e}")
        return False

def check_ollama_service():
    """检查Ollama服务"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            logger.info("✓ Ollama服务运行正常")
            return True
        else:
            logger.warning("✗ Ollama服务可能未启动")
            return False
    except subprocess.TimeoutExpired:
        logger.warning("✗ Ollama服务响应超时")
        return False
    except FileNotFoundError:
        logger.error("✗ Ollama未安装或不在PATH中")
        return False
    except Exception as e:
        logger.error(f"检查Ollama时出错: {e}")
        return False

def check_required_packages():
    """检查必需的Python包"""
    packages = ['fastapi', 'uvicorn', 'pydantic', 'langchain', 'streamlit']
    missing = []
    
    for package in packages:
        try:
            __import__(package)
            logger.info(f"✓ {package} 已安装")
        except ImportError:
            logger.warning(f"✗ {package} 未安装")
            missing.append(package)
    
    if missing:
        logger.error(f"缺少包: {', '.join(missing)}")
        logger.info("运行: pip install " + " ".join(missing))
        return False
    return True

def main():
    """主检查函数"""
    logger.info("开始环境检查...")
    
    checks = [
        ("Python版本", check_python_version),
        ("端口可用性", check_port_availability), 
        ("Ollama服务", check_ollama_service),
        ("Python包", check_required_packages)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        logger.info(f"\n检查 {name}...")
        if check_func():
            passed += 1
    
    logger.info(f"\n检查完成: {passed}/{total} 项通过")
    
    if passed == total:
        logger.info("✅ 环境检查通过，可以启动服务")
        return True
    else:
        logger.warning("⚠️  环境检查发现问题，请修复后再启动")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 