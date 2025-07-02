"""
业务逻辑服务
"""

import asyncio
import concurrent.futures
import threading
import queue
import time
from datetime import datetime
from typing import Dict, AsyncGenerator, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum

from fastapi import HTTPException

from Agent.xiaohongshu_agent import XiaohongshuAgent, ContentRequest, ContentCategory
from .sse import SSEMessage, sse_manager
from .config import logger, THREAD_CONFIG
from .i18n import Language, get_message


@dataclass
class TaskRequest:
    """任务请求数据类"""
    task_id: str
    user_id: str
    task_type: str
    task_func: Callable
    args: tuple
    kwargs: dict
    priority: int = 1  # 优先级，数字越小优先级越高
    created_at: datetime = None
    timeout: float = 300.0  # 任务超时时间（秒）
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    """任务结果数据类"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: str = None
    started_at: datetime = None
    completed_at: datetime = None
    execution_time: float = 0.0


class ThreadPoolManager:
    """线程池管理器"""
    
    def __init__(self, max_workers: int = 10, queue_size: int = 100, pool_name: str = "default"):
        self.max_workers = max_workers
        self.queue_size = queue_size
        self.pool_name = pool_name
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix=f"{pool_name}_worker"
        )
        self.task_queue = queue.PriorityQueue(maxsize=queue_size)
        self.running_tasks: Dict[str, TaskRequest] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        self.task_futures: Dict[str, concurrent.futures.Future] = {}
        self.lock = threading.RLock()
        self._shutdown = False
        
        # 启动任务分发线程
        self.dispatcher_thread = threading.Thread(
            target=self._task_dispatcher, 
            daemon=True,
            name=f"{pool_name}_dispatcher"
        )
        self.dispatcher_thread.start()
        
        logger.info(f"线程池管理器 [{pool_name}] 初始化完成，最大工作线程数: {max_workers}")
    
    def submit_task(self, task_request: TaskRequest) -> str:
        """提交任务到线程池"""
        try:
            # 检查队列是否已满
            if self.task_queue.full():
                raise HTTPException(
                    status_code=429, 
                    detail=f"线程池 [{self.pool_name}] 任务队列已满，请稍后重试"
                )
            
            # 将任务加入优先级队列
            self.task_queue.put((task_request.priority, time.time(), task_request))
            
            # 初始化任务状态
            with self.lock:
                self.completed_tasks[task_request.task_id] = TaskResult(
                    task_id=task_request.task_id,
                    status=TaskStatus.PENDING
                )
            
            logger.info(f"任务 {task_request.task_id} 已提交到线程池 [{self.pool_name}]")
            return task_request.task_id
            
        except Exception as e:
            logger.error(f"提交任务到线程池 [{self.pool_name}] 失败: {e}")
            raise HTTPException(status_code=500, detail=f"提交任务失败: {str(e)}")
    
    def _task_dispatcher(self):
        """任务分发器（在独立线程中运行）"""
        logger.info(f"线程池 [{self.pool_name}] 任务分发器启动")
        
        while not self._shutdown:
            try:
                # 从队列获取任务（阻塞式，超时1秒）
                try:
                    priority, timestamp, task_request = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # 检查任务是否超时
                if (datetime.now() - task_request.created_at).total_seconds() > task_request.timeout:
                    with self.lock:
                        self.completed_tasks[task_request.task_id] = TaskResult(
                            task_id=task_request.task_id,
                            status=TaskStatus.TIMEOUT,
                            error="任务在队列中等待超时"
                        )
                    logger.warning(f"任务 {task_request.task_id} 在线程池 [{self.pool_name}] 中等待超时")
                    continue
                
                # 提交任务到线程池执行
                try:
                    future = self.executor.submit(self._execute_task, task_request)
                    
                    with self.lock:
                        self.running_tasks[task_request.task_id] = task_request
                        self.task_futures[task_request.task_id] = future
                    
                    logger.info(f"任务 {task_request.task_id} 已分发到 [{self.pool_name}] 工作线程")
                    
                except Exception as e:
                    logger.error(f"分发任务 {task_request.task_id} 到线程池 [{self.pool_name}] 失败: {e}")
                    with self.lock:
                        self.completed_tasks[task_request.task_id] = TaskResult(
                            task_id=task_request.task_id,
                            status=TaskStatus.FAILED,
                            error=f"分发失败: {str(e)}"
                        )
                        
            except Exception as e:
                logger.error(f"线程池 [{self.pool_name}] 任务分发器异常: {e}")
                time.sleep(1)  # 避免快速循环
        
        logger.info(f"线程池 [{self.pool_name}] 任务分发器已停止")
    
    def _execute_task(self, task_request: TaskRequest) -> TaskResult:
        """执行任务（在工作线程中运行）"""
        start_time = datetime.now()
        
        try:
            # 更新任务状态为运行中
            with self.lock:
                if task_request.task_id in self.completed_tasks:
                    self.completed_tasks[task_request.task_id].status = TaskStatus.RUNNING
                    self.completed_tasks[task_request.task_id].started_at = start_time
            
            logger.info(f"开始执行任务 {task_request.task_id} (线程池: {self.pool_name})")
            
            # 执行任务函数
            result = task_request.task_func(*task_request.args, **task_request.kwargs)
            
            # 计算执行时间
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # 创建成功结果
            task_result = TaskResult(
                task_id=task_request.task_id,
                status=TaskStatus.COMPLETED,
                result=result,
                started_at=start_time,
                completed_at=end_time,
                execution_time=execution_time
            )
            
            logger.info(f"任务 {task_request.task_id} 在线程池 [{self.pool_name}] 执行完成，耗时 {execution_time:.2f}秒")
            
        except Exception as e:
            # 计算执行时间
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # 创建失败结果
            task_result = TaskResult(
                task_id=task_request.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
                started_at=start_time,
                completed_at=end_time,
                execution_time=execution_time
            )
            
            logger.error(f"任务 {task_request.task_id} 在线程池 [{self.pool_name}] 执行失败: {e}")
        
        finally:
            # 清理运行中的任务记录
            with self.lock:
                self.running_tasks.pop(task_request.task_id, None)
                self.task_futures.pop(task_request.task_id, None)
                self.completed_tasks[task_request.task_id] = task_result
        
        return task_result
    
    def get_task_status(self, task_id: str) -> Optional[TaskResult]:
        """获取任务状态"""
        with self.lock:
            return self.completed_tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self.lock:
            # 取消正在运行的任务
            if task_id in self.task_futures:
                future = self.task_futures[task_id]
                if future.cancel():
                    self.completed_tasks[task_id] = TaskResult(
                        task_id=task_id,
                        status=TaskStatus.CANCELLED,
                        error="任务已被取消"
                    )
                    self.running_tasks.pop(task_id, None)
                    self.task_futures.pop(task_id, None)
                    logger.info(f"任务 {task_id} 在线程池 [{self.pool_name}] 中已取消")
                    return True
            
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取线程池状态"""
        with self.lock:
            running_tasks = len(self.running_tasks)
            pending_tasks = self.task_queue.qsize()
            completed_tasks = len([t for t in self.completed_tasks.values() if t.status == TaskStatus.COMPLETED])
            failed_tasks = len([t for t in self.completed_tasks.values() if t.status == TaskStatus.FAILED])
            
            return {
                "max_workers": self.max_workers,
                "active_threads": running_tasks,
                "queue_size": pending_tasks,
                "running_tasks": running_tasks,
                "pending_tasks": pending_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "tasks_completed": completed_tasks,
                "tasks_failed": failed_tasks,
                "tasks_pending": pending_tasks
            }
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务"""
        cutoff_time = datetime.now() - asyncio.timedelta(hours=max_age_hours)
        
        with self.lock:
            old_task_ids = [
                task_id for task_id, result in self.completed_tasks.items()
                if result.completed_at and result.completed_at < cutoff_time
            ]
            
            for task_id in old_task_ids:
                del self.completed_tasks[task_id]
            
            logger.info(f"线程池 [{self.pool_name}] 清理了 {len(old_task_ids)} 个旧任务")
    
    def shutdown(self):
        """关闭线程池"""
        logger.info(f"正在关闭线程池 [{self.pool_name}]...")
        self._shutdown = True
        
        # 等待分发线程结束
        if self.dispatcher_thread.is_alive():
            self.dispatcher_thread.join(timeout=5)
        
        # 关闭线程池
        self.executor.shutdown(wait=True)
        logger.info(f"线程池 [{self.pool_name}] 已关闭")


class AgentService:
    """智能体服务"""
    
    def __init__(self):
        self.agent: Optional[XiaohongshuAgent] = None
        # 创建两个专用线程池
        self.agent_thread_pool = ThreadPoolManager(
            max_workers=THREAD_CONFIG["agent_pool"]["max_workers"],
            queue_size=THREAD_CONFIG["agent_pool"]["queue_size"],
            pool_name="agent"
        )
        self.system_thread_pool = ThreadPoolManager(
            max_workers=THREAD_CONFIG["system_pool"]["max_workers"],
            queue_size=THREAD_CONFIG["system_pool"]["queue_size"],
            pool_name="system"
        )
    
    async def initialize(self):
        """初始化智能体（异步）"""
        if self.agent is None:
            logger.info("正在初始化小红书智能体...")
            self.agent = XiaohongshuAgent()
            logger.info("智能体初始化完成")
    
    def check_ready(self):
        """检查智能体是否就绪"""
        if self.agent is None:
            raise HTTPException(status_code=503, detail="智能体尚未初始化，请稍候再试")
        return self.agent
    
    def parse_content_category(self, category_str: str) -> ContentCategory:
        """解析内容分类"""
        category_mapping = {
            "美食": ContentCategory.FOOD,
            "旅行": ContentCategory.TRAVEL,
            "时尚": ContentCategory.FASHION,
            "美妆": ContentCategory.BEAUTY,
            "健身": ContentCategory.FITNESS,
            "生活": ContentCategory.LIFESTYLE,
            "科技": ContentCategory.TECH,
            "情感": ContentCategory.EMOTION,
            "职场": ContentCategory.CAREER,
            "教育": ContentCategory.EDUCATION
        }
        return category_mapping.get(category_str, ContentCategory.LIFESTYLE)
    
    def submit_agent_task(self, task_type: str, user_id: str, task_func: Callable, *args, priority: int = 1, **kwargs) -> str:
        """提交智能体任务到专用线程池"""
        import uuid
        task_id = f"{task_type}_{user_id}_{uuid.uuid4().hex[:8]}"
        
        task_request = TaskRequest(
            task_id=task_id,
            user_id=user_id,
            task_type=task_type,
            task_func=task_func,
            args=args,
            kwargs=kwargs,
            priority=priority
        )
        
        return self.agent_thread_pool.submit_task(task_request)
    
    def submit_stream_task(self, task_type: str, user_id: str, generator_func: Callable, *args, priority: int = 1, **kwargs) -> str:
        """提交流式任务到智能体线程池
        
        Args:
            task_type: 任务类型
            user_id: 用户ID
            generator_func: 生成器函数，必须返回一个生成器
            *args: 传递给生成器函数的参数
            priority: 任务优先级（数字越小优先级越高）
            **kwargs: 传递给生成器函数的关键字参数
        
        Returns:
            str: 任务ID
        """
        import uuid
        task_id = f"stream_{task_type}_{user_id}_{uuid.uuid4().hex[:8]}"
        
        def stream_task_wrapper():
            """流式任务包装器，在线程中执行生成器函数并收集结果"""
            try:
                # 执行生成器函数获取生成器
                generator = generator_func(*args, **kwargs)
                
                # 收集生成器的所有内容
                chunks = []
                for chunk in generator:
                    chunks.append(chunk)
                
                # 返回完整内容
                return {
                    "chunks": chunks,
                    "full_content": "".join(chunks),
                    "chunk_count": len(chunks)
                }
                
            except Exception as e:
                logger.error(f"流式任务 {task_id} 执行失败: {e}")
                raise
        
        task_request = TaskRequest(
            task_id=task_id,
            user_id=user_id,
            task_type=f"stream_{task_type}",
            task_func=stream_task_wrapper,
            args=(),
            kwargs={},
            priority=priority
        )
        
        return self.agent_thread_pool.submit_task(task_request)
    
    def submit_system_task(self, task_type: str, user_id: str, task_func: Callable, *args, priority: int = 1, **kwargs) -> str:
        """提交系统任务到专用线程池"""
        import uuid
        task_id = f"{task_type}_{user_id}_{uuid.uuid4().hex[:8]}"
        
        task_request = TaskRequest(
            task_id=task_id,
            user_id=user_id,
            task_type=task_type,
            task_func=task_func,
            args=args,
            kwargs=kwargs,
            priority=priority
        )
        
        return self.system_thread_pool.submit_task(task_request)
    
    def get_task_status(self, task_id: str) -> Optional[TaskResult]:
        """获取任务状态（从两个线程池中查找）"""
        # 先从智能体线程池查找
        result = self.agent_thread_pool.get_task_status(task_id)
        if result:
            return result
        
        # 再从系统线程池查找
        return self.system_thread_pool.get_task_status(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务（在两个线程池中尝试）"""
        # 先尝试在智能体线程池取消
        if self.agent_thread_pool.cancel_task(task_id):
            return True
        
        # 再尝试在系统线程池取消
        return self.system_thread_pool.cancel_task(task_id)
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取所有线程池的系统状态"""
        agent_status = self.agent_thread_pool.get_system_status()
        system_status = self.system_thread_pool.get_system_status()
        
        return {
            "agent_pool": agent_status,
            "system_pool": system_status,
            "total_running_tasks": agent_status["running_tasks"] + system_status["running_tasks"],
            "total_pending_tasks": agent_status["pending_tasks"] + system_status["pending_tasks"],
            "total_completed_tasks": agent_status["completed_tasks"] + system_status["completed_tasks"],
            "total_failed_tasks": agent_status["failed_tasks"] + system_status["failed_tasks"]
        }
    
    def is_agent_pool_idle(self) -> bool:
        """检查智能体线程池是否空闲（没有运行或等待的任务）"""
        status = self.agent_thread_pool.get_system_status()
        return status["running_tasks"] == 0 and status["pending_tasks"] == 0
    
    def can_execute_immediately(self) -> bool:
        """检查是否可以立即执行任务（有空闲线程且无等待队列）"""
        status = self.agent_thread_pool.get_system_status()
        return status["running_tasks"] < status["max_workers"] and status["pending_tasks"] == 0
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理所有线程池的旧任务"""
        self.agent_thread_pool.cleanup_old_tasks(max_age_hours)
        self.system_thread_pool.cleanup_old_tasks(max_age_hours)
    
    def shutdown(self):
        """关闭所有线程池"""
        self.agent_thread_pool.shutdown()
        self.system_thread_pool.shutdown()


