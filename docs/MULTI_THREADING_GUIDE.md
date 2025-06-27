# 多线程处理指南

## 概述

本项目采用**分离式多线程架构**，将智能体任务和系统功能分别处理到不同的专用线程池中，避免了资源竞争，确保在对话过程中可以正常执行系统检查和其他功能。

## 架构设计

### 双线程池架构

系统使用两个独立的线程池：

#### 1. 智能体线程池 (Agent Pool)
- **线程数**: 3个工作线程
- **队列容量**: 20个任务
- **专用处理**: AI相关任务（对话、生成、优化）
- **优先级**: 对话(1) > 优化(2) > 批量生成(3)

#### 2. 系统线程池 (System Pool)  
- **线程数**: 5个工作线程
- **队列容量**: 50个任务
- **专用处理**: 系统功能（清理、监控、状态查询）
- **优先级**: 系统清理(1) > 其他系统任务(2)

### 分离的优势

✅ **避免资源竞争**: 智能体任务不会阻塞系统功能  
✅ **对话友好**: 在对话过程中可正常执行系统检查  
✅ **独立扩展**: 两个线程池可以独立配置和调优  
✅ **故障隔离**: 一个线程池出问题不影响另一个  
✅ **性能优化**: 根据任务特性分配不同的资源

## API接口

### 智能体任务接口 (Agent Pool)

#### 1. 异步文案生成
```http
POST /generate/async
Content-Type: application/json

{
    "category": "美食探店",
    "topic": "新开的日式料理店",
    "tone": "活泼可爱", 
    "length": "短",
    "user_id": "user123",
    "language": "zh-CN"
}
```

**响应**:
```json
{
    "success": true,
    "message": "任务已提交",
    "data": {
        "task_id": "generate_user123_abc12345",
        "status": "pending",
        "message": "开始生成内容...",
        "pool": "agent"
    }
}
```

#### 2. 异步聊天对话
```http
POST /chat/async
Content-Type: application/json

{
    "message": "请给我一些写作建议",
    "user_id": "user123",
    "language": "zh-CN"
}
```

**响应**:
```json
{
    "success": true,
    "message": "任务已提交",
    "data": {
        "task_id": "chat_user123_def67890",
        "status": "pending", 
        "message": "开始对话...",
        "pool": "agent"
    }
}
```

#### 3. 异步内容优化
```http
POST /optimize/async
Content-Type: application/json

{
    "content": "需要优化的文案内容...",
    "user_id": "user123",
    "language": "zh-CN"
}
```

#### 4. 批量生成
```http
POST /batch/generate
Content-Type: application/json

[
    {
        "category": "美食探店",
        "topic": "餐厅推荐1",
        "tone": "活泼可爱",
        "length": "短",
        "user_id": "user123",
        "language": "zh-CN"
    },
    {
        "category": "美食探店", 
        "topic": "餐厅推荐2",
        "tone": "专业详细",
        "length": "中等",
        "user_id": "user123",
        "language": "zh-CN"
    }
]
```

#### 5. 批量对话
```http
POST /chat/batch?user_id=user123
Content-Type: application/json

[
    "请介绍小红书写作技巧",
    "如何提高文案的吸引力",
    "什么是好的标题"
]
```

### 系统功能接口 (System Pool)

#### 1. 异步系统清理
```http
POST /system/cleanup?max_age_hours=24
```

**响应**:
```json
{
    "success": true,
    "message": "任务已提交",
    "data": {
        "task_id": "cleanup_system_xyz98765",
        "status": "pending",
        "message": "开始清理系统数据...",
        "pool": "system"
    }
}
```

#### 2. 同步系统清理 (立即执行)
```http
POST /system/cleanup/sync?max_age_hours=24
```

#### 3. 线程池状态监控
```http
GET /system/pools
```

