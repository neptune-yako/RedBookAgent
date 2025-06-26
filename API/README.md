# 小红书文案生成智能体 API 模块

这是一个解耦后的FastAPI后端服务，将原本单一的`fastapi_server.py`文件拆分成多个模块，提高了代码的可维护性和扩展性。

## 📁 模块结构

```
API/
├── __init__.py          # 包初始化文件
├── main.py              # 主应用入口
├── config.py            # 配置和常量
├── models.py            # 数据模型定义
├── sse.py               # SSE相关功能
├── services.py          # 业务逻辑服务
├── routes/              # 路由模块
│   ├── __init__.py
│   ├── base.py          # 基础路由（根路径、健康检查）
│   ├── content.py       # 内容生成相关路由
│   ├── chat.py          # 聊天相关路由
│   ├── feedback.py      # 反馈相关路由
│   ├── sse.py           # SSE连接相关路由
│   └── history.py       # 历史记录相关路由
└── README.md            # 本文档
```

## 🚀 使用方法

### 启动服务器
```bash
# 使用新的解耦版服务器
python fastapi_server_new.py

# 或者直接运行API模块
python -m uvicorn API.main:app --host 0.0.0.0 --port 8000 --reload
```

### 原有服务器（向后兼容）
```bash
# 原版本仍然可用
python fastapi_server.py
```

## 📦 模块说明

### config.py
- 应用配置参数
- 日志配置
- CORS配置
- SSE配置
- API端点信息

### models.py
- 所有Pydantic数据模型
- 请求和响应模型定义
- 数据验证规则

### sse.py
- SSE消息格式化
- SSE连接管理
- 心跳任务管理

### services.py
- `AgentService`: 智能体服务管理
- `SessionService`: 用户会话管理
- `StreamService`: 流式处理服务

### routes/
各个功能模块的路由定义：
- `base.py`: 根路径和健康检查
- `content.py`: 文案生成和优化
- `chat.py`: 对话聊天功能
- `feedback.py`: 智能反馈回环
- `sse.py`: SSE连接管理
- `history.py`: 版本历史管理

## 🔧 优势

1. **模块化设计**: 功能按模块分离，便于维护和扩展
2. **职责分离**: 配置、模型、服务、路由各司其职
3. **代码复用**: 公共服务可以被多个路由使用
4. **测试友好**: 每个模块可以独立测试
5. **可扩展性**: 新功能可以轻松添加新的路由模块

## 🔄 迁移指南

从原版`fastapi_server.py`迁移到新的模块化结构：

1. **无需更改客户端代码**: API接口保持完全兼容
2. **配置调整**: 配置参数移至`config.py`
3. **服务扩展**: 新功能添加到对应的服务模块
4. **路由扩展**: 新API端点添加到对应的路由模块

## 📚 开发指南

### 添加新功能
1. 在`models.py`中定义数据模型
2. 在`services.py`中实现业务逻辑
3. 在相应的路由文件中添加API端点
4. 在`main.py`中注册新路由（如需要）

### 修改配置
- 应用配置: 修改`config.py`中的相关常量
- 路由配置: 修改对应路由文件的路由装饰器

### 调试和日志
- 所有模块使用统一的日志配置
- 可以通过修改`config.py`中的日志级别进行调试 