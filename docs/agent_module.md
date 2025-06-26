# 小红书文案生成智能体

基于LangChain和Ollama构建的智能小红书文案生成工具，支持多种内容类型和智能对话功能。

## 🎯 主要功能

- **🏷️ 多分类文案生成**：支持美妆、穿搭、美食、旅行等10+分类
- **🎨 丰富模板库**：提供各种文案模板和提示词
- **💬 智能对话交互**：基于LangChain Agent的对话式体验
- **🎯 内容优化建议**：智能分析和优化现有文案
- **💡 热门主题推荐**：根据分类推荐热门内容主题
- **🚀 批量生成功能**：支持批量生成多个文案

## 📁 文件结构

```
Agent/
├── __init__.py              # 包初始化文件
├── xiaohongshu_agent.py     # 主要智能体类
├── content_templates.py     # 内容模板库
├── web_interface.py         # Streamlit Web界面
├── demo.py                  # 命令行演示脚本
└── README.md               # 本文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动Ollama服务

```bash
ollama serve
```

### 3. 下载模型（如果未安装）

```bash
ollama pull qwen3-redbook-q8:latest
```

### 4. 运行演示

#### 命令行版本
```bash
python Agent/demo.py
```

#### Web界面版本
```bash
streamlit run Agent/web_interface.py
```

## 💻 使用方法

### 基础使用

```python
from Agent import XiaohongshuAgent, ContentCategory, ContentRequest

# 初始化智能体
agent = XiaohongshuAgent()

# 检查设置
if agent.check_setup():
    # 创建内容请求
    request = ContentRequest(
        category=ContentCategory.BEAUTY,
        topic="冬季护肤保湿攻略",
        tone="专业温和",
        keywords=["保湿", "冬季", "护肤"],
        target_audience="20-30岁女性"
    )
    
    # 生成文案
    result = agent.generate_complete_post(request)
    
    if result["success"]:
        print(result["content"])
    else:
        print(f"生成失败：{result['error']}")
```

### 对话模式

```python
# 与智能体对话
response = agent.chat("帮我写一个美食探店的文案")
print(response)
```

### 内容优化

```python
# 优化现有文案
original_content = "今天试了这个新面膜，效果还不错..."
result = agent.optimize_content(original_content)

if result["success"]:
    print("优化后的文案：")
    print(result["optimized"])
```

### 使用模板库

```python
from Agent import XiaohongshuTemplates, TemplateType

templates = XiaohongshuTemplates()

# 获取随机标题模板
title = templates.get_random_template(TemplateType.TITLE, "美妆护肤")
print(title)

# 获取分类模板
category_templates = templates.get_templates_by_category("美妆护肤")
```

## 🏷️ 支持的内容分类

- 💄 **美妆护肤**：护肤心得、化妆技巧、产品测评
- 👗 **时尚穿搭**：穿搭攻略、服装搭配、时尚趋势
- 🍽️ **美食探店**：餐厅推荐、美食评测、料理分享
- ✈️ **旅行攻略**：景点推荐、旅游路线、出行贴士
- 🌱 **生活方式**：日常分享、生活技巧、居家指南
- 💪 **健身运动**：运动教程、健身心得、体能训练
- 🏠 **家居装饰**：装修灵感、家具推荐、收纳技巧
- 📚 **学习分享**：学习方法、知识总结、技能提升
- 💼 **职场干货**：职业发展、工作技巧、面试经验
- 🛍️ **好物推荐**：产品评测、购物指南、性价比分析

## 🎨 模板类型

### 标题模板
- 各分类专门的标题格式
- 符合小红书风格
- 包含emoji和吸引人的词汇

### 内容模板
- 开头模板：惊喜发现、问题解决、经验分享等
- 结尾模板：互动引导、行动呼吁、情感共鸣等
- 完整模板：产品推荐、攻略分享、体验分享等

### 话题标签
- 分类相关的热门标签
- 符合小红书标签规范
- 按热度和相关性排序

## ⚙️ 配置选项

### ContentRequest 参数

- `category`: 内容分类（ContentCategory枚举）
- `topic`: 主题内容（字符串）
- `tone`: 语气风格（活泼可爱、专业温和等）
- `length`: 内容长度（简短、中等、详细）
- `keywords`: 关键词列表（可选）
- `target_audience`: 目标受众（年轻女性、上班族等）
- `special_requirements`: 特殊要求（可选）

### 语气风格选项

- **活泼可爱**：适合年轻用户，语言轻松有趣
- **专业温和**：适合知识分享，语言专业但易懂
- **幽默风趣**：适合娱乐内容，语言诙谐幽默
- **温馨治愈**：适合生活分享，语言温暖贴心
- **时尚潮流**：适合时尚内容，语言前卫时髦

## 🛠️ 开发说明

### 核心组件

1. **XiaohongshuAgent**: 主要智能体类，基于LangChain构建
2. **OllamaLangChainLLM**: Ollama客户端的LangChain适配器
3. **XiaohongshuTemplates**: 内容模板库管理
4. **ContentRequest**: 内容生成请求数据结构

### 工具系统

智能体内置了以下工具：
- **生成标题**: 为内容生成吸引人的标题
- **生成正文**: 根据需求生成完整的文案内容
- **生成话题标签**: 为内容生成相关的话题标签
- **内容优化**: 对现有文案提供优化建议

### 扩展开发

要添加新的功能或工具，可以：

1. 在`_create_tools()`方法中添加新工具
2. 在模板库中添加新的模板类型
3. 扩展`ContentCategory`枚举添加新分类
4. 修改提示词优化生成效果

## 🐛 故障排除

### 常见问题

1. **Ollama连接失败**
   - 检查Ollama服务是否运行：`ollama serve`
   - 确认端口11434是否可用

2. **模型不存在**
   - 手动下载模型：`ollama pull qwen3-redbook-q8:latest`
   - 检查模型名称是否正确

3. **生成内容质量不佳**
   - 优化提示词内容
   - 调整模型参数
   - 使用内容优化功能

4. **依赖包问题**
   - 升级pip：`pip install --upgrade pip`
   - 重新安装依赖：`pip install -r requirements.txt --force-reinstall`

### 性能优化

- 使用流式生成减少等待时间
- 缓存常用模板和配置
- 批量处理多个请求
- 调整模型参数平衡质量和速度

## 📄 许可证

本项目采用MIT许可证，详情请查看LICENSE文件。

## 🤝 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 支持

如果您在使用过程中遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查Issue列表中是否有类似问题
3. 创建新的Issue描述您的问题
4. 提供详细的错误信息和环境信息 