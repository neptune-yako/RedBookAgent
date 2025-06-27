#!/usr/bin/env python3
"""
HTTP/2.0 快速测试脚本
用于验证小红书文案生成智能体的HTTP/2.0功能是否正常工作
"""

import asyncio
import httpx
import time
import json
from typing import Dict, Any

class HTTP2QuickTest:
    """HTTP/2.0快速测试类"""
    
    def __init__(self):
        self.http1_url = "http://localhost:8000"
        self.http2_url = "https://localhost:8443"
        self.test_data = {
            "topic": "春季护肤",
            "category": "beauty",
            "tone": "friendly",
            "target_audience": "年轻女性",
            "user_id": "test_user"
        }
    
    async def test_connection(self, url: str, http2: bool = False) -> Dict[str, Any]:
        """测试连接并返回结果"""
        protocol = "HTTP/2.0" if http2 else "HTTP/1.1"
        print(f"🔍 测试 {protocol} 连接: {url}")
        
        try:
            timeout = httpx.Timeout(10.0, connect=5.0)
            async with httpx.AsyncClient(http2=http2, timeout=timeout, verify=False) as client:
                # 测试基本连接
                start_time = time.time()
                response = await client.get(f"{url}/health")
                connection_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = {
                        "success": True,
                        "status_code": response.status_code,
                        "protocol": getattr(response, 'http_version', 'unknown'),
                        "connection_time": round(connection_time * 1000, 2),  # 毫秒
                        "headers": dict(response.headers),
                        "response_size": len(response.content)
                    }
                    print(f"✅ {protocol} 连接成功")
                    print(f"   协议版本: {result['protocol']}")
                    print(f"   响应时间: {result['connection_time']}ms")
                    return result
                else:
                    print(f"❌ {protocol} 连接失败: HTTP {response.status_code}")
                    return {"success": False, "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            print(f"❌ {protocol} 连接失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_api_endpoint(self, url: str, http2: bool = False) -> Dict[str, Any]:
        """测试API端点"""
        protocol = "HTTP/2.0" if http2 else "HTTP/1.1"
        print(f"🔍 测试 {protocol} API端点: {url}/generate/async")
        
        try:
            timeout = httpx.Timeout(30.0, connect=10.0)
            async with httpx.AsyncClient(http2=http2, timeout=timeout, verify=False) as client:
                start_time = time.time()
                response = await client.post(f"{url}/generate/async", json=self.test_data)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    result = {
                        "success": True,
                        "status_code": response.status_code,
                        "protocol": getattr(response, 'http_version', 'unknown'),
                        "response_time": round(response_time * 1000, 2),
                        "task_id": data.get("data", {}).get("task_id", "unknown"),
                        "response_size": len(response.content)
                    }
                    print(f"✅ {protocol} API调用成功")
                    print(f"   任务ID: {result['task_id']}")
                    print(f"   响应时间: {result['response_time']}ms")
                    return result
                else:
                    print(f"❌ {protocol} API调用失败: HTTP {response.status_code}")
                    return {"success": False, "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            print(f"❌ {protocol} API调用失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_concurrent_requests(self, url: str, http2: bool = False, num_requests: int = 5) -> Dict[str, Any]:
        """测试并发请求"""
        protocol = "HTTP/2.0" if http2 else "HTTP/1.1"
        print(f"🔍 测试 {protocol} 并发请求 ({num_requests}个)...")
        
        try:
            limits = httpx.Limits(
                max_connections=10 if not http2 else 5,  # HTTP/2使用更少连接
                max_keepalive_connections=10 if not http2 else 5
            )
            timeout = httpx.Timeout(30.0, connect=10.0)
            
            async with httpx.AsyncClient(http2=http2, limits=limits, timeout=timeout, verify=False) as client:
                start_time = time.time()
                
                # 创建并发任务
                tasks = []
                for i in range(num_requests):
                    task_data = {**self.test_data, "user_id": f"test_user_{i}"}
                    task = client.post(f"{url}/generate/async", json=task_data)
                    tasks.append(task)
                
                # 并发执行
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                total_time = time.time() - start_time
                
                # 统计结果
                successful = 0
                failed = 0
                response_times = []
                
                for response in responses:
                    if isinstance(response, Exception):
                        failed += 1
                    elif hasattr(response, 'status_code') and response.status_code == 200:
                        successful += 1
                    else:
                        failed += 1
                
                result = {
                    "success": successful > 0,
                    "total_requests": num_requests,
                    "successful": successful,
                    "failed": failed,
                    "total_time": round(total_time * 1000, 2),
                    "requests_per_second": round(successful / total_time, 2) if total_time > 0 else 0
                }
                
                print(f"✅ {protocol} 并发测试完成")
                print(f"   成功请求: {successful}/{num_requests}")
                print(f"   总耗时: {result['total_time']}ms")
                print(f"   每秒请求数: {result['requests_per_second']} RPS")
                
                return result
                
        except Exception as e:
            print(f"❌ {protocol} 并发测试失败: {e}")
            return {"success": False, "error": str(e)}
    
    def print_comparison(self, http1_result: Dict[str, Any], http2_result: Dict[str, Any]):
        """打印对比结果"""
        print("\n" + "=" * 60)
        print("📊 HTTP/1.1 vs HTTP/2.0 对比结果")
        print("=" * 60)
        
        if http1_result.get("success") and http2_result.get("success"):
            # 响应时间对比
            http1_time = http1_result.get("response_time", 0)
            http2_time = http2_result.get("response_time", 0)
            
            if http1_time > 0 and http2_time > 0:
                improvement = ((http1_time - http2_time) / http1_time) * 100
                print(f"⚡ 响应时间对比:")
                print(f"   HTTP/1.1: {http1_time}ms")
                print(f"   HTTP/2.0: {http2_time}ms")
                print(f"   性能提升: {improvement:+.1f}%")
            
            # 并发性能对比
            if "requests_per_second" in http1_result and "requests_per_second" in http2_result:
                http1_rps = http1_result["requests_per_second"]
                http2_rps = http2_result["requests_per_second"]
                
                if http1_rps > 0:
                    rps_improvement = ((http2_rps - http1_rps) / http1_rps) * 100
                    print(f"🚀 并发性能对比:")
                    print(f"   HTTP/1.1: {http1_rps} RPS")
                    print(f"   HTTP/2.0: {http2_rps} RPS")
                    print(f"   吞吐量提升: {rps_improvement:+.1f}%")
        else:
            print("⚠️  部分测试失败，无法进行完整对比")
    
    async def run_full_test(self):
        """运行完整测试"""
        print("🚀 小红书文案生成智能体 - HTTP/2.0快速测试")
        print("=" * 60)
        print("📋 测试计划:")
        print("1. 连接测试")
        print("2. API端点测试")
        print("3. 并发性能测试")
        print("4. 结果对比")
        print("-" * 60)
        
        # 1. 连接测试
        print("\n📡 第一步：连接测试")
        http1_conn = await self.test_connection(self.http1_url, False)
        http2_conn = await self.test_connection(self.http2_url, True)
        
        if not http1_conn.get("success") and not http2_conn.get("success"):
            print("\n❌ 所有连接测试失败，请检查服务器是否启动")
            print("💡 启动建议:")
            print("   HTTP/1.1: python start_api.py")
            print("   HTTP/2.0: python start_http2.py")
            return
        
        # 2. API端点测试
        print("\n🔧 第二步：API端点测试")
        http1_api = {}
        http2_api = {}
        
        if http1_conn.get("success"):
            http1_api = await self.test_api_endpoint(self.http1_url, False)
        
        if http2_conn.get("success"):
            http2_api = await self.test_api_endpoint(self.http2_url, True)
        
        # 3. 并发性能测试
        print("\n⚡ 第三步：并发性能测试")
        http1_concurrent = {}
        http2_concurrent = {}
        
        if http1_api.get("success"):
            http1_concurrent = await self.test_concurrent_requests(self.http1_url, False, 5)
            await asyncio.sleep(1)  # 避免服务器压力
        
        if http2_api.get("success"):
            http2_concurrent = await self.test_concurrent_requests(self.http2_url, True, 5)
        
        # 4. 结果对比
        print("\n📊 第四步：结果对比")
        if http1_api.get("success") or http2_api.get("success"):
            self.print_comparison(
                {**http1_api, **http1_concurrent} if http1_api.get("success") else {},
                {**http2_api, **http2_concurrent} if http2_api.get("success") else {}
            )
        
        # 总结
        print(f"\n✅ 测试完成!")
        print("💡 建议:")
        if http2_conn.get("success"):
            print("   - HTTP/2.0功能正常，建议在生产环境使用以获得更好性能")
            print("   - 确保客户端支持HTTP/2.0以充分利用性能优势")
        if http1_conn.get("success"):
            print("   - HTTP/1.1服务可作为备用方案")
        print("   - 详细配置请参考 docs/HTTP2_UPGRADE_GUIDE.md")

async def main():
    """主函数"""
    tester = HTTP2QuickTest()
    await tester.run_full_test()

if __name__ == "__main__":
    # 检查依赖
    try:
        import httpx
    except ImportError:
        print("❌ 请安装httpx: pip install 'httpx[http2]'")
        exit(1)
    
    # 运行测试
    asyncio.run(main()) 