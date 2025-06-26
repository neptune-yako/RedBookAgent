# 小红书文案生成智能体 API 文档

## 概述

小红书文案生成智能体 API 是一个基于大语言模型的智能文案生成服务，提供完整的文案创作、优化和对话功能。

### 技术特色
- 🎯 **智能文案生成**: 根据主题和风格要求生成高质量小红书文案
- 🔄 **内容优化**: 对现有文案进行智能优化和改进
- 💬 **对话聊天**: 与AI助手进行自然对话交流
- 📝 **反馈回环**: 基于用户反馈持续改进生成质量
- 📚 **版本管理**: 支持多版本内容管理和历史记录
- 🔄 **实时流式**: 支持SSE实时流式输出

## 快速开始

### 1. 启动服务

```bash
# 启动FastAPI服务
python fastapi_server.py

# 或使用uvicorn
uvicorn fastapi_server:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 访问文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 3. 基础健康检查

```bash
curl http://localhost:8000/health
```

## API 端点详解

### 基础信息

#### GET / - API基本信息
获取API的基本信息、状态和可用端点列表。

#### GET /health - 健康检查
检查API服务和智能体的运行状态。

### 内容生成

#### POST /generate - 生成小红书文案
根据指定的分类、主题、语调等参数生成小红书文案内容。

**请求参数详解:**
- `category`: 内容分类（美妆护肤、时尚穿搭、美食探店等）
- `topic`: 具体主题描述
- `tone`: 语调风格（活泼可爱、温馨治愈、专业详细、幽默搞笑、简洁明了）
- `length`: 内容长度（短、中等、长）
- `keywords`: 关键词列表（可选）
- `target_audience`: 目标受众
- `special_requirements`: 特殊要求
- `user_id`: 用户ID

**示例请求:**
```json
{
  "category": "美食探店",
  "topic": "新开的日式料理店初体验",
  "tone": "活泼可爱",
  "length": "中等",
  "keywords": ["日式料理", "新店", "美味", "性价比"],
  "target_audience": "年轻女性",
  "special_requirements": "要有个人体验感，适合拍照打卡",
  "user_id": "user_001"
}
```

#### POST /generate/stream - 流式生成小红书文案
使用Server-Sent Events实时流式生成小红书文案，支持实时查看生成进度。

### 内容优化

#### POST /optimize - 优化文案内容
对现有文案内容进行智能优化，改进语言表达和结构。

#### POST /optimize/stream - 流式优化文案内容
使用Server-Sent Events实时流式优化文案内容。

### 对话聊天

#### POST /chat - 对话聊天
与AI智能体进行自然语言对话交流。

#### POST /chat/stream - 流式对话聊天
使用Server-Sent Events进行实时流式对话聊天。

### 智能反馈

#### POST /feedback - 智能反馈处理
基于用户反馈对内容进行重新生成或优化处理。

**反馈类型:**
- `不满意`: 完全重新生成新的文案
- `满意`: 在当前基础上进行优化
- `需要优化`: 保持主体内容，进行细节优化
- `完全满意`: 结束处理流程

#### POST /feedback/stream - 流式智能反馈处理
使用Server-Sent Events进行实时流式反馈处理。

### 版本管理

#### GET /history/{user_id} - 获取版本历史
获取指定用户的内容版本历史记录。

#### POST /history/restore - 恢复指定版本
将用户内容恢复到指定的历史版本。

#### DELETE /history/{user_id} - 清空用户历史
清空指定用户的所有历史记录和版本数据。

### SSE连接管理

#### POST /sse/connect - 创建SSE连接
创建Server-Sent Events连接用于实时消息推送。

#### GET /sse/status/{user_id} - 获取SSE连接状态
获取指定用户的Server-Sent Events连接状态信息。

## Server-Sent Events (SSE) 详解

### SSE消息格式

所有SSE消息都遵循以下标准格式：

```
event: [事件类型]
data: {JSON格式的消息数据}

```

### 消息类型

#### 1. 内容块消息 (chunk)
```
event: chunk
data: {
data:   "type": "chunk",
data:   "chunk": "姐妹们！今天发现了一家",
data:   "chunk_type": "content",
data:   "timestamp": "2024-01-15T10:30:00.123Z",
data:   "action": "初始生成",
data:   "chunk_count": 1,
data:   "total_length": 12
data: }
```

#### 2. 完成消息 (complete)
```
event: complete
data: {
data:   "type": "complete",
data:   "content": "完整的生成内容...",
data:   "action": "初始生成",
data:   "version": 1,
data:   "total_chunks": 25,
data:   "total_length": 380,
data:   "timestamp": "2024-01-15T10:30:05.456Z"
data: }
```

#### 3. 错误消息 (error)
```
event: error
data: {
data:   "type": "error",
data:   "message": "生成过程中出现错误",
data:   "code": "GENERATION_ERROR",
data:   "timestamp": "2024-01-15T10:30:02.789Z"
data: }
```

#### 4. 状态消息 (status)
```
event: status
data: {
data:   "type": "status",
data:   "status": "started",
data:   "message": "开始生成...",
data:   "progress": 0.1,
data:   "timestamp": "2024-01-15T10:30:00.000Z"
data: }
```

#### 5. 心跳消息 (heartbeat)
```
event: heartbeat
data: {
data:   "type": "heartbeat",
data:   "timestamp": "2024-01-15T10:30:00.000Z"
data: }
```

### 客户端连接示例

#### JavaScript
```javascript
const eventSource = new EventSource('http://localhost:8000/sse/connect', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    user_id: 'user_001',
    connection_type: 'general'
  })
});

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

