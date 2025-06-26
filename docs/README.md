# 📚 小红书文案生成智能体 - 文档目录

## 📋 文档概览

本目录包含小红书文案生成智能体项目的所有相关文档，按照功能和类型进行分类整理。

## 📁 目录结构

```
docs/
├── README.md                     # 本文件 - 文档索引
├── agent_module.md               # Agent模块说明文档
├── llm_module.md                 # LLM模块说明文档
├── features/                     # 功能特性文档
│   ├── FEATURES.md               # 项目核心功能介绍
│   ├── STREAM_FEATURES.md        # 流式功能说明
│   ├── INTELLIGENT_LOOP_README.md # 智能反馈回环功能
│   └── VERSION_HISTORY_FEATURE.md # 版本历史管理功能
├── api/                          # API相关文档
│   └── FASTAPI_README.md         # FastAPI后端API文档
└── development/                  # 开发记录文档
    ├── VERSION_HISTORY_FIX_SUMMARY.md     # 版本历史修复记录
    ├── UI_UX_OPTIMIZATION_SUMMARY.md      # UI/UX优化记录
    ├── GENERATION_UI_UPDATE_SUMMARY.md    # 生成界面更新记录
    ├── LOOP_FIX_SUMMARY.md               # 智能回环修复记录
    ├── CONTENT_GENERATION_FIX_SUMMARY.md # 内容生成修复记录
    └── CHAT_FIX_SUMMARY.md               # 聊天功能修复记录
```

## 🎯 快速导航

### 📖 核心文档
- **[项目主文档](../README.md)** - 项目总览、安装和使用指南
- **[功能特性](features/FEATURES.md)** - 项目核心功能介绍
- **[Agent模块](agent_module.md)** - 智能体核心模块文档
- **[LLM模块](llm_module.md)** - 大语言模型集成模块文档

### 🚀 部署和API
- **[FastAPI后端](api/FASTAPI_README.md)** - FastAPI版本部署和API文档
- **Streamlit Web版** - 参考[项目主文档](../README.md)中的启动说明

### ✨ 核心功能
- **[智能反馈回环](features/INTELLIGENT_LOOP_README.md)** - 核心智能体交互功能
- **[版本历史管理](features/VERSION_HISTORY_FEATURE.md)** - 内容版本控制功能
- **[流式处理](features/STREAM_FEATURES.md)** - 实时内容生成功能

### 🔧 开发参考
- **[开发记录](development/)** - 功能开发和问题修复的详细记录
- **修复总结** - 各个功能模块的问题修复过程记录

## 🎨 文档类型说明

### 📘 功能文档 (`features/`)
包含项目各个功能模块的详细说明，适合：
- 了解功能特性和使用方法
- 功能配置和自定义
- 功能原理和设计思路

### 🔌 API文档 (`api/`)
包含API接口的详细说明，适合：
- 集成开发
- 前后端分离部署
- 第三方系统对接

### 🛠️ 开发文档 (`development/`)
包含开发过程中的记录和总结，适合：
- 了解项目演进历程
- 问题排查和调试
- 功能扩展和维护

## 📋 文档维护

### 文档更新原则
1. **功能文档**：随功能更新同步维护
2. **API文档**：随接口变更同步维护  
3. **开发文档**：记录重要的开发决策和修复过程

### 文档命名规范
- 功能文档：使用简洁的功能名称
- 修复记录：使用`模块名_FIX_SUMMARY.md`格式
- 更新记录：使用`模块名_UPDATE_SUMMARY.md`格式

## 🤝 贡献指南

如需添加或更新文档，请：
1. 在相应目录下创建或编辑文档
2. 更新本索引文件的相关链接
3. 保持文档格式的一致性

---

📅 **最后更新**: 2024年6月26日  
📝 **维护者**: 项目开发团队 