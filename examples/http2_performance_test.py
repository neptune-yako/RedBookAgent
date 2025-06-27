#!/usr/bin/env python3
"""
HTTP/2.0 性能测试脚本
比较HTTP/1.1和HTTP/2.0在小红书文案生成智能体中的性能差异
"""

import asyncio
import time
import statistics
import httpx
import json
from typing import List, Dict, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class TestResult:
    """测试结果数据类"""
    protocol: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    requests_per_second: float
    concurrent_streams: int = 1

class HTTP2PerformanceTester:
    """HTTP/2.0性能测试器"""
    
    def __init__(self, base_url_http1: str = "http://localhost:8000", 
                 base_url_http2: str = "https://localhost:8443"):
        self.base_url_http1 = base_url_http1
        self.base_url_http2 = base_url_http2
        self.test_data = {
            "topic": "春季护肤",
            "category": "beauty",
            "tone": "friendly",
            "target_audience": "年轻女性",
            "user_id": "test_user",
            "language": "zh-CN"
        }
    
    async def make_single_request(self, client: httpx.AsyncClient, url: str, data: Dict[str, Any]) -> float:
        """发送单个请求并返回响应时间"""
        start_time = time.time()
        try:
            response = await client.post(url, json=data, timeout=30.0)
            response.raise_for_status()
            return time.time() - start_time
        except Exception as e:
            print(f"请求失败: {e}")
            return -1
    
    async def test_http1_concurrent(self, num_requests: int = 50, max_concurrent: int = 10) -> TestResult:
        """测试HTTP/1.1并发性能"""
        print(f"🔄 测试HTTP/1.1并发性能 ({num_requests}个请求, {max_concurrent}并发)...")
        
        url = f"{self.base_url_http1}/generate/async"
        response_times = []
        successful = 0
        failed = 0
        
        start_time = time.time()
        
        # 使用连接池限制并发连接数
        limits = httpx.Limits(max_connections=max_concurrent, max_keepalive_connections=max_concurrent)
        timeout = httpx.Timeout(30.0, connect=10.0)
        
        async with httpx.AsyncClient(limits=limits, timeout=timeout, verify=False) as client:
            # 创建信号量控制并发数
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def bounded_request():
                async with semaphore:
                    return await self.make_single_request(client, url, self.test_data)
            
            # 并发发送请求
            tasks = [bounded_request() for _ in range(num_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception) or result == -1:
                    failed += 1
                else:
                    successful += 1
                    response_times.append(result)
        
        total_time = time.time() - start_time
        
        return TestResult(
            protocol="HTTP/1.1",
            total_requests=num_requests,
            successful_requests=successful,
            failed_requests=failed,
            total_time=total_time,
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            min_response_time=min(response_times) if response_times else 0,
            max_response_time=max(response_times) if response_times else 0,
            requests_per_second=successful / total_time if total_time > 0 else 0,
            concurrent_streams=max_concurrent
        )
    
    async def test_http2_concurrent(self, num_requests: int = 50, max_concurrent: int = 10) -> TestResult:
        """测试HTTP/2.0并发性能"""
        print(f"🚀 测试HTTP/2.0并发性能 ({num_requests}个请求, {max_concurrent}并发)...")
        
        url = f"{self.base_url_http2}/generate/async"
        response_times = []
        successful = 0
        failed = 0
        
        start_time = time.time()
        
        # HTTP/2客户端配置
        limits = httpx.Limits(max_connections=5, max_keepalive_connections=5)  # HTTP/2使用更少连接
        timeout = httpx.Timeout(30.0, connect=10.0)
        
        async with httpx.AsyncClient(http2=True, limits=limits, timeout=timeout, verify=False) as client:
            # HTTP/2支持多路复用，可以更高的并发
            semaphore = asyncio.Semaphore(max_concurrent * 2)  # HTTP/2可以处理更多并发
            
            async def bounded_request():
                async with semaphore:
                    return await self.make_single_request(client, url, self.test_data)
            
            # 并发发送请求
            tasks = [bounded_request() for _ in range(num_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception) or result == -1:
                    failed += 1
                else:
                    successful += 1
                    response_times.append(result)
        
        total_time = time.time() - start_time
        
        return TestResult(
            protocol="HTTP/2.0",
            total_requests=num_requests,
            successful_requests=successful,
            failed_requests=failed,
            total_time=total_time,
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            min_response_time=min(response_times) if response_times else 0,
            max_response_time=max(response_times) if response_times else 0,
            requests_per_second=successful / total_time if total_time > 0 else 0,
            concurrent_streams=max_concurrent * 2
        )
    
    def print_results(self, results: List[TestResult]):
        """打印测试结果对比"""
        print("\n" + "=" * 80)
        print("📊 HTTP/1.1 vs HTTP/2.0 性能测试结果")
        print("=" * 80)
        
        for result in results:
            print(f"\n🔗 协议: {result.protocol}")
            print(f"📊 总请求数: {result.total_requests}")
            print(f"✅ 成功请求: {result.successful_requests}")
            print(f"❌ 失败请求: {result.failed_requests}")
            print(f"⏱️ 总耗时: {result.total_time:.2f}秒")
            print(f"📈 平均响应时间: {result.avg_response_time:.3f}秒")
            print(f"⚡ 最快响应: {result.min_response_time:.3f}秒")
            print(f"🐌 最慢响应: {result.max_response_time:.3f}秒")
            print(f"🚀 每秒请求数: {result.requests_per_second:.2f} RPS")
            print(f"🔄 并发流数: {result.concurrent_streams}")
        
        # 计算性能提升
        if len(results) == 2:
            http1_result = next(r for r in results if r.protocol == "HTTP/1.1")
            http2_result = next(r for r in results if r.protocol == "HTTP/2.0")
            
            if http1_result.requests_per_second > 0:
                rps_improvement = ((http2_result.requests_per_second - http1_result.requests_per_second) 
                                 / http1_result.requests_per_second) * 100
                
                time_improvement = ((http1_result.avg_response_time - http2_result.avg_response_time) 
                                  / http1_result.avg_response_time) * 100
                
                print(f"\n🌟 性能提升对比:")
                print(f"📈 RPS提升: {rps_improvement:+.1f}%")
                print(f"⚡ 响应时间改善: {time_improvement:+.1f}%")
    
    async def run_comprehensive_test(self):
        """运行综合性能测试"""
        print("🎯 开始HTTP/2.0综合性能测试...")
        print("测试场景: 小红书文案生成API并发请求")
        
        test_scenarios = [
            (20, 5),   # 20个请求，5并发
            (50, 10),  # 50个请求，10并发
            (100, 20), # 100个请求，20并发
        ]
        
        all_results = []
        
        for num_requests, concurrency in test_scenarios:
            print(f"\n📋 测试场景: {num_requests}个请求，{concurrency}并发")
            print("-" * 50)
            
            # 测试HTTP/1.1
            try:
                http1_result = await self.test_http1_concurrent(num_requests, concurrency)
                all_results.append(http1_result)
            except Exception as e:
                print(f"❌ HTTP/1.1测试失败: {e}")
                continue
            
            # 等待一秒避免服务器压力
            await asyncio.sleep(1)
            
            # 测试HTTP/2.0
            try:
                http2_result = await self.test_http2_concurrent(num_requests, concurrency)
                all_results.append(http2_result)
            except Exception as e:
                print(f"❌ HTTP/2.0测试失败: {e}")
                print("💡 提示: 请确保HTTP/2.0服务器正在运行 (python start_http2.py)")
                continue
            
            # 打印此轮对比结果
            self.print_results([http1_result, http2_result])
            
            # 等待一下再进行下个测试
            await asyncio.sleep(2)
        
        # 总结
        print(f"\n🎉 测试完成! 共进行了{len(all_results)}个测试")
    
    async def test_sse_performance(self):
        """测试SSE流式响应性能"""
        print("\n🔄 测试SSE流式响应性能...")
        
        # HTTP/1.1 SSE测试
        print("测试HTTP/1.1 SSE...")
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream('POST', f"{self.base_url_http1}/generate/stream", 
                                       json=self.test_data) as response:
                    chunks = 0
                    async for chunk in response.aiter_text():
                        chunks += 1
                        if chunks >= 10:  # 限制测试长度
                            break
            http1_sse_time = time.time() - start_time
            print(f"✅ HTTP/1.1 SSE: {http1_sse_time:.2f}秒 ({chunks}个数据块)")
        except Exception as e:
            print(f"❌ HTTP/1.1 SSE测试失败: {e}")
            http1_sse_time = float('inf')
        
        # HTTP/2.0 SSE测试
        print("测试HTTP/2.0 SSE...")
        start_time = time.time()
        try:
            async with httpx.AsyncClient(http2=True, timeout=30.0, verify=False) as client:
                async with client.stream('POST', f"{self.base_url_http2}/generate/stream", 
                                       json=self.test_data) as response:
                    chunks = 0
                    async for chunk in response.aiter_text():
                        chunks += 1
                        if chunks >= 10:  # 限制测试长度
                            break
            http2_sse_time = time.time() - start_time
            print(f"✅ HTTP/2.0 SSE: {http2_sse_time:.2f}秒 ({chunks}个数据块)")
        except Exception as e:
            print(f"❌ HTTP/2.0 SSE测试失败: {e}")
            http2_sse_time = float('inf')
        
        # 对比结果
        if http1_sse_time != float('inf') and http2_sse_time != float('inf'):
            improvement = ((http1_sse_time - http2_sse_time) / http1_sse_time) * 100
            print(f"🌟 SSE性能提升: {improvement:+.1f}%")

async def main():
    """主函数"""
    print("🚀 小红书文案生成智能体 - HTTP/2.0性能测试")
    print("=" * 60)
    
    tester = HTTP2PerformanceTester()
    
    print("📋 测试准备:")
    print("1. 确保HTTP/1.1服务器运行在 http://localhost:8000")
    print("2. 确保HTTP/2.0服务器运行在 https://localhost:8443")
    print("3. 将测试多种并发场景下的性能差异")
    
    # 等待用户确认
    input("\n按回车键开始测试...")
    
    try:
        # 运行综合测试
        await tester.run_comprehensive_test()
        
        # 测试SSE性能
        await tester.test_sse_performance()
        
        print(f"\n✅ 所有测试完成!")
        print("💡 建议:")
        print("   - 在生产环境中使用HTTP/2.0以获得更好的性能")
        print("   - 确保启用SSL/TLS以充分利用HTTP/2.0特性")
        print("   - 考虑使用CDN进一步优化性能")
        
    except KeyboardInterrupt:
        print("\n👋 测试已取消")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 检查依赖
    try:
        import httpx
    except ImportError:
        print("❌ 请安装httpx: pip install 'httpx[http2]'")
        exit(1)
    
    asyncio.run(main()) 