class SessionService:
    """用户会话服务"""
    
    def __init__(self):
        self.user_sessions: Dict[str, Dict] = {}
        self._lock = threading.RLock()
    
    def get_user_session(self, user_id: str) -> Dict:
        """获取用户会话（线程安全）"""
        with self._lock:
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {
                    "content_history": [],
                    "current_version_index": -1,
                    "feedback_round": 0,
                    "last_generated_content": "",
                    "current_request": None,
                    "created_at": datetime.now(),
                    "last_activity": datetime.now()
                }
            else:
                # 更新最后活动时间
                self.user_sessions[user_id]["last_activity"] = datetime.now()
            
            return self.user_sessions[user_id]
    
    def add_content_to_history(self, user_id: str, content: str, action: str = "生成"):
        """添加内容到版本历史（线程安全）"""
        with self._lock:
            session = self.get_user_session(user_id)
            version_info = {
                "content": content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "action": action,
                "version": len(session["content_history"]) + 1
            }
            session["content_history"].append(version_info)
            session["current_version_index"] = len(session["content_history"]) - 1
            session["last_generated_content"] = content
    
    def clear_user_session(self, user_id: str):
        """清空用户会话（线程安全）"""
        with self._lock:
            if user_id in self.user_sessions:
                del self.user_sessions[user_id]
    
    def cleanup_inactive_sessions(self, max_inactive_hours: int = 24):
        """清理不活跃的会话"""
        cutoff_time = datetime.now() - asyncio.timedelta(hours=max_inactive_hours)
        
        with self._lock:
            inactive_users = [
                user_id for user_id, session in self.user_sessions.items()
                if session.get("last_activity", session["created_at"]) < cutoff_time
            ]
            
            for user_id in inactive_users:
                del self.user_sessions[user_id]
            
            logger.info(f"清理了 {len(inactive_users)} 个不活跃的用户会话")