eventSource.addEventListener('chunk', function(event) {
  const data = JSON.parse(event.data);
  console.log('Content chunk:', data.chunk);
});

eventSource.addEventListener('complete', function(event) {
  const data = JSON.parse(event.data);
  console.log('Generation complete:', data.content);
});

eventSource.addEventListener('error', function(event) {
  const data = JSON.parse(event.data);
  console.error('Error:', data.message);
});
```

#### Python
```python
import requests
import json

def handle_sse_stream(user_id):
    url = 'http://localhost:8000/generate/stream'
    data = {
        "category": "美食探店",
        "topic": "新开的日式料理店初体验",
        "tone": "活泼可爱",
        "length": "中等",
        "user_id": user_id
    }
    
    response = requests.post(url, json=data, stream=True)
    
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                try:
                    data = json.loads(line_str[6:])
                    if data.get('type') == 'chunk':
                        print(data['chunk'], end='', flush=True)
                    elif data.get('type') == 'complete':
                        print(f"\n\n生成完成！版本: {data.get('version')}")
                        break
                except json.JSONDecodeError:
                    continue
```

## 错误处理

### HTTP状态码

- `200` - 请求成功
- `400` - 请求参数错误
- `500` - 服务器内部错误
- `503` - 服务不可用（智能体未初始化）

### 错误响应格式

```json
{
  "success": false,
  "message": "错误描述",
  "data": null,
  "timestamp": "2024-01-15T10:30:00"
}
```

## 使用建议

### 1. 内容分类选择
根据您的内容类型选择合适的分类：
- **美妆护肤**: 护肤品评测、化妆教程
- **时尚穿搭**: 服装搭配、时尚趋势
- **美食探店**: 餐厅评价、美食推荐
- **旅行攻略**: 旅游指南、景点介绍
- **生活方式**: 日常分享、生活窍门

### 2. 语调风格选择
- **活泼可爱**: 适合年轻受众，emoji丰富，互动性强
- **温馨治愈**: 适合情感类内容，温暖舒缓
- **专业详细**: 适合评测类内容，客观专业
- **幽默搞笑**: 适合娱乐类内容，轻松有趣
- **简洁明了**: 适合信息类内容，直接简练

### 3. 长度选择
- **短** (100-200字): 适合简单推荐、朋友圈分享
- **中等** (200-500字): 适合标准小红书笔记
- **长** (500-800字): 适合深度测评、详细攻略

### 4. 反馈优化流程
1. 生成初始内容
2. 根据质量给出反馈（满意/不满意/需要优化）
3. 系统根据反馈进行相应处理
4. 重复步骤2-3直到满意

### 5. 版本管理最佳实践
- 定期查看历史版本
- 保存满意的版本作为基准
- 利用版本对比功能选择最佳内容

## 性能和限制

### 连接限制
- 每个用户最多可同时维持5个SSE连接
- 连接超时时间：60秒无活动自动断开
- 心跳间隔：30秒

### 内容限制
- 单次生成内容最大长度：2000字
- 关键词列表最多：20个
- 历史版本保存：每用户最多50个版本

### 速率限制
- 内容生成：每分钟最多10次请求
- 对话聊天：每分钟最多20次请求
- 其他接口：每分钟最多50次请求

## 常见问题 (FAQ)

### Q: 如何获得更好的生成效果？
A: 
1. 提供详细具体的主题描述
2. 选择合适的语调和目标受众
3. 添加相关关键词
4. 在特殊要求中说明具体需求

### Q: SSE连接断开了怎么办？
A: 
1. 检查网络连接
2. 重新创建SSE连接
3. 确认用户ID正确

### Q: 生成的内容不满意怎么办？
A: 
1. 使用反馈接口，选择"不满意"重新生成
2. 调整原始参数（语调、长度、特殊要求等）
3. 使用优化接口进行改进

### Q: 如何管理多个版本？
A: 
1. 使用 `/history/{user_id}` 查看所有版本
2. 使用 `/history/restore` 恢复到指定版本
3. 定期清理不需要的历史记录

## 技术支持

如果您在使用过程中遇到问题，请：

1. 查看本文档的常见问题部分
2. 检查 `/health` 端点确认服务状态
3. 查看详细的错误信息和日志
4. 联系技术支持团队

---

*最后更新时间: 2024-01-15*
*API版本: v1.0.0* 