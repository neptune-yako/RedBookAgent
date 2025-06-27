# 小红书文案生成API - 国际化功能指南

## 概述

小红书文案生成API现已全面支持国际化（i18n），提供多语言接口响应。所有API端点都支持通过语言参数来获取本地化的响应消息。

## 支持的语言

| 语言代码 | 语言名称 | 本地名称 |
|---------|---------|---------|
| `zh-CN` | 简体中文 | 简体中文 |
| `en-US` | 英语（美国） | English (US) |
| `zh-TW` | 繁体中文 | 繁體中文 |
| `ja-JP` | 日语 | 日本語 |

## 使用方法

### 1. GET请求 - 查询参数

对于GET请求，可以通过查询参数指定语言：

```bash
# 获取英语版本的API信息
GET http://localhost:8000/?language=en-US

# 获取日语版本的健康检查
GET http://localhost:8000/health?language=ja-JP

# 获取繁体中文版本的版本历史
GET http://localhost:8000/history/user123?language=zh-TW
```

### 2. POST请求 - 请求体参数

对于POST请求，在请求体中包含`language`字段：

```json
{
  "category": "美食探店",
  "topic": "新开的日式料理店体验",
  "tone": "活泼可爱",
  "length": "中等",
  "target_audience": "年轻女性",
  "user_id": "user_001",
  "language": "en-US"
}
```

## API端点国际化支持

### 基础接口

#### GET / - API根信息
- **查询参数**: `language` (可选，默认: zh-CN)
- **示例**:
  ```bash
  GET /?language=en-US
  ```

#### GET /health - 健康检查
- **查询参数**: `language` (可选，默认: zh-CN)
- **示例**:
  ```bash
  GET /health?language=ja-JP
  ```

### 内容生成接口

#### POST /generate - 生成文案
- **请求体参数**: `language` (可选，默认: zh-CN)
- **响应**: 成功/错误消息将使用指定语言

#### POST /generate/stream - 流式生成文案
- **请求体参数**: `language` (可选，默认: zh-CN)
- **响应**: SSE消息将使用指定语言

#### POST /optimize - 优化内容
- **请求体参数**: `language` (可选，默认: zh-CN)
- **响应**: 成功/错误消息将使用指定语言

#### POST /optimize/stream - 流式优化内容
- **请求体参数**: `language` (可选，默认: zh-CN)
- **响应**: SSE消息将使用指定语言

### 聊天接口

#### POST /chat - 对话聊天
- **请求体参数**: `language` (可选，默认: zh-CN)

#### POST /chat/stream - 流式对话聊天
- **请求体参数**: `language` (可选，默认: zh-CN)

### 反馈接口

#### POST /feedback - 智能反馈回环
- **请求体参数**: `language` (可选，默认: zh-CN)

#### POST /feedback/stream - 流式智能反馈
- **请求体参数**: `language` (可选，默认: zh-CN)

### 历史记录接口

#### GET /history/{user_id} - 获取版本历史
- **查询参数**: `language` (可选，默认: zh-CN)

#### POST /history/restore - 恢复指定版本
- **请求体参数**: `language` (可选，默认: zh-CN)

#### DELETE /history/{user_id} - 清空用户历史
- **查询参数**: `language` (可选，默认: zh-CN)

### SSE连接接口

#### POST /sse/connect - 创建SSE连接
- **请求体参数**: `language` (可选，默认: zh-CN)

#### GET /sse/status/{user_id} - 获取SSE连接状态
- **查询参数**: `language` (可选，默认: zh-CN)

### 国际化专用接口

#### GET /i18n/languages - 获取支持的语言列表
返回所有支持的语言及其信息。

**响应示例**:
```json
{
  "success": true,
  "message": "小红书文案生成智能体 API 服务运行中",
  "data": {
    "supported_languages": {
      "zh-CN": {
        "code": "zh-CN",
        "name": "简体中文",
        "native_name": "简体中文"
      },
      "en-US": {
        "code": "en-US",
        "name": "English (US)",
        "native_name": "English (US)"
      },
      "zh-TW": {
        "code": "zh-TW",
        "name": "繁體中文",
        "native_name": "繁體中文"
      },
      "ja-JP": {
        "code": "ja-JP",
        "name": "日本語", 
        "native_name": "日本語"
      }
    },
    "default_language": "zh-CN",
    "total_languages": 4
  }
}
```

#### GET /i18n/messages - 获取指定语言的所有消息
返回指定语言的所有本地化消息。

**查询参数**: `language` (可选，默认: zh-CN)

**响应示例**:
```json
{
  "success": true,
  "message": "API service running",
  "data": {
    "language": "en-US",
    "messages": {
      "api_running": "Xiaohongshu Content Generation AI Agent API Service Running",
      "service_healthy": "Service Healthy",
      "content_generation_success": "Content generation successful",
      "content_optimization_success": "Content optimization successful",
      // ... 更多消息
    }
  }
}
```

## 响应示例

### 中文响应 (zh-CN)
```json
{
  "success": true,
  "message": "文案生成成功",
  "data": {
    "content": "生成的内容...",
    "version": 1
  }
}
```

### 英语响应 (en-US)
```json
{
  "success": true,
  "message": "Content generation successful",
  "data": {
    "content": "Generated content...",
    "version": 1
  }
}
```

### 日语响应 (ja-JP)
```json
{
  "success": true,
  "message": "コンテンツ生成成功",
  "data": {
    "content": "生成されたコンテンツ...",
    "version": 1
  }
}
```

## 测试国际化功能

项目提供了测试脚本来验证国际化功能：

```bash
# 运行国际化测试
python test_i18n_api.py
```

测试脚本将验证：
1. 不同语言参数的响应
2. 国际化端点的功能
3. 错误消息的本地化

## 最佳实践

### 1. 前端集成
建议前端应用根据用户的语言设置自动选择合适的语言参数：

```javascript
// 获取用户浏览器语言
const userLanguage = navigator.language || navigator.userLanguage;

// 映射到支持的语言
const supportedLanguages = ['zh-CN', 'en-US', 'zh-TW', 'ja-JP'];
const apiLanguage = supportedLanguages.includes(userLanguage) 
  ? userLanguage 
  : 'zh-CN'; // 默认简体中文

// 在API请求中使用
const response = await fetch('/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ...otherParams,
    language: apiLanguage
  })
});
```

### 2. 错误处理
当处理API响应时，应该考虑本地化的错误消息：

```javascript
try {
  const response = await apiCall();
  // 处理成功响应，消息已经是本地化的
  console.log(response.message);
} catch (error) {
  // 错误消息也是本地化的
  console.error(error.detail);
}
```

### 3. 缓存语言偏好
建议在客户端缓存用户的语言偏好：

```javascript
// 保存用户语言偏好
localStorage.setItem('preferredLanguage', selectedLanguage);

// 在后续请求中使用
const preferredLanguage = localStorage.getItem('preferredLanguage') || 'zh-CN';
```

## 注意事项

1. **默认语言**: 如果未指定语言参数，系统默认使用简体中文 (zh-CN)
2. **无效语言**: 如果指定了不支持的语言代码，系统将回退到默认语言
3. **内容生成**: 语言参数仅影响API响应消息的语言，不影响生成内容的语言
4. **一致性**: 建议在整个用户会话中保持一致的语言设置

## 扩展支持

如需添加新的语言支持，请在 `API/i18n.py` 文件中：

1. 在 `Language` 枚举中添加新的语言代码
2. 在 `MESSAGES` 字典中添加对应的翻译
3. 更新相关文档和测试

---

*最后更新时间: 2024-01-15*  
*版本: v1.0.0* 