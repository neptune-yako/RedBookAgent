# 语言检测与切换功能指南

## 概述

所有流式异步接口（`/*/stream/async`）现在都支持智能语言检测和切换功能，能够根据传入的`language`参数自动判断并使用相应的语言进行回答。

## 新增功能

### ✅ 语言验证与切换

系统会自动验证传入的`language`参数：
- ✅ **有效语言**: 直接使用用户指定的语言
- ⚠️ **无效语言**: 自动切换到默认语言（简体中文），并记录警告日志
- 📝 **日志记录**: 记录用户的语言选择和切换情况

### ✅ 支持的语言

| 语言代码 | 语言名称 | 智能体回答语言 |
|---------|---------|--------------|
| `zh-CN` | 简体中文 | 请用简体中文回答 |
| `en-US` | 英语 | Please respond in English |
| `zh-TW` | 繁体中文 | 請用繁體中文回答 |
| `ja-JP` | 日语 | 日本語で回答してください |

## 优化的接口

### 内容生成接口
```bash
POST /content/generate/stream/async
```

### 内容优化接口
```bash
POST /content/optimize/stream/async
```

### 聊天对话接口
```bash
POST /chat/stream/async
```

### 反馈处理接口
```bash
POST /feedback/stream
```

## 使用示例

### Python客户端示例

```python
import httpx
import json

async def test_language_detection():
    """测试语言检测功能"""
    
    client = httpx.AsyncClient()
    
    # 测试有效语言 - 英语
    payload_en = {
        "user_id": "test_user",
        "category": "生活",
        "topic": "健康饮食",
        "tone": "轻松",
        "length": "短",
        "enable_thinking": True,
        "language": "en-US"  # 英语
    }
    
    # 测试无效语言 - 自动切换到默认语言
    payload_invalid = {
        "user_id": "test_user",
        "category": "生活", 
        "topic": "健康饮食",
        "tone": "轻松",
        "length": "短",
        "enable_thinking": True,
        "language": "fr-FR"  # 无效语言，将切换到zh-CN
    }
    
    # 发送请求
    async with client.stream(
        "POST",
        "http://localhost:8000/content/generate/stream/async",
        json=payload_en
    ) as response:
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = json.loads(line[6:])
                print(f"英语回答: {data}")
    
    await client.aclose()
```

### JavaScript客户端示例

```javascript
// 测试语言检测功能
const testLanguageDetection = async () => {
    
    // 测试繁体中文
    const payload = {
        user_id: 'test_user',
        category: '生活',
        topic: '健康饮食',
        tone: '轻松',
        length: '短',
        enable_thinking: true,
        language: 'zh-TW'  // 繁体中文
    };
    
    const response = await fetch('/content/generate/stream/async', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.substring(6));
                console.log('繁体中文回答:', data);
            }
        }
    }
};
```

## 技术实现

### 语言验证逻辑

```python
# 语言判断和验证
from ..i18n import Language

try:
    # 验证语言参数是否有效
    target_language = Language(request.language)
    logger.info(f"用户 {request.user_id} 请求语言: {target_language.value}")
except ValueError:
    # 如果语言无效，使用默认语言
    target_language = Language.ZH_CN
    logger.warning(f"用户 {request.user_id} 使用了无效语言 '{request.language}'，已切换到默认语言: {target_language.value}")
```

### 智能体语言指令

在调用智能体时，会自动添加对应语言的指令：

```python
# 智能体会收到类似这样的指令：
"请用简体中文回答。\n\n[实际的提示词内容]"  # 中文
"Please respond in English.\n\n[实际的提示词内容]"  # 英文
```

## 日志监控

### 成功示例
```log
INFO: 用户 user_123 请求语言: en-US
INFO: 用户 user_123 聊天请求语言: zh-TW
```

### 切换示例  
```log
WARNING: 用户 user_456 使用了无效语言 'fr-FR'，已切换到默认语言: zh-CN
WARNING: 用户 user_789 使用了无效语言 'invalid-lang'，已切换到默认语言: zh-CN
```

## 兼容性

- ✅ **向后兼容**: 现有的API调用无需修改
- ✅ **渐进增强**: 如果不传language参数，默认使用简体中文
- ✅ **容错处理**: 无效的语言代码会自动降级为默认语言
- ✅ **一致性**: 所有流式异步接口都支持相同的语言检测逻辑

## 最佳实践

1. **明确指定语言**: 始终在请求中明确指定`language`参数
2. **错误处理**: 客户端应该处理语言切换的情况
3. **日志监控**: 监控语言切换的警告日志，及时发现客户端问题
4. **用户体验**: 在UI中提供语言选择器，避免用户传入无效语言

## 注意事项

- 语言检测只影响智能体的回答语言，不影响API响应的结构
- 所有SSE消息（状态、错误等）也会使用对应的语言
- 会话历史会记录用户的目标语言偏好
- 智能体的语言指令会被注入到所有Ollama调用中

---

通过这些优化，系统现在能够智能地处理多语言场景，确保用户获得准确的语言回答体验！ 