class StreamService:
    """流式处理服务"""
    
    def __init__(self, session_service: SessionService):
        self.session_service = session_service
    
    async def generate_with_sse_smart(self, generator_func: Callable, user_id: str, action: str = "生成", language: Language = Language.ZH_CN, *args, **kwargs) -> AsyncGenerator[str, None]:
        """智能流式生成：如果线程池空闲则直接执行，否则使用线程池"""
        # 检查是否可以立即执行
        if agent_service.can_execute_immediately():
            logger.info(f"线程池空闲，直接执行流式任务 - 用户: {user_id}, 操作: {action}")
            # 直接执行生成器函数
            try:
                generator = generator_func(*args, **kwargs)
                async for message in self.generate_with_sse(generator, user_id, action, language):
                    yield message
            except Exception as e:
                logger.error(f"直接执行流式任务失败: {e}")
                error_message = get_message("generation_failed", language) if action == get_message("initial_generation", language) else f"{action}失败"
                yield SSEMessage.error(f"{error_message}: {str(e)}")
        else:
            # 使用线程池处理
            logger.info(f"线程池忙碌，使用任务队列 - 用户: {user_id}, 操作: {action}")
            task_id = agent_service.submit_stream_task(
                task_type="smart_stream",
                user_id=user_id,
                generator_func=generator_func,
                priority=0,  # 最高优先级
                *args,
                **kwargs
            )
            
            async for message in self.generate_with_sse_from_task(task_id, user_id, action, language):
                yield message
    
    async def generate_with_sse(self, generator, user_id: str, action: str = "生成", language: Language = Language.ZH_CN) -> AsyncGenerator[str, None]:
        """通用的SSE生成器包装器"""
        connection_id = f"{user_id}_{datetime.now().timestamp()}"
        
        try:
            # 添加连接
            sse_manager.add_connection(connection_id, user_id)
            
            # 发送开始状态 - 使用国际化消息
            start_message = get_message("processing", language)
            yield SSEMessage.status("started", f"{start_message} {action}...")
            
            content = ""
            chunk_count = 0
            
            # 处理生成器内容（同步生成器）
            try:
                for chunk in generator:
                    if chunk:
                        content += chunk
                        chunk_count += 1
                        
                        # 发送内容块
                        yield SSEMessage.content_chunk(
                            chunk=chunk,
                            metadata={
                                "action": action,
                                "chunk_count": chunk_count,
                                "total_length": len(content)
                            }
                        )
                        
                        # 更新心跳
                        sse_manager.update_heartbeat(connection_id)
                        
                        # 小延迟，避免发送过快
                        await asyncio.sleep(0.01)
            except StopIteration:
                pass  # 生成器正常结束
            
            # 保存到历史
            if content:
                self.session_service.add_content_to_history(user_id, content, action)
                session = self.session_service.get_user_session(user_id)
                
                # 发送完成状态
                yield SSEMessage.complete({
                    "content": content,
                    "action": action,
                    "version": session["current_version_index"] + 1,
                    "total_chunks": chunk_count,
                    "total_length": len(content)
                })
            else:
                empty_content_message = get_message("generation_failed", language)
                yield SSEMessage.error(empty_content_message)
                
        except Exception as e:
            logger.error(f"{action}过程中出错: {e}")
            error_message = get_message("generation_failed", language)
            yield SSEMessage.error(f"{error_message}: {str(e)}")
        
        finally:
            # 移除连接
            sse_manager.remove_connection(connection_id)
    
    async def generate_with_sse_from_task(self, task_id: str, user_id: str, action: str = "生成", language: Language = Language.ZH_CN) -> AsyncGenerator[str, None]:
        """从线程池任务结果生成SSE流
        
        这个方法会高频轮询任务状态，并将完成的结果转换为SSE流式输出
        """
        connection_id = f"{user_id}_{datetime.now().timestamp()}"
        
        try:
            # 添加连接
            sse_manager.add_connection(connection_id, user_id)
            
            # 发送开始状态 - 使用国际化消息
            start_message = get_message("processing", language)
            yield SSEMessage.status("started", f"{start_message} {action}...")
            
            # 高效轮询任务状态
            poll_count = 0
            status_sent = False
            last_status_time = datetime.now()
            
            while True:
                start_poll_time = datetime.now()
                task_result = agent_service.get_task_status(task_id)
                
                if task_result is None:
                    error_message = get_message("generation_failed", language)
                    yield SSEMessage.error(f"{error_message}: 任务 {task_id} 不存在")
                    return
                
                if task_result.status == TaskStatus.COMPLETED:
                    # 任务完成，立即处理结果
                    result = task_result.result
                    
                    if isinstance(result, dict) and "chunks" in result:
                        # 流式任务结果，快速发送
                        chunks = result["chunks"]
                        full_content = result.get("full_content", "")
                        
                        for i, chunk in enumerate(chunks):
                            if chunk:
                                yield SSEMessage.content_chunk(
                                    chunk=chunk,
                                    metadata={
                                        "action": action,
                                        "chunk_count": i + 1,
                                        "total_chunks": len(chunks),
                                        "total_length": len(full_content)
                                    }
                                )
                                # 更新心跳
                                sse_manager.update_heartbeat(connection_id)
                                await asyncio.sleep(0.02)  # 更快的模拟流式输出
                        
                        # 保存到历史
                        if full_content:
                            self.session_service.add_content_to_history(user_id, full_content, action)
                            session = self.session_service.get_user_session(user_id)
                            
                            # 发送完成状态
                            yield SSEMessage.complete({
                                "content": full_content,
                                "action": action,
                                "version": session["current_version_index"] + 1,
                                "total_chunks": len(chunks),
                                "total_length": len(full_content),
                                "execution_time": task_result.execution_time
                            })
                        else:
                            empty_content_message = get_message("generation_failed", language)
                            yield SSEMessage.error(empty_content_message)
                    else:
                        # 普通任务结果，直接输出
                        content = str(result)
                        yield SSEMessage.content_chunk(
                            chunk=content,
                            metadata={
                                "action": action,
                                "chunk_count": 1,
                                "total_chunks": 1,
                                "total_length": len(content)
                            }
                        )
                        
                        # 保存到历史
                        self.session_service.add_content_to_history(user_id, content, action)
                        session = self.session_service.get_user_session(user_id)
                        
                        # 发送完成状态
                        yield SSEMessage.complete({
                            "content": content,
                            "action": action,
                            "version": session["current_version_index"] + 1,
                            "total_chunks": 1,
                            "total_length": len(content),
                            "execution_time": task_result.execution_time
                        })
                    
                    return
                
                elif task_result.status == TaskStatus.FAILED:
                    error_message = get_message("generation_failed", language)
                    yield SSEMessage.error(f"{error_message}: {task_result.error}")
                    return
                
                elif task_result.status == TaskStatus.TIMEOUT:
                    timeout_message = "超时" if language == Language.ZH_CN else "Timeout" if language == Language.EN_US else "タイムアウト" if language == Language.JA_JP else "超時"
                    yield SSEMessage.error(f"{action}{timeout_message}")
                    return
                
                elif task_result.status == TaskStatus.CANCELLED:
                    cancelled_message = "已取消" if language == Language.ZH_CN else "Cancelled" if language == Language.EN_US else "キャンセル済み" if language == Language.JA_JP else "已取消"
                    yield SSEMessage.error(f"{action}{cancelled_message}")
                    return
                
                else:
                    # 任务还在进行中，智能化状态消息发送
                    poll_count += 1
                    current_time = datetime.now()
                    
                    # 获取配置
                    from .config import SSE_CONFIG
                    status_interval = SSE_CONFIG.get("status_message_interval", 50)
                    poll_interval = SSE_CONFIG.get("poll_interval", 0.1)
                    
                    # 智能发送状态消息：首次 + 每5秒一次
                    time_since_last_status = (current_time - last_status_time).total_seconds()
                    should_send_status = (not status_sent or 
                                        time_since_last_status >= 5.0 or 
                                        poll_count % status_interval == 0)
                    
                    if should_send_status:
                        elapsed_time = (current_time - start_poll_time).total_seconds()
                        processing_message = get_message("processing", language)
                        wait_message = "已等待" if language == Language.ZH_CN else "waiting" if language == Language.EN_US else "待機中" if language == Language.JA_JP else "已等待"
                        yield SSEMessage.status("processing", f"{processing_message} {action}... ({wait_message} {elapsed_time:.1f}s)")
                        status_sent = True
                        last_status_time = current_time
                    
                    # 更新心跳但不发送消息
                    sse_manager.update_heartbeat(connection_id)
                    
                    # 动态调整轮询间隔：任务运行时间越长，轮询间隔越长
                    if poll_count < 10:  # 前1秒快速轮询
                        actual_interval = 0.05
                    elif poll_count < 50:  # 前5秒中速轮询
                        actual_interval = poll_interval
                    else:  # 5秒后慢速轮询
                        actual_interval = min(poll_interval * 2, 0.3)
                    
                    await asyncio.sleep(actual_interval)
                
        except Exception as e:
            logger.error(f"SSE任务轮询错误: {e}")
            error_message = get_message("generation_failed", language)
            yield SSEMessage.error(f"{error_message}: {str(e)}")
        
        finally:
            # 移除连接
            sse_manager.remove_connection(connection_id)


# 全局服务实例
agent_service = AgentService()
session_service = SessionService()
stream_service = StreamService(session_service) 