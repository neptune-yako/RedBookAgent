"""
小红书文案生成智能体演示脚本
命令行版本的功能展示
"""

import sys
import os
from typing import Dict, Any

# 添加上级目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Agent.xiaohongshu_agent import XiaohongshuAgent, ContentCategory, ContentRequest
from content_templates import XiaohongshuTemplates, TemplateType


def print_banner():
    """打印欢迎标语"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                🎉 小红书文案生成智能体 🎉                     ║
    ║              基于LangChain和Ollama构建                        ║
    ║                                                              ║
    ║  功能特色：                                                   ║
    ║  📝 智能文案生成    🎨 丰富模板库    💬 对话式交互             ║
    ║  🎯 内容优化建议    ⚙️ 配置管理      🏷️ 多分类支持            ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def show_menu():
    """显示主菜单"""
    menu = """
    🎯 主菜单 - 请选择功能：
    
    1️⃣  快速生成文案
    2️⃣  模板库浏览
    3️⃣  智能对话模式
    4️⃣  内容优化工具
    5️⃣  批量生成示例
    6️⃣  配置设置
    0️⃣  退出程序
    
    """
    print(menu)


def quick_generate_demo(agent: XiaohongshuAgent):
    """快速生成文案演示"""
    print("\n" + "="*60)
    print("📝 快速生成文案")
    print("="*60)
    
    # 预设的示例请求
    examples = [
        {
            "name": "美妆护肤",
            "request": ContentRequest(
                category=ContentCategory.BEAUTY,
                topic="秋冬护唇攻略",
                tone="温馨治愈",
                keywords=["护唇", "秋冬", "保湿"],
                target_audience="年轻女性"
            )
        },
        {
            "name": "美食探店", 
            "request": ContentRequest(
                category=ContentCategory.FOOD,
                topic="深圳网红火锅店测评",
                tone="活泼可爱",
                keywords=["火锅", "深圳", "探店"],
                target_audience="美食爱好者"
            )
        },
        {
            "name": "穿搭分享",
            "request": ContentRequest(
                category=ContentCategory.FASHION,
                topic="小个子女生秋季穿搭",
                tone="时尚潮流",
                keywords=["小个子", "秋季", "穿搭"],
                target_audience="学生党"
            )
        }
    ]
    
    print("请选择生成示例：")
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['name']} - {example['request'].topic}")
    
    try:
        choice = int(input("\n请输入选择（1-3）："))
        if 1 <= choice <= len(examples):
            selected = examples[choice - 1]
            print(f"\n正在生成：{selected['name']} - {selected['request'].topic}")
            print("⏳ 请稍候...")
            
            result = agent.generate_complete_post(selected['request'])
            
            if result["success"]:
                print("\n✅ 生成成功！")
                print("📋 生成结果：")
                print("-" * 40)
                print(result["content"])
                print("-" * 40)
                
                # 询问是否需要优化
                optimize = input("\n是否需要优化此文案？(y/n): ").lower()
                if optimize == 'y':
                    print("⏳ 正在优化...")
                    opt_result = agent.optimize_content(result["content"])
                    if opt_result["success"]:
                        print("\n🎯 优化结果：")
                        print("-" * 40)
                        print(opt_result["optimized"])
                        print("-" * 40)
                    else:
                        print(f"❌ 优化失败：{opt_result['error']}")
            else:
                print(f"❌ 生成失败：{result['error']}")
        else:
            print("❌ 无效选择")
    except ValueError:
        print("❌ 请输入有效数字")


def template_browser_demo():
    """模板库浏览演示"""
    print("\n" + "="*60)
    print("🎨 模板库浏览")
    print("="*60)
    
    templates = XiaohongshuTemplates()
    categories = ["美妆护肤", "时尚穿搭", "美食探店", "旅行攻略", "生活方式"]
    
    print("请选择查看的分类：")
    for i, cat in enumerate(categories, 1):
        print(f"{i}. {cat}")
    
    try:
        choice = int(input("\n请输入选择（1-5）："))
        if 1 <= choice <= len(categories):
            selected_category = categories[choice - 1]
            print(f"\n📂 {selected_category} 分类模板：")
            
            category_templates = templates.get_templates_by_category(selected_category)
            
            for template_type, template_list in category_templates.items():
                print(f"\n🏷️ {template_type}:")
                if isinstance(template_list, list):
                    for i, template in enumerate(template_list[:3], 1):
                        print(f"  {i}. {template}")
                elif isinstance(template_list, dict):
                    for sub_type, sub_list in list(template_list.items())[:2]:
                        print(f"  📌 {sub_type}:")
                        if isinstance(sub_list, list) and sub_list:
                            print(f"     {sub_list[0]}")
            
            # 演示随机模板
            print(f"\n🎲 随机模板演示：")
            print(f"随机标题: {templates.get_random_template(TemplateType.TITLE, selected_category)}")
            print(f"随机开头: {templates.get_random_template(TemplateType.OPENING)}")
            print(f"随机结尾: {templates.get_random_template(TemplateType.ENDING)}")
            
        else:
            print("❌ 无效选择")
    except ValueError:
        print("❌ 请输入有效数字")


def chat_mode_demo(agent: XiaohongshuAgent):
    """智能对话模式演示"""
    print("\n" + "="*60)
    print("💬 智能对话模式")
    print("="*60)
    print("提示：输入'quit'或'退出'结束对话\n")
    
    # 提供一些示例问题
    examples = [
        "帮我写一个关于秋季穿搭的小红书文案",
        "怎样写出更吸引人的小红书标题？",
        "推荐一些美妆类的热门话题",
        "如何提高小红书文案的互动性？"
    ]
    
    print("💡 示例问题：")
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")
    print()
    
    while True:
        try:
            user_input = input("您：")
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("👋 感谢使用对话模式！")
                break
            
            if not user_input.strip():
                continue
            
            print("⏳ 智能体正在思考...")
            response = agent.chat(user_input)
            print(f"\n智能体：{response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 对话结束！")
            break


def content_optimization_demo(agent: XiaohongshuAgent):
    """内容优化工具演示"""
    print("\n" + "="*60)
    print("🎯 内容优化工具")
    print("="*60)
    
    # 提供示例文案
    sample_content = """
    今天试了这个新面膜，效果还不错。
    用完之后皮肤比较水润，而且味道也很好闻。
    价格也不算贵，性价比挺高的。
    推荐给大家试试看。
    """
    
    print("📝 示例文案：")
    print(sample_content)
    print()
    
    choice = input("是否使用示例文案进行优化？(y/n): ").lower()
    
    if choice == 'y':
        content = sample_content
    else:
        print("请输入您要优化的文案（输入完成后按两次回车）：")
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        content = "\n".join(lines[:-1])  # 去掉最后的空行
    
    if content.strip():
        print("⏳ 正在分析和优化...")
        result = agent.optimize_content(content)
        
        if result["success"]:
            print("\n✅ 优化完成！")
            print("\n📋 原文案：")
            print("-" * 30)
            print(result["original"])
            print("-" * 30)
            print("\n🎯 优化后：")
            print("-" * 30)
            print(result["optimized"])
            print("-" * 30)
        else:
            print(f"❌ 优化失败：{result['error']}")
    else:
        print("❌ 请输入有效的文案内容")





def batch_generation_demo(agent: XiaohongshuAgent):
    """批量生成示例演示"""
    print("\n" + "="*60)
    print("🚀 批量生成示例")
    print("="*60)
    
    # 预设的批量生成任务
    batch_requests = [
        ContentRequest(
            category=ContentCategory.BEAUTY,
            topic="平价眼霜推荐",
            tone="活泼可爱",
            keywords=["平价", "眼霜", "护肤"],
            target_audience="学生党"
        ),
        ContentRequest(
            category=ContentCategory.FOOD,
            topic="周末brunch推荐",
            tone="温馨治愈",
            keywords=["brunch", "周末", "美食"],
            target_audience="上班族"
        ),
        ContentRequest(
            category=ContentCategory.LIFESTYLE,
            topic="居家办公效率提升",
            tone="专业温和",
            keywords=["居家", "办公", "效率"],
            target_audience="上班族"
        )
    ]
    
    print(f"即将批量生成 {len(batch_requests)} 个文案：")
    for i, req in enumerate(batch_requests, 1):
        print(f"{i}. {req.category.value} - {req.topic}")
    
    confirm = input("\n是否开始批量生成？(y/n): ").lower()
    
    if confirm == 'y':
        results = []
        for i, request in enumerate(batch_requests, 1):
            print(f"\n⏳ 正在生成第 {i}/{len(batch_requests)} 个文案...")
            print(f"主题：{request.topic}")
            
            result = agent.generate_complete_post(request)
            results.append(result)
            
            if result["success"]:
                print("✅ 生成成功")
            else:
                print(f"❌ 生成失败：{result['error']}")
        
        # 显示所有结果
        print("\n" + "="*60)
        print("📋 批量生成结果汇总")
        print("="*60)
        
        for i, (request, result) in enumerate(zip(batch_requests, results), 1):
            print(f"\n🏷️ 文案 {i}：{request.topic}")
            print("-" * 50)
            if result["success"]:
                print(result["content"])
            else:
                print(f"❌ 生成失败：{result['error']}")
            print("-" * 50)
    else:
        print("❌ 取消批量生成")


def config_settings_demo(agent: XiaohongshuAgent):
    """配置设置演示"""
    print("\n" + "="*60)
    print("⚙️ 配置设置")
    print("="*60)
    
    # 显示当前配置
    print("📊 当前配置：")
    print(f"- 流式响应: {'✅ 启用' if agent.enable_stream else '❌ 禁用'}")
    print(f"- 思考模式: {'✅ 启用' if agent.enable_thinking else '❌ 禁用'}")
    print()
    
    # 配置菜单
    print("🔧 配置选项：")
    print("1. 切换流式响应")
    print("2. 切换思考模式")
    print("3. 重置所有配置")
    print("0. 返回主菜单")
    
    try:
        choice = input("\n请选择操作（0-3）：").strip()
        
        if choice == '1':
            new_stream = not agent.enable_stream
            agent.update_config(enable_stream=new_stream)
            status = "启用" if new_stream else "禁用"
            print(f"✅ 流式响应已{status}")
            
        elif choice == '2':
            new_thinking = not agent.enable_thinking
            agent.update_config(enable_thinking=new_thinking)
            status = "启用" if new_thinking else "禁用"
            print(f"✅ 思考模式已{status}")
            
        elif choice == '3':
            agent.update_config(enable_stream=True, enable_thinking=True)
            print("✅ 所有配置已重置为默认值")
            
        elif choice == '0':
            return
            
        else:
            print("❌ 无效选择")
            
    except ValueError:
        print("❌ 请输入有效数字")
    
    print(f"\n💡 提示：")
    print(f"- 流式响应: {'已启用' if agent.enable_stream else '已禁用'}")
    print(f"- 思考模式: {'已启用' if agent.enable_thinking else '已禁用'}") 
    if not agent.enable_thinking:
        print("- 思考模式禁用时，提示词会自动添加 '/no_think'")
        print("- 这将减少模型的思考过程输出，提高响应速度")


def main():
    """主函数"""
    print_banner()
    
    # 初始化智能体
    print("🔧 正在初始化智能体...")
    try:
        agent = XiaohongshuAgent()
        if not agent.check_setup():
            print("❌ 智能体初始化失败，请检查Ollama服务和模型")
            return
        print("✅ 智能体初始化成功！")
    except Exception as e:
        print(f"❌ 初始化错误：{str(e)}")
        return
    
    # 主循环
    while True:
        try:
            show_menu()
            choice = input("请选择功能（0-6）：").strip()
            
            if choice == '0':
                print("\n👋 感谢使用小红书文案生成智能体！")
                break
            elif choice == '1':
                quick_generate_demo(agent)
            elif choice == '2':
                template_browser_demo()
            elif choice == '3':
                chat_mode_demo(agent)
            elif choice == '4':
                content_optimization_demo(agent)
            elif choice == '5':
                batch_generation_demo(agent)
            elif choice == '6':
                config_settings_demo(agent)
            else:
                print("❌ 无效选择，请重新输入")
            
            input("\n按回车键继续...")
            
        except KeyboardInterrupt:
            print("\n\n👋 程序已退出！")
            break
        except Exception as e:
            print(f"❌ 发生错误：{str(e)}")
            input("\n按回车键继续...")


if __name__ == "__main__":
    main() 