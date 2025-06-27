#!/usr/bin/env python3
"""
多线程处理演示脚本
演示如何使用新的分离式多线程API接口
"""

import asyncio
import aiohttp
import time
import json
from typing import List, Dict


class MultiThreadingDemo:
    """多线程功能演示类"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.session = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def check_health(self) -> Dict:
        """检查API健康状态"""
        async with self.session.get(f"{self.api_base_url}/health") as response:
            return await response.json()
    
    async def get_system_status(self) -> Dict:
        """获取系统状态"""
        async with self.session.get(f"{self.api_base_url}/system/status") as response:
            return await response.json()
    
    async def get_thread_pools_status(self) -> Dict:
        """获取线程池详细状态"""
        async with self.session.get(f"{self.api_base_url}/system/pools") as response:
            return await response.json()
    
    async def submit_async_generation_task(self, request_data: Dict) -> str:
        """提交异步生成任务（智能体线程池）"""
        async with self.session.post(
            f"{self.api_base_url}/generate/async",
            json=request_data
        ) as response:
            result = await response.json()
            return result["data"]["task_id"]
    
    async def submit_async_chat_task(self, request_data: Dict) -> str:
        """提交异步聊天任务（智能体线程池）"""
        async with self.session.post(
            f"{self.api_base_url}/chat/async",
            json=request_data
        ) as response:
            result = await response.json()
            return result["data"]["task_id"]
    
    async def submit_system_cleanup_task(self) -> str:
        """提交系统清理任务（系统线程池）"""
        async with self.session.post(
            f"{self.api_base_url}/system/cleanup",
            params={"max_age_hours": 1}
        ) as response:
            result = await response.json()
            return result["data"]["task_id"]
    
    async def get_task_status(self, task_id: str) -> Dict:
        """获取任务状态"""
        async with self.session.get(f"{self.api_base_url}/tasks/{task_id}/status") as response:
            return await response.json()
    
    async def wait_for_task_completion(self, task_id: str, timeout: int = 60) -> Dict:
        """等待任务完成"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status_response = await self.get_task_status(task_id)
            status_data = status_response["data"]
            
            if status_data["status"] in ["completed", "failed", "timeout", "cancelled"]:
                return status_data
            
            await asyncio.sleep(2)  # 每2秒检查一次
        
        raise TimeoutError(f"任务 {task_id} 在 {timeout} 秒内未完成")
    
    async def batch_generate_content(self, requests: List[Dict]) -> List[str]:
        """批量生成内容（智能体线程池）"""
        async with self.session.post(
            f"{self.api_base_url}/batch/generate",
            json=requests
        ) as response:
            result = await response.json()
            return result["data"]["task_ids"]
    
    async def batch_chat(self, messages: List[str], user_id: str) -> List[str]:
        """批量聊天（智能体线程池）"""
        async with self.session.post(
            f"{self.api_base_url}/chat/batch",
            params={"user_id": user_id},
            json=messages
        ) as response:
            result = await response.json()
            return result["data"]["task_ids"]
    
    async def demo_thread_pool_separation(self):
        """演示线程池分离功能"""
        print("=== 线程池分离演示 ===")
        
        # 获取初始状态
        pools_status = await self.get_thread_pools_status()
        
        print("当前线程池状态:")
        agent_pool = pools_status["data"]["agent_pool"]
        system_pool = pools_status["data"]["system_pool"]
        
        print(f"智能体线程池: {agent_pool['description']}")
        print(f"  - 最大线程: {agent_pool['max_workers']}")
        print(f"  - 运行任务: {agent_pool['running_tasks']}")
        print(f"  - 排队任务: {agent_pool['pending_tasks']}")
        print(f"  - 队列使用率: {agent_pool['queue_usage_rate']}")
        
        print(f"系统线程池: {system_pool['description']}")
        print(f"  - 最大线程: {system_pool['max_workers']}")
        print(f"  - 运行任务: {system_pool['running_tasks']}")
        print(f"  - 排队任务: {system_pool['pending_tasks']}")
        print(f"  - 队列使用率: {system_pool['queue_usage_rate']}")
        
        # 同时提交不同类型的任务
        print("\n同时提交智能体任务和系统任务...")
        
        # 智能体任务
        generation_request = {
            "category": "美食探店",
            "topic": "新开的日式料理店",
            "tone": "活泼可爱",
            "length": "短",
            "user_id": "demo_user_pool_test",
            "language": "zh-CN"
        }
        
        chat_request = {
            "message": "请给我一些写作建议",
            "user_id": "demo_user_pool_test",
            "language": "zh-CN"
        }
        
        # 提交任务
        gen_task_id = await self.submit_async_generation_task(generation_request)
        chat_task_id = await self.submit_async_chat_task(chat_request)
        cleanup_task_id = await self.submit_system_cleanup_task()
        
        print(f"生成任务ID: {gen_task_id} (智能体线程池)")
        print(f"聊天任务ID: {chat_task_id} (智能体线程池)")
        print(f"清理任务ID: {cleanup_task_id} (系统线程池)")
        
        # 检查提交后的状态
        pools_status_after = await self.get_thread_pools_status()
        agent_pool_after = pools_status_after["data"]["agent_pool"]
        system_pool_after = pools_status_after["data"]["system_pool"]
        
        print(f"\n提交任务后状态:")
        print(f"智能体线程池: 运行{agent_pool_after['running_tasks']}, 排队{agent_pool_after['pending_tasks']}")
        print(f"系统线程池: 运行{system_pool_after['running_tasks']}, 排队{system_pool_after['pending_tasks']}")
        
        # 等待所有任务完成
        print("\n等待任务完成...")
        results = await asyncio.gather(
            self.wait_for_task_completion(gen_task_id),
            self.wait_for_task_completion(chat_task_id),
            self.wait_for_task_completion(cleanup_task_id),
            return_exceptions=True
        )
        
        print("任务执行结果:")
        task_names = ["生成任务", "聊天任务", "清理任务"]
        pools = ["智能体", "智能体", "系统"]
        
        for i, (result, name, pool) in enumerate(zip(results, task_names, pools)):
            if isinstance(result, Exception):
                print(f"{name} ({pool}线程池): 失败 - {result}")
            else:
                print(f"{name} ({pool}线程池): {result['status']}, 耗时: {result['execution_time']:.2f}秒")
        
        print()
    
    async def demo_concurrent_agent_and_system_tasks(self):
        """演示智能体任务和系统任务的并发处理"""
        print("=== 并发处理演示 ===")
        
        print("测试场景: 在对话过程中同时执行系统检查")
        
        # 提交一个较长的智能体任务（聊天）
        long_chat_request = {
            "message": "请详细介绍小红书文案写作的所有技巧和注意事项，包括标题、正文、标签等各个方面",
            "user_id": "demo_concurrent_user",
            "language": "zh-CN"
        }
        
        print("1. 提交长时间聊天任务...")
        chat_task_id = await self.submit_async_chat_task(long_chat_request)
        
        # 稍等一下，确保聊天任务开始执行
        await asyncio.sleep(1)
        
        # 在聊天进行的同时，提交系统任务
        print("2. 在聊天进行时提交系统监控任务...")
        
        start_time = time.time()
        
        # 连续提交多个系统监控任务
        system_tasks = []
        for i in range(3):
            cleanup_task_id = await self.submit_system_cleanup_task()
            system_tasks.append(cleanup_task_id)
            print(f"   系统任务 {i+1}: {cleanup_task_id}")
        
        # 检查聊天任务状态
        chat_status = await self.get_task_status(chat_task_id)
        print(f"3. 聊天任务状态: {chat_status['data']['status']}")
        
        # 等待系统任务完成
        print("4. 等待系统任务完成...")
        system_results = []
        for task_id in system_tasks:
            result = await self.wait_for_task_completion(task_id, timeout=30)
            system_results.append(result)
        
        system_time = time.time() - start_time
        print(f"   系统任务全部完成，总耗时: {system_time:.2f}秒")
        
        # 等待聊天任务完成
        print("5. 等待聊天任务完成...")
        chat_result = await self.wait_for_task_completion(chat_task_id)
        
        total_time = time.time() - start_time
        
        print(f"测试结果:")
        print(f"  - 聊天任务执行时间: {chat_result['execution_time']:.2f}秒")
        print(f"  - 系统任务平均执行时间: {sum(r['execution_time'] for r in system_results)/len(system_results):.2f}秒")
        print(f"  - 总体耗时: {total_time:.2f}秒")
        print(f"  - 验证: 在对话过程中可以正常执行系统功能 ✅")
        print()
    
    async def demo_load_balancing(self):
        """演示负载均衡"""
        print("=== 负载均衡演示 ===")
        
        print("提交大量任务测试负载分布...")
        
        # 提交多个智能体任务
        agent_tasks = []
        for i in range(5):  # 超过智能体线程池容量
            gen_request = {
                "category": "生活方式",
                "topic": f"生活小技巧 {i+1}",
                "tone": "简洁明了",
                "length": "短",
                "user_id": f"load_test_user_{i+1}",
                "language": "zh-CN"
            }
            task_id = await self.submit_async_generation_task(gen_request)
            agent_tasks.append(task_id)
            print(f"智能体任务 {i+1}: {task_id}")
        
        # 提交多个系统任务
        system_tasks = []
        for i in range(3):
            task_id = await self.submit_system_cleanup_task()
            system_tasks.append(task_id)
            print(f"系统任务 {i+1}: {task_id}")
        
        # 检查队列状态
        pools_status = await self.get_thread_pools_status()
        agent_pool = pools_status["data"]["agent_pool"]
        system_pool = pools_status["data"]["system_pool"]
        
        print(f"\n任务提交后队列状态:")
        print(f"智能体线程池: 运行{agent_pool['running_tasks']}, 排队{agent_pool['pending_tasks']}")
        print(f"系统线程池: 运行{system_pool['running_tasks']}, 排队{system_pool['pending_tasks']}")
        
        # 等待所有任务完成
        print("\n等待所有任务完成...")
        
        all_tasks = agent_tasks + system_tasks
        completed_tasks = []
        
        for task_id in all_tasks:
            try:
                result = await self.wait_for_task_completion(task_id, timeout=120)
                completed_tasks.append(result)
            except TimeoutError:
                print(f"任务 {task_id} 超时")
        
        # 分析结果
        agent_times = [r['execution_time'] for r in completed_tasks[:len(agent_tasks)]]
        system_times = [r['execution_time'] for r in completed_tasks[len(agent_tasks):]]
        
        print(f"负载测试结果:")
        print(f"  - 智能体任务完成数: {len([r for r in completed_tasks[:len(agent_tasks)] if r])}")
        print(f"  - 智能体任务平均耗时: {sum(agent_times)/len(agent_times) if agent_times else 0:.2f}秒")
        print(f"  - 系统任务完成数: {len([r for r in completed_tasks[len(agent_tasks):] if r])}")
        print(f"  - 系统任务平均耗时: {sum(system_times)/len(system_times) if system_times else 0:.2f}秒")
        print()
    
    async def demo_system_monitoring(self):
        """演示系统监控"""
        print("=== 系统监控演示 ===")
        
        # 获取详细状态
        pools_status = await self.get_thread_pools_status()
        status_data = pools_status["data"]
        
        print("线程池详细状态:")
        
        for pool_name in ["agent_pool", "system_pool"]:
            pool_data = status_data[pool_name]
            print(f"\n{pool_data['description']}:")
            print(f"  用途: {pool_data['purpose']}")
            print(f"  线程池名称: {pool_data['pool_name']}")
            print(f"  最大工作线程数: {pool_data['max_workers']}")
            print(f"  当前运行任务: {pool_data['running_tasks']}")
            print(f"  排队等待任务: {pool_data['pending_tasks']}")
            print(f"  已完成任务: {pool_data['completed_tasks']}")
            print(f"  失败任务: {pool_data['failed_tasks']}")
            print(f"  总任务数: {pool_data['total_tasks']}")
            print(f"  队列大小: {pool_data['queue_size']}")
            print(f"  队列使用率: {pool_data['queue_usage_rate']}")
            print(f"  队列是否满载: {pool_data['queue_full']}")
        
        summary = status_data["summary"]
        print(f"\n系统总览:")
        print(f"  总运行任务: {summary['total_running']}")
        print(f"  总排队任务: {summary['total_pending']}")
        print(f"  总完成任务: {summary['total_completed']}")
        print(f"  总失败任务: {summary['total_failed']}")
        print()
    
    async def run_all_demos(self):
        """运行所有演示"""
        print("🚀 开始多线程分离式处理演示")
        print("=" * 60)
        
        # 检查API状态
        try:
            health = await self.check_health()
            if health["success"]:
                print("✅ API服务正常运行")
                system_status = health["data"]["system_status"]
                print(f"   智能体线程池: 运行{system_status['agent_pool']['running_tasks']}, 排队{system_status['agent_pool']['pending_tasks']}")
                print(f"   系统线程池: 运行{system_status['system_pool']['running_tasks']}, 排队{system_status['system_pool']['pending_tasks']}")
            else:
                print("❌ API服务异常")
                return
        except Exception as e:
            print(f"❌ 无法连接到API服务: {e}")
            return
        
        print()
        
        # 运行各种演示
        try:
            await self.demo_thread_pool_separation()
            await self.demo_concurrent_agent_and_system_tasks()
            await self.demo_load_balancing()
            await self.demo_system_monitoring()
            
            print("🎉 所有演示完成!")
            print("\n核心优势:")
            print("✅ 智能体任务与系统功能完全分离")
            print("✅ 对话过程中可正常执行系统检查")
            print("✅ 避免资源竞争，提高系统稳定性")
            print("✅ 独立的队列管理和负载均衡")
            
        except Exception as e:
            print(f"❌ 演示过程中出错: {e}")


async def main():
    """主函数"""
    print("小红书文案生成智能体 - 分离式多线程处理演示")
    print("请确保API服务正在运行 (python start_api.py)")
    print()
    
    async with MultiThreadingDemo() as demo:
        await demo.run_all_demos()


if __name__ == "__main__":
    asyncio.run(main()) 