**响应**:
```json
{
    "success": true,
    "data": {
        "agent_pool": {
            "description": "智能体任务专用线程池",
            "purpose": "处理对话、生成、优化等AI任务",
            "pool_name": "agent",
            "max_workers": 3,
            "running_tasks": 1,
            "pending_tasks": 2,
            "completed_tasks": 15,
            "failed_tasks": 0,
            "total_tasks": 18,
            "queue_size": 20,
            "queue_usage_rate": "2/20 (10.0%)",
            "queue_full": false
        },
        "system_pool": {
            "description": "系统功能专用线程池",
            "purpose": "处理清理、监控等系统任务", 
            "pool_name": "system",
            "max_workers": 5,
            "running_tasks": 0,
            "pending_tasks": 0,
            "completed_tasks": 8,
            "failed_tasks": 0,
            "total_tasks": 8,
            "queue_size": 50,
            "queue_usage_rate": "0/50 (0.0%)",
            "queue_full": false
        },
        "summary": {
            "total_running": 1,
            "total_pending": 2,
            "total_completed": 23,
            "total_failed": 0
        }
    }
}
```

### 通用接口

#### 1. 任务状态查询
```http
GET /tasks/{task_id}/status
```

#### 2. 取消任务
```http
DELETE /tasks/{task_id}
```

#### 3. 健康检查
```http
GET /health
```

## 任务优先级

### 智能体线程池优先级
1. **对话任务** (priority=1): 最高优先级，确保交互响应
2. **优化任务** (priority=2): 中等优先级，内容改进
3. **批量生成** (priority=3): 较低优先级，批量处理

### 系统线程池优先级
1. **系统清理** (priority=1): 高优先级，维护系统健康
2. **其他系统任务** (priority=2): 一般优先级

## 使用示例

### Python客户端示例

```python
import asyncio
import aiohttp

async def example_separated_pools():
    """演示线程池分离使用"""
    
    async with aiohttp.ClientSession() as session:
        # 提交智能体任务（对话）
        chat_response = await session.post(
            "http://localhost:8000/chat/async",
            json={
                "message": "请详细介绍小红书写作技巧", 
                "user_id": "user123",
                "language": "zh-CN"
            }
        )
        chat_data = await chat_response.json()
        chat_task_id = chat_data["data"]["task_id"]
        print(f"聊天任务提交: {chat_task_id} (智能体线程池)")
        
        # 在对话进行时，同时执行系统检查
        cleanup_response = await session.post(
            "http://localhost:8000/system/cleanup"
        )
        cleanup_data = await cleanup_response.json()
        cleanup_task_id = cleanup_data["data"]["task_id"]
        print(f"清理任务提交: {cleanup_task_id} (系统线程池)")
        
        # 检查线程池状态
        pools_response = await session.get(
            "http://localhost:8000/system/pools"
        )
        pools_data = await pools_response.json()
        
        agent_pool = pools_data["data"]["agent_pool"]
        system_pool = pools_data["data"]["system_pool"]
        
        print(f"智能体线程池: 运行{agent_pool['running_tasks']}, 排队{agent_pool['pending_tasks']}")
        print(f"系统线程池: 运行{system_pool['running_tasks']}, 排队{system_pool['pending_tasks']}")
        
        # 等待任务完成
        while True:
            # 检查聊天任务
            chat_status_response = await session.get(
                f"http://localhost:8000/tasks/{chat_task_id}/status"
            )
            chat_status = await chat_status_response.json()
            
            # 检查清理任务  
            cleanup_status_response = await session.get(
                f"http://localhost:8000/tasks/{cleanup_task_id}/status"
            )
            cleanup_status = await cleanup_status_response.json()
            
            if (chat_status["data"]["status"] == "completed" and 
                cleanup_status["data"]["status"] == "completed"):
                print("所有任务完成!")
                print(f"对话耗时: {chat_status['data']['execution_time']:.2f}秒")
                print(f"清理耗时: {cleanup_status['data']['execution_time']:.2f}秒")
                break
                
            await asyncio.sleep(2)

# 运行示例
asyncio.run(example_separated_pools())
```

### curl示例

```bash
# 1. 提交智能体任务
curl -X POST "http://localhost:8000/chat/async" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "请介绍小红书写作技巧",
    "user_id": "user123", 
    "language": "zh-CN"
  }'

# 返回: {"success":true,"data":{"task_id":"chat_user123_abc12345","pool":"agent"}}

# 2. 在对话进行时提交系统任务
curl -X POST "http://localhost:8000/system/cleanup?max_age_hours=24"

# 返回: {"success":true,"data":{"task_id":"cleanup_system_xyz98765","pool":"system"}}

# 3. 检查线程池状态
curl "http://localhost:8000/system/pools"

# 4. 查询任务状态
curl "http://localhost:8000/tasks/chat_user123_abc12345/status"
curl "http://localhost:8000/tasks/cleanup_system_xyz98765/status"
```

## 配置参数

### 智能体线程池配置
```python
AGENT_THREAD_CONFIG = {
    "max_workers": 3,      # 最大工作线程数
    "queue_size": 20,      # 任务队列容量
    "pool_name": "agent"   # 线程池名称
}
```

### 系统线程池配置
```python
SYSTEM_THREAD_CONFIG = {
    "max_workers": 5,      # 最大工作线程数
    "queue_size": 50,      # 任务队列容量  
    "pool_name": "system"  # 线程池名称
}
```

### 任务配置
```python
TASK_CONFIG = {
    "task_timeout": 300,   # 任务超时时间（秒）
    "cleanup_interval": 3600,  # 清理间隔（秒）
    "max_age_hours": 24    # 保留任务记录时间（小时）
}
```

## 性能优势

### 1. 避免阻塞
- **传统单线程池**: 长时间对话会阻塞系统功能
- **分离式架构**: 对话和系统功能完全独立

### 2. 资源优化
- **智能体线程池**: 较少线程，专注AI任务的高质量处理
- **系统线程池**: 较多线程，快速响应系统请求

### 3. 并发能力
- **智能体任务**: 3个并发，适合CPU密集型AI任务
- **系统任务**: 5个并发，适合I/O密集型系统任务

### 4. 故障隔离
- 任一线程池故障不影响另一个
- 独立的错误处理和恢复机制

## 监控和调试

### 实时监控
```bash
# 获取系统概览
curl "http://localhost:8000/health" | jq '.data.system_status'

# 获取详细线程池状态
curl "http://localhost:8000/system/pools" | jq '.'

# 查看特定任务
curl "http://localhost:8000/tasks/{task_id}/status" | jq '.'
```

### 日志分析
日志中会标明任务使用的线程池：
```
[INFO] 任务 generate_user123_abc12345 已提交到线程池 [agent]
[INFO] 任务 cleanup_system_xyz98765 已提交到线程池 [system]
[INFO] 任务 generate_user123_abc12345 在线程池 [agent] 执行完成，耗时 15.32秒
[INFO] 任务 cleanup_system_xyz98765 在线程池 [system] 执行完成，耗时 2.15秒
```

## 最佳实践

### 1. 任务选择
- **智能体线程池**: 对话、生成、优化、批量AI任务
- **系统线程池**: 清理、监控、状态查询、配置更新

### 2. 并发控制
- 智能体任务数量控制在队列容量内(20个)
- 系统任务可以更高并发(50个)

### 3. 错误处理
```python
try:
    # 提交任务
    task_id = await submit_agent_task(...)
    
    # 等待完成
    result = await wait_for_completion(task_id)
    
    if result["status"] == "failed":
        # 处理失败情况
        print(f"任务失败: {result['error']}")
        
except Exception as e:
    print(f"提交任务失败: {e}")
```

### 4. 性能调优
- 根据硬件配置调整线程数
- 监控队列使用率，避免满载
- 定期清理历史任务记录

## 故障排除

### 常见问题

#### 1. 队列满载
**问题**: `HTTP 429 - 线程池 [agent] 任务队列已满`
**解决**: 等待任务完成或增加队列容量

#### 2. 任务超时
**问题**: 任务状态显示 `timeout`
**解决**: 检查AI服务连接，增加超时时间

#### 3. 系统功能无响应
**问题**: 系统清理等功能无法执行
**解决**: 检查系统线程池状态，确保未满载

#### 4. 跨线程池查询失败
**问题**: 任务ID在错误的线程池中查询
**解决**: 使用统一的任务状态查询接口

### 调试命令
```bash
# 检查所有线程池状态
curl "http://localhost:8000/system/pools"

# 强制清理系统
curl -X POST "http://localhost:8000/system/cleanup/sync"

# 查看应用健康状态
curl "http://localhost:8000/health"

# 取消阻塞任务
curl -X DELETE "http://localhost:8000/tasks/{task_id}"
```

## 示例演示

运行完整的演示脚本：
```bash
python examples/multi_threading_demo.py
```

演示内容包括：
1. 线程池分离功能
2. 并发智能体和系统任务
3. 负载均衡测试
4. 系统监控展示

该演示将验证分离式多线程架构的所有优势，确保在对话过程中系统功能正常可用。 