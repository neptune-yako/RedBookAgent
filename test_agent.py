#!/usr/bin/env python
"""
小红书文案生成智能体 - 功能测试脚本
"""

import sys
import os
from pathlib import Path

# 添加Agent模块到路径
sys.path.append(str(Path(__file__).parent / "Agent"))

try:
    from xiaohongshu_agent import XiaohongshuAgent, ContentCategory, ContentRequest
    from content_templates import XiaohongshuTemplates, TemplateType
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)

def test_template_system():
    """测试模板系统"""
    print("🧪 测试模板系统...")
    
    templates = XiaohongshuTemplates()
    
    # 测试获取分类模板
    category_templates = templates.get_templates_by_category("美妆护肤")
    assert "标题" in category_templates, "标题模板不存在"
    print("✅ 分类模板获取正常")
    
    # 测试随机模板
    random_title = templates.get_random_template(TemplateType.TITLE, "美妆护肤")
    assert random_title, "随机标题模板获取失败"
    print("✅ 随机模板获取正常")
    
    # 测试结构化提示词
    prompt = templates.generate_structured_prompt("美妆护肤", "护肤攻略", "活泼")
    assert "护肤攻略" in prompt, "结构化提示词生成失败"
    print("✅ 结构化提示词生成正常")
    
    print("🎉 模板系统测试通过！\n")

def test_agent_initialization():
    """测试智能体初始化"""
    print("🧪 测试智能体初始化...")
    
    try:
        # 测试默认配置
        agent = XiaohongshuAgent()
        print("✅ 智能体创建成功（默认配置）")
        
        # 测试基本属性
        assert hasattr(agent, 'ollama_client'), "缺少ollama_client属性"
        assert hasattr(agent, 'tools'), "缺少tools属性"
        assert hasattr(agent, 'agent'), "缺少agent属性"
        assert hasattr(agent, 'enable_stream'), "缺少enable_stream属性"
        assert hasattr(agent, 'enable_thinking'), "缺少enable_thinking属性"
        print("✅ 智能体属性检查通过")
        
        # 测试配置
        assert agent.enable_stream == True, "默认流式响应配置错误"
        assert agent.enable_thinking == True, "默认思考模式配置错误"
        print("✅ 默认配置检查通过")
        
        # 测试工具数量
        assert len(agent.tools) >= 4, f"工具数量不足，当前: {len(agent.tools)}"
        print(f"✅ 工具数量正常: {len(agent.tools)}个")
        
        # 测试自定义配置
        agent_custom = XiaohongshuAgent(enable_stream=False, enable_thinking=False)
        assert agent_custom.enable_stream == False, "自定义流式响应配置错误"
        assert agent_custom.enable_thinking == False, "自定义思考模式配置错误"
        print("✅ 自定义配置检查通过")
        
        # 测试配置更新
        agent.update_config(enable_stream=False)
        assert agent.enable_stream == False, "配置更新失败"
        print("✅ 配置更新功能正常")
        
        print("🎉 智能体初始化测试通过！\n")
        return agent
        
    except Exception as e:
        print(f"❌ 智能体初始化失败: {e}")
        return None

def test_content_request():
    """测试内容请求"""
    print("🧪 测试内容请求...")
    
    # 创建测试请求
    request = ContentRequest(
        category=ContentCategory.BEAUTY,
        topic="测试护肤攻略",
        tone="活泼可爱",
        keywords=["测试", "护肤"],
        target_audience="年轻女性"
    )
    
    assert request.category == ContentCategory.BEAUTY, "分类设置错误"
    assert request.topic == "测试护肤攻略", "主题设置错误"
    assert "测试" in request.keywords, "关键词设置错误"
    
    print("✅ 内容请求创建正常")
    print("🎉 内容请求测试通过！\n")
    
    return request

def test_ollama_connection():
    """测试Ollama连接"""
    print("🧪 测试Ollama连接...")
    
    try:
        from LLM.ollama_client import OllamaClient
        
        client = OllamaClient()
        
        # 测试连接
        if client.check_connection():
            print("✅ Ollama服务连接正常")
            
            # 测试模型
            if client.check_model_exists():
                print("✅ 模型存在")
                print("🎉 Ollama连接测试通过！\n")
                return True
            else:
                print("⚠️ 模型不存在，请运行: ollama pull qwen3-redbook-q8:latest")
                return False
        else:
            print("❌ Ollama服务连接失败")
            print("💡 请确保Ollama正在运行: ollama serve")
            return False
            
    except Exception as e:
        print(f"❌ Ollama连接测试失败: {e}")
        return False

def test_basic_generation():
    """测试基本生成功能（仅当Ollama可用时）"""
    print("🧪 测试基本生成功能...")
    
    if not test_ollama_connection():
        print("⚠️ 跳过生成测试（Ollama不可用）\n")
        return
    
    try:
        # 测试默认配置（思考模式开启）
        agent = XiaohongshuAgent(enable_thinking=True)
        
        # 创建简单请求
        request = ContentRequest(
            category=ContentCategory.BEAUTY,
            topic="简单护肤测试",
            tone="活泼可爱"
        )
        
        print("⏳ 正在测试文案生成（思考模式开启）...")
        result = agent.generate_complete_post(request)
        
        if result["success"]:
            print("✅ 文案生成成功（思考模式）")
            print(f"📝 生成内容长度: {len(result['content'])}字符")
        else:
            print(f"❌ 文案生成失败: {result['error']}")
        
        # 测试无思考模式
        agent_no_think = XiaohongshuAgent(enable_thinking=False)
        print("⏳ 正在测试文案生成（思考模式关闭）...")
        result_no_think = agent_no_think.generate_complete_post(request)
        
        if result_no_think["success"]:
            print("✅ 文案生成成功（无思考模式）")
            print(f"📝 生成内容长度: {len(result_no_think['content'])}字符")
            print("🎉 基本生成功能测试通过！\n")
        else:
            print(f"❌ 无思考模式文案生成失败: {result_no_think['error']}")
            
    except Exception as e:
        print(f"❌ 生成测试失败: {e}")

def main():
    """主测试函数"""
    print("🧪 小红书文案生成智能体 - 功能测试")
    print("=" * 60)
    
    # 运行各项测试
    test_template_system()
    agent = test_agent_initialization()
    test_content_request()
    test_basic_generation()
    
    print("=" * 60)
    print("🎉 测试完成！")
    
    if agent:
        print("\n💡 提示：")
        print("- 使用 python Agent/demo.py 启动命令行版本")
        print("- 使用 python start_web.py 启动Web界面")
        print("- 使用 streamlit run Agent/web_interface.py 直接启动Web界面")

if __name__ == "__main__":
    main() 