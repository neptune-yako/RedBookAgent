# 流式接口线程池功能指南

## 概述

为了提高并发性能和系统稳定性，我们为小红书文案生成智能体的流式接口（SSE）添加了线程池支持。现在每个流式接口都有两个版本：

1. **直接执行版本** - 在主线程中直接处理请求
2. **线程池执行版本** - 在智能体专用线程池中处理请求

## 新增接口

### 内容生成流式接口

```bash
# 直接执行（原有接口）
POST /content/generate/stream

# 线程池执行（新增接口） 
POST /content/generate/stream/async
```

### 内容优化流式接口

```bash
# 直接执行（原有接口）
POST /content/optimize/stream

# 线程池执行（新增接口）
POST /content/optimize/stream/async
```

### 对话聊天流式接口

```bash
# 直接执行（原有接口）
POST /chat/stream

# 线程池执行（新增接口）
POST /chat/stream/async
```

## 技术架构

### 双线程池架构

系统现在采用双线程池架构：

- **智能体线程池**: 专门处理AI相关任务（生成、优化、聊天）
  - 最大工作线程数: 3
  - 队列大小: 20
  - 任务超时: 300秒

- **系统线程池**: 专门处理系统功能（清理、监控）
  - 最大工作线程数: 5
  - 队列大小: 50
  - 任务超时: 60秒

### 流式任务处理流程

1. **任务提交**: 流式生成器函数被包装成任务提交到线程池
2. **线程执行**: 在工作线程中执行生成器，收集所有输出块
3. **结果转换**: 将线程池结果转换为SSE流式输出
4. **客户端接收**: 客户端通过EventSource接收流式数据

## 使用示例

### Python客户端示例

```python
import httpx
import json
import asyncio

async def test_stream_with_threadpool():
    """测试线程池版本的流式接口"""
    
    client = httpx.AsyncClient(http2=True, verify=False)
    
    payload = {
        "user_id": "test_user",
        "category": "生活",
        "topic": "健康饮食",
        "tone": "轻松",
        "length": "短",
        "enable_thinking": True,
        "language": "zh-CN"
    }
    
    # 使用线程池版本的流式接口
    async with client.stream(
        "POST", 
        "https://localhost:8443/content/generate/stream/async",
        json=payload
    ) as response:
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = json.loads(line[6:])
                print(f"收到消息: {data['type']} - {data.get('message', '')}")
    
    await client.aclose()

# 运行测试
asyncio.run(test_stream_with_threadpool())
```

### JavaScript客户端示例

```javascript
// 测试线程池版本的流式接口
const testStreamWithThreadPool = async () => {
    const eventSource = new EventSource('/content/generate/stream/async', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: 'test_user',
            category: '生活',
            topic: '健康饮食',
            tone: '轻松',
            length: '短',
            enable_thinking: true,
            language: 'zh-CN'
        })
    });
    
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(`收到消息: ${data.type} - ${data.message || ''}`);
        
        if (data.type === 'complete') {
            eventSource.close();
            console.log('流式处理完成');
        }
    };
    
    eventSource.onerror = (error) => {
        console.error('SSE连接错误:', error);
        eventSource.close();
    };
};
```

## 性能优势

### 直接执行 vs 线程池执行

| 特性 | 直接执行 | 线程池执行 |
|------|---------|------------|
| **响应速度** | 快速启动 | 轻微延迟（任务排队） |
| **并发能力** | 受主线程限制 | 支持更高并发 |
| **资源管理** | 可能阻塞主线程 | 隔离执行，不影响主线程 |
| **错误隔离** | 错误可能影响其他请求 | 错误被隔离在工作线程中 |
| **负载均衡** | 无 | 自动负载均衡 |

### 建议使用场景

- **直接执行版本**: 适用于低并发、快速响应的场景
- **线程池版本**: 适用于高并发、长时间运行的场景

## 配置参数

### 线程池配置

```python
THREAD_CONFIG = {
    "agent_pool": {
        "max_workers": 3,      # 智能体线程池大小
        "queue_size": 20,      # 任务队列大小
        "task_timeout": 300,   # 任务超时时间（秒）
    },
    "system_pool": {
        "max_workers": 5,      # 系统线程池大小
        "queue_size": 50,      # 任务队列大小  
        "task_timeout": 60,    # 任务超时时间（秒）
    }
}
```

### 优先级设置

流式任务在线程池中的优先级：

- **聊天流式任务**: 优先级 1（最高）
- **生成流式任务**: 优先级 1（最高）
- **优化流式任务**: 优先级 1（最高）

## 监控和调试

### 系统状态监控

```bash
# 查看线程池状态
GET /system/pools

# 查看任务状态
GET /tasks/{task_id}/status

# 系统整体状态
GET /system/status
```

### 日志信息

系统会记录以下关键信息：

- 任务提交到线程池
- 任务开始执行
- 任务执行完成
- 任务执行失败
- 线程池状态变化

## 测试工具

我们提供了专门的测试脚本：

```bash
# 测试所有流式接口的线程池功能
python test_stream_threadpool.py
```

测试脚本会验证：

1. 所有流式接口的基本功能
2. 直接执行 vs 线程池执行的性能对比
3. 并发流式请求的处理能力
4. 错误处理和恢复机制

## 最佳实践

### 1. 选择合适的接口版本

```python
# 低并发场景 - 使用直接执行
if concurrent_users < 10:
    endpoint = "/content/generate/stream"

# 高并发场景 - 使用线程池执行  
else:
    endpoint = "/content/generate/stream/async"
```

### 2. 错误处理

```python
try:
    async with client.stream("POST", endpoint, json=payload) as response:
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = json.loads(line[6:])
                if data['type'] == 'error':
                    print(f"服务器错误: {data['message']}")
                    break
except Exception as e:
    print(f"连接错误: {e}")
```

### 3. 超时设置

```python
# 设置合适的超时时间
client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))
```

## 故障排除

### 常见问题

1. **任务队列满**: 返回 HTTP 429，建议稍后重试
2. **任务超时**: 检查任务复杂度和超时设置
3. **连接中断**: 实现重连机制

### 解决方案

```python
# 实现重试机制
async def stream_with_retry(endpoint, payload, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with client.stream("POST", endpoint, json=payload) as response:
                if response.status_code == 429:  # 队列满
                    await asyncio.sleep(2 ** attempt)  # 指数退避
                    continue
                # 处理响应
                return await process_stream(response)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1)
```

## 更新日志

- **v1.2.0**: 添加流式接口线程池支持
- **v1.2.0**: 实现双线程池架构
- **v1.2.0**: 增加任务优先级管理
- **v1.2.0**: 完善监控和调试功能

## 相关文档

- [HTTP/2.0 升级指南](HTTP2_UPGRADE_GUIDE.md)
- [多线程处理指南](MULTI_THREADING_GUIDE.md)
- [API 文档](API_DOCUMENTATION.md) 