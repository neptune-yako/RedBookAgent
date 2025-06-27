#!/usr/bin/env python3
"""
小红书文案生成智能体 - HTTP/2.0 服务器启动脚本
支持Hypercorn ASGI服务器，提供HTTP/2.0和HTTP/3功能
"""

import os
import sys
import logging
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime, timedelta

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from API.config import HTTP2_CONFIG, SERVER_CONFIG, RUNTIME_CONFIG, logger

def check_dependencies():
    """检查HTTP/2.0相关依赖是否正确安装"""
    required_packages = {
        'hypercorn': '0.17.0',
        'h2': '4.1.0',
        'h11': '0.14.0',
        'hpack': '4.0.0',
        'httpx': '0.24.0',
        'cryptography': '3.4.0'
    }
    
    missing_packages = []
    
    for package, min_version in required_packages.items():
        try:
            spec = importlib.util.find_spec(package)
            if spec is None:
                missing_packages.append(f"{package}>={min_version}")
            else:
                try:
                    importlib.import_module(package)
                except ImportError as e:
                    print(f"⚠️  {package} 导入失败: {e}")
                    missing_packages.append(f"{package}>={min_version}")
        except Exception as e:
            print(f"⚠️  检查 {package} 时出错: {e}")
            missing_packages.append(f"{package}>={min_version}")
    
    if missing_packages:
        print("❌ 以下HTTP/2.0依赖包缺失或版本不兼容:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n🔧 请运行以下命令安装/更新依赖:")
        print("   pip install -r requirements.txt --upgrade")
        return False
    
    print("✅ HTTP/2.0依赖检查通过")
    return True

def check_python_version():
    """检查Python版本兼容性"""
    if sys.version_info < (3, 8):
        print(f"❌ Python版本太低: {sys.version}")
        print("   HTTP/2.0功能需要Python 3.8或更高版本")
        return False
    
    print(f"✅ Python版本检查通过: {sys.version}")
    return True

def generate_self_signed_certificate():
    """生成自签名SSL证书用于HTTP/2.0测试"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import ipaddress
        
        # 创建证书目录
        cert_dir = Path("certs")
        cert_dir.mkdir(exist_ok=True)
        
        cert_file = cert_dir / "cert.pem"
        key_file = cert_dir / "key.pem"
        
        # 如果证书已存在且未过期，跳过生成
        if cert_file.exists() and key_file.exists():
            try:
                with open(cert_file, 'rb') as f:
                    cert = x509.load_pem_x509_certificate(f.read())
                    if cert.not_valid_after > datetime.now():
                        print("✅ 发现有效的SSL证书，跳过生成")
                        return str(key_file), str(cert_file)
            except Exception:
                pass
        
        print("🔐 正在生成自签名SSL证书...")
        
        # 生成私钥
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # 生成证书
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Beijing"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Beijing"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "XiaoHongShu Agent"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.now()
        ).not_valid_after(
            datetime.now() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("127.0.0.1"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                x509.IPAddress(ipaddress.IPv6Address("::1")),
            ]),
            critical=False,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                content_commitment=False,
                data_encipherment=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).add_extension(
            x509.ExtendedKeyUsage([
                x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
            ]),
            critical=True,
        ).sign(private_key, hashes.SHA256())
        
        # 保存私钥
        with open(key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # 保存证书
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        print(f"✅ SSL证书生成完成:")
        print(f"   - 私钥: {key_file}")
        print(f"   - 证书: {cert_file}")
        print(f"   - 有效期: 1年")
        
        return str(key_file), str(cert_file)
        
    except ImportError:
        print("❌ cryptography包未安装，无法生成SSL证书")
        print("   请安装: pip install cryptography")
        return None, None
    except Exception as e:
        print(f"❌ 生成SSL证书失败: {e}")
        return None, None

def start_hypercorn_server(ssl_enabled=False):
    """启动Hypercorn HTTP/2.0服务器"""
    
    # 基础命令 - 修正参数格式
    if ssl_enabled:
        # SSL模式
        key_file, cert_file = generate_self_signed_certificate()
        if key_file and cert_file:
            cmd = [
                sys.executable, "-m", "hypercorn",
                "API.main:app",
                "--bind", f"{SERVER_CONFIG['host']}:{RUNTIME_CONFIG['ssl_port']}",
                "--workers", str(RUNTIME_CONFIG['workers']),
                "--backlog", str(SERVER_CONFIG['backlog']),
                "--keep-alive", str(SERVER_CONFIG['timeout_keep_alive']),
                "--keyfile", key_file,
                "--certfile", cert_file,
                "--access-logfile", "-",
                "--log-level", "info"
            ]
            print(f"🔒 HTTPS服务器将运行在: https://localhost:{RUNTIME_CONFIG['ssl_port']}")
            print(f"🌐 HTTP/2.0 已启用 (通过HTTPS)")
        else:
            print("⚠️  SSL证书生成失败，回退到HTTP模式")
            ssl_enabled = False
    
    if not ssl_enabled:
        # HTTP模式
        cmd = [
            sys.executable, "-m", "hypercorn",
            "API.main:app",
            "--bind", f"{SERVER_CONFIG['host']}:{RUNTIME_CONFIG['port']}",
            "--workers", str(RUNTIME_CONFIG['workers']),
            "--backlog", str(SERVER_CONFIG['backlog']),
            "--keep-alive", str(SERVER_CONFIG['timeout_keep_alive']),
            "--access-logfile", "-",
            "--log-level", "info"
        ]
        print(f"🌐 HTTP服务器将运行在: http://localhost:{RUNTIME_CONFIG['port']}")
        print(f"📝 注意: HTTP/2.0需要HTTPS才能在大多数浏览器中工作")
    
    # 输出服务器信息
    print("=" * 60)
    print("🚀 启动小红书文案生成智能体 HTTP/2.0 服务...")
    print(f"📊 服务器: Hypercorn ASGI")
    print(f"🔧 工作进程: {RUNTIME_CONFIG['workers']}")
    
    if ssl_enabled:
        print(f"🔗 协议支持: HTTP/1.1, HTTP/2.0")
        print(f"📚 API文档: https://localhost:{RUNTIME_CONFIG['ssl_port']}/docs")
        print(f"🔧 ReDoc文档: https://localhost:{RUNTIME_CONFIG['ssl_port']}/redoc")
    else:
        print(f"🔗 协议支持: HTTP/1.1")
        print(f"📚 API文档: http://localhost:{RUNTIME_CONFIG['port']}/docs")
        print(f"🔧 ReDoc文档: http://localhost:{RUNTIME_CONFIG['port']}/redoc")
    
    print("=" * 60)
    print("命令行:", " ".join(cmd))  # 调试信息
    print("=" * 60)
    
    try:
        # 启动服务器
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务器启动失败: {e}")
        print(f"💡 请检查端口{RUNTIME_CONFIG['ssl_port' if ssl_enabled else 'port']}是否被占用")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        sys.exit(1)

def start_uvicorn_fallback():
    """回退到Uvicorn服务器（HTTP/1.1）"""
    print("⚠️  Hypercorn不可用，回退到Uvicorn服务器")
    print("📝 注意: Uvicorn仅支持HTTP/1.1，如需HTTP/2.0请安装Hypercorn")
    
    try:
        import uvicorn
        uvicorn.run(
            "API.main:app",
            host=SERVER_CONFIG['host'],
            port=RUNTIME_CONFIG['port'],
            reload=True,
            log_level="info",
            access_log=True,
        )
    except ImportError:
        print("❌ Uvicorn也未安装，无法启动服务器")
        print("   请安装: pip install uvicorn[standard]")
        sys.exit(1)

def main():
    """主函数"""
    logging.basicConfig(level=logging.INFO)
    
    print("🔍 正在进行HTTP/2.0启动前检查...")
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 检查依赖
    if not check_dependencies():
        print("💡 提示: 可以使用传统的HTTP/1.1模式启动")
        choice = input("是否回退到HTTP/1.1模式? (y/N): ").lower()
        if choice == 'y':
            start_uvicorn_fallback()
            return
        sys.exit(1)
    
    # 询问是否启用SSL
    ssl_choice = input("是否启用HTTPS (推荐，HTTP/2.0最佳体验)? (Y/n): ").lower()
    ssl_enabled = ssl_choice != 'n'
    
    try:
        start_hypercorn_server(ssl_enabled)
    except Exception as e:
        print(f"❌ Hypercorn启动失败: {e}")
        print("🔄 尝试回退到Uvicorn...")
        start_uvicorn_fallback()

if __name__ == "__main__":
    main() 