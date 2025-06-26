#!/usr/bin/env python3
"""
智能服务器启动脚本
自动检测可用端口并启动FastAPI服务
"""

import socket
import sys
import os
import subprocess
import logging
from typing import Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_port_available(host: str, port: int) -> bool:
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0
    except Exception as e:
        logger.warning(f"检查端口 {port} 时出错: {e}")
        return False

def find_available_port(host: str = "0.0.0.0", start_port: int = 8000, max_attempts: int = 100) -> Optional[int]:
    """寻找可用端口"""
    for port in range(start_port, start_port + max_attempts):
        if check_port_available(host, port):
            return port
    return None

def kill_process_on_port(port: int):
    """尝试杀死占用指定端口的进程 (Windows)"""
    try:
        # 查找占用端口的进程
        result = subprocess.run(
            ["netstat", "-ano", "|", "findstr", f":{port}"],
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if f":{port}" in line and "LISTENING" in line:
                    # 提取PID
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        if pid.isdigit():
                            logger.info(f"发现进程 {pid} 占用端口 {port}，尝试结束该进程...")
                            subprocess.run(["taskkill", "/F", "/PID", pid], shell=True)
                            return True
    except Exception as e:
        logger.warning(f"尝试结束占用端口 {port} 的进程时出错: {e}")
    return False

def start_server():
    """启动服务器"""
    host = "0.0.0.0"
    preferred_port = 8000
    
    logger.info("正在启动小红书智能体服务器...")
    
    # 首先检查首选端口
    if not check_port_available(host, preferred_port):
        logger.warning(f"端口 {preferred_port} 已被占用")
        
        # 询问用户是否要结束占用进程
        try:
            response = input(f"是否要尝试结束占用端口 {preferred_port} 的进程? (y/n): ").lower().strip()
            if response == 'y' or response == 'yes':
                if kill_process_on_port(preferred_port):
                    logger.info("已结束占用进程，等待端口释放...")
                    import time
                    time.sleep(2)
                    
                    if check_port_available(host, preferred_port):
                        logger.info(f"端口 {preferred_port} 现在可用")
                        port = preferred_port
                    else:
                        logger.warning("端口仍然被占用，寻找其他可用端口...")
                        port = find_available_port(host, preferred_port + 1)
                else:
                    logger.warning("无法结束占用进程，寻找其他可用端口...")
                    port = find_available_port(host, preferred_port + 1)
            else:
                logger.info("寻找其他可用端口...")
                port = find_available_port(host, preferred_port + 1)
        except KeyboardInterrupt:
            logger.info("用户取消操作")
            return
    else:
        port = preferred_port
    
    if port is None:
        logger.error("无法找到可用端口，请检查网络配置")
        return
    
    logger.info(f"将在端口 {port} 启动服务器")
    logger.info(f"访问地址: http://localhost:{port}")
    logger.info(f"API文档: http://localhost:{port}/docs")
    logger.info("按 Ctrl+C 停止服务器")
    
    try:
        # 启动uvicorn服务器
        # 检查是否存在新的模块化API
        if os.path.exists("API/main.py"):
            logger.info("使用新的模块化API")
            subprocess.run([
                sys.executable, "-m", "uvicorn", 
                "API.main:app", 
                "--host", host, 
                "--port", str(port),
                "--reload"
            ])
        else:
            logger.info("使用修复版服务器")
            subprocess.run([
                sys.executable, "-m", "uvicorn", 
                "fastapi_server_fixed:app", 
                "--host", host, 
                "--port", str(port),
                "--reload"
            ])
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    except Exception as e:
        logger.error(f"启动服务器时出错: {e}")

if __name__ == "__main__":
    start_server() 