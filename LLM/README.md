# Qwen3-Redbook Ollama 客户端

这个项目提供了连接和使用 Ollama 的 `qwen3-redbook-q8:latest` 模型的 Python 客户端。

## 前置要求

1. **安装 Ollama**
   - 访问 [Ollama 官网](https://ollama.ai/) 下载并安装
   - 或使用命令安装（Linux/macOS）：
     ```bash
     curl -fsSL https://ollama.ai/install.sh | sh
     ```

2. **启动 Ollama 服务**
   ```bash
   ollama serve
   ```

3. **拉取 Qwen3-Redbook 模型**
   ```bash
   ollama pull qwen3-redbook-q8:latest
   ```

4. **安装 Python 依赖**
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

### 1. 完整功能演示
运行主客户端，包含连接检查、模型检查、文本生成和交互式对话：

```bash
cd LLM
python ollama_client.py
```

### 2. 简单聊天模式
运行轻量级聊天客户端：

```bash
cd LLM
python simple_chat.py
```

### 3. 编程调用

```python
from ollama_client import OllamaClient

# 创建客户端
client = OllamaClient()

# 检查连接
if client.check_connection():
    print("✅ 连接成功!")
    
    # 简单文本生成
    response = client.generate("写一篇小红书种草文案", stream=True)
    
    # 对话模式
    messages = [
        {"role": "user", "content": "你好，请介绍一下自己"}
    ]
    response = client.chat(messages, stream=True)
```

## 功能特性

- ✅ **自动连接检查**: 自动检测 Ollama 服务状态
- ✅ **模型管理**: 检查模型存在性，支持自动拉取
- ✅ **流式输出**: 支持实时显示生成内容
- ✅ **对话历史**: 保持上下文连续对话
- ✅ **错误处理**: 完善的异常处理机制
- ✅ **中文支持**: 全中文界面和交互

## API 接口

### OllamaClient 类

#### 初始化
```python
client = OllamaClient(base_url="http://localhost:11434")
```

#### 主要方法

- `check_connection()`: 检查 Ollama 服务连接
- `list_models()`: 获取可用模型列表
- `check_model_exists()`: 检查目标模型是否存在
- `pull_model()`: 拉取模型
- `generate(prompt, stream=False)`: 文本生成
- `chat(messages, stream=False)`: 对话模式

## 故障排除

### 1. 连接失败
```
❌ 无法连接到Ollama服务
```
**解决方案**: 确保 Ollama 服务正在运行
```bash
ollama serve
```

### 2. 模型不存在
```
❌ 模型不存在
```
**解决方案**: 拉取模型
```bash
ollama pull qwen3-redbook-q8:latest
```

### 3. 依赖缺失
```
ModuleNotFoundError: No module named 'requests'
```
**解决方案**: 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 端口冲突
如果默认端口 11434 被占用，可以修改 Ollama 服务端口：
```bash
OLLAMA_HOST=0.0.0.0:11435 ollama serve
```

然后在代码中修改客户端 URL：
```python
client = OllamaClient(base_url="http://localhost:11435")
```

## 配置选项

### 环境变量
- `OLLAMA_HOST`: Ollama 服务地址 (默认: localhost:11434)

### 模型配置
可以在 `ollama_client.py` 中修改 `model_name` 来使用不同的模型：
```python
self.model_name = "your-model-name:latest"
```

## 许可证

MIT License 