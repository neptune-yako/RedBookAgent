# 小红书文案生成智能体 API - Swagger 文档指南

## 🚀 快速启动

### 方式一：使用启动脚本（推荐）
```bash
python start_swagger_docs.py
```
这个脚本会自动：
- 启动API服务器
- 检查服务器状态
- 自动打开Swagger文档页面

### 方式二：手动启动
```bash
# 启动服务器
python fastapi_server.py

# 或使用 uvicorn
uvicorn fastapi_server:app --host 0.0.0.0 --port 8000 --reload
```

然后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 Swagger UI 使用指南

### 1. 接口分类
文档按功能分为以下几个类别：
- **基础信息** - API状态和健康检查
- **内容生成** - 小红书文案生成
- **内容优化** - 文案优化和改进
- **对话聊天** - AI助手对话
- **智能反馈** - 反馈回环处理
- **版本管理** - 历史版本管理
- **SSE连接** - 实时流式连接

### 2. 测试API接口

#### 步骤1：选择接口
点击任意接口展开详细信息

#### 步骤2：点击"Try it out"
在接口详情页面点击右上角的"Try it out"按钮

#### 步骤3：填写参数
根据接口要求填写请求参数，Swagger会提供：
- 参数说明
- 示例值
- 必填/可选标识

#### 步骤4：执行请求
点击"Execute"按钮发送请求

#### 步骤5：查看响应
在下方查看：
- 响应状态码
- 响应内容
- 响应头信息

### 3. 示例请求

#### 生成小红书文案
```json
{
  "category": "美食探店",
  "topic": "新开的日式料理店初体验",
  "tone": "活泼可爱",
  "length": "中等",
  "keywords": ["日式料理", "新店", "美味"],
  "target_audience": "年轻女性",
  "special_requirements": "要有个人体验感",
  "user_id": "user_001"
}
```

#### 优化内容
```json
{
  "content": "今天去了一家新开的日式料理店，味道不错，环境也很好。",
  "user_id": "user_001"
}
```

#### 智能反馈
```json
{
  "content": "生成的文案内容...",
  "feedback": "需要优化",
  "user_id": "user_001"
}
```

## 🔄 SSE实时流式接口

### 特殊说明
以下接口支持Server-Sent Events (SSE)实时流式输出：
- `/generate/stream` - 流式生成文案
- `/optimize/stream` - 流式优化内容  
- `/chat/stream` - 流式对话聊天
- `/feedback/stream` - 流式反馈处理

### 在Swagger中测试SSE
1. 点击SSE接口的"Try it out"
2. 填写请求参数
3. 点击"Execute"
4. 在Response部分可以看到实时的流式输出

### SSE消息格式示例
```
event: chunk
data: {"type": "chunk", "chunk": "姐妹们！", "timestamp": "2024-01-15T10:30:00Z"}

event: complete  
data: {"type": "complete", "content": "完整内容...", "version": 1}
```

## 🔍 API 功能详解

### 1. 内容生成参数详解

| 参数 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| category | string | 内容分类 | "美食探店" |
| topic | string | 主题描述 | "新开的日式料理店体验" |
| tone | string | 语调风格 | "活泼可爱" |
| length | string | 内容长度 | "中等" |
| keywords | array | 关键词列表 | ["日料", "新店"] |
| target_audience | string | 目标受众 | "年轻女性" |
| special_requirements | string | 特殊要求 | "突出性价比" |
| user_id | string | 用户ID | "user_001" |

### 2. 语调风格选项
- **活泼可爱** - 年轻化、emoji丰富、互动性强
- **温馨治愈** - 温暖、舒缓、情感丰富
- **专业详细** - 客观、专业、信息量大
- **幽默搞笑** - 轻松、有趣、调侃式
- **简洁明了** - 直接、简练、要点突出

### 3. 内容长度选项
- **短** - 100-200字，适合朋友圈分享
- **中等** - 200-500字，适合标准小红书笔记
- **长** - 500-800字，适合深度测评

### 4. 反馈类型
- **不满意** - 完全重新生成
- **满意** - 在现有基础上优化
- **需要优化** - 保持主体，优化细节
- **完全满意** - 结束处理流程

## 📋 测试建议

### 1. 基础功能测试流程
1. 健康检查 - `GET /health`
2. 生成文案 - `POST /generate`
3. 查看历史 - `GET /history/{user_id}`
4. 优化内容 - `POST /optimize`
5. 反馈处理 - `POST /feedback`

### 2. SSE功能测试流程
1. 流式生成 - `POST /generate/stream`
2. 流式优化 - `POST /optimize/stream`
3. 流式对话 - `POST /chat/stream`

### 3. 版本管理测试
1. 生成多个版本的内容
2. 查看版本历史
3. 恢复到指定版本
4. 清空历史记录

## 🛠️ 故障排除

### 常见问题

**Q: 接口返回503错误**
A: 智能体未初始化，请检查后端服务配置

**Q: SSE连接断开**
A: 检查网络连接，重新发起请求

**Q: 生成内容为空**
A: 检查输入参数是否完整，特别是topic字段

**Q: 无法访问Swagger文档**
A: 确认服务器已启动，端口8000未被占用

### 调试步骤
1. 检查服务器状态 - `GET /health`
2. 查看浏览器控制台错误信息
3. 检查请求参数格式
4. 查看服务器日志

## 📞 技术支持

如需帮助，请：
1. 查看本指南和API文档
2. 检查常见问题部分
3. 查看详细的错误信息
4. 联系技术支持团队

---

**快速链接:**
- [详细API文档](docs/API_DOCUMENTATION.md)
- [Swagger示例配置](docs/swagger_examples.py)
- [项目README](README.md) 