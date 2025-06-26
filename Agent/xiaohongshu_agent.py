"""
小红书文案生成智能体
基于LangChain和Ollama构建的智能文案生成工具
"""

import json
import sys
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# 添加上级目录到路径，以便导入LLM模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LLM.ollama_client import OllamaClient

from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from pydantic import Field, ConfigDict


class ContentCategory(Enum):
    """内容分类枚举"""
    BEAUTY = "美妆护肤"
    FASHION = "时尚穿搭"
    FOOD = "美食探店"
    TRAVEL = "旅行攻略"
    LIFESTYLE = "生活方式"
    FITNESS = "健身运动"
    HOME = "家居装饰"
    STUDY = "学习分享"
    WORK = "职场干货"
    SHOPPING = "好物推荐"


@dataclass
class ContentRequest:
    """内容生成请求"""
    category: ContentCategory
    topic: str
    tone: str = "活泼可爱"
    length: str = "中等"
    keywords: List[str] = None
    target_audience: str = "年轻女性"
    special_requirements: str = ""


class OllamaLangChainLLM(LLM):
    """将Ollama客户端适配为LangChain的LLM接口"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    ollama_client: OllamaClient = Field(default_factory=lambda: OllamaClient())
    enable_stream: bool = Field(default=True)
    enable_thinking: bool = Field(default=True)
    
    @property
    def _llm_type(self) -> str:
        return "ollama"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """调用Ollama生成文本"""
        # 处理思考模式
        if not self.enable_thinking and not prompt.endswith("/no_think"):
            prompt += "/no_think"
        
        response = self.ollama_client.generate(prompt, stream=self.enable_stream)
        return response if response else "抱歉，生成失败，请重试。"


class XiaohongshuAgent:
    """小红书文案生成智能体"""
    
    def __init__(self, enable_stream: bool = True, enable_thinking: bool = True):
        """初始化智能体
        
        Args:
            enable_stream: 是否启用流式响应
            enable_thinking: 是否启用思考模式
        """
        self.ollama_client = OllamaClient()
        self.llm = OllamaLangChainLLM(
            enable_stream=enable_stream,
            enable_thinking=enable_thinking
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # 存储配置
        self.enable_stream = enable_stream
        self.enable_thinking = enable_thinking
        
        # 初始化工具
        self.tools = self._create_tools()
        
        # 初始化智能体
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _create_tools(self) -> List[Tool]:
        """创建智能体使用的工具"""
        
        def generate_title_tool(query: str) -> str:
            """生成小红书标题的工具"""
            prompt = f"""
作为小红书爆款标题专家，请为以下内容生成3个吸引人的标题：

内容描述：{query}

要求：
1. 标题要有吸引力和话题性
2. 适当使用emoji表情
3. 长度控制在15-25字
4. 符合小红书用户习惯
5. 每个标题风格要有差异
6.带emoji、分段清晰

请生成3个标题，用序号分别标注。
"""
            # 处理思考模式
            if not self.enable_thinking:
                prompt += "/no_think"
            
            return self.ollama_client.generate(prompt, stream=self.enable_stream) or "生成失败"
        
        def generate_content_tool(query: str) -> str:
            """生成小红书正文内容的工具"""
            prompt = f"""
作为小红书内容创作专家，请为以下需求生成完整的小红书文案：

需求：{query}

要求：
1. 开头要有吸引人的hook
2. 内容要有价值和实用性
3. 带emoji、分段清晰
4. 结尾要有互动引导
5. 整体风格要符合小红书调性
6. 字数控制在200-500字

请生成完整的小红书文案。
"""
            # 处理思考模式
            if not self.enable_thinking:
                prompt += "/no_think"
            
            return self.ollama_client.generate(prompt, stream=self.enable_stream) or "生成失败"
        
        def generate_hashtags_tool(query: str) -> str:
            """生成小红书话题标签的工具"""
            prompt = f"""
作为小红书话题标签专家，请为以下内容生成相关的话题标签：

内容：{query}

要求：
1. 生成8-12个相关话题标签
2. 包含热门标签和精准标签
3. 标签要符合小红书规范
4. 用#号标注每个标签
5. 按照热度和相关性排序

请生成话题标签列表。
"""
            # 处理思考模式
            if not self.enable_thinking:
                prompt += "/no_think"
            
            return self.ollama_client.generate(prompt, stream=self.enable_stream) or "生成失败"
        
        def content_optimization_tool(query: str) -> str:
            """内容优化建议工具"""
            prompt = f"""
作为小红书内容优化专家，请对以下文案提供优化建议：

文案内容：{query}

请从以下角度提供优化建议：
1. 标题吸引力
2. 内容结构
3. 用词优化
4. emoji使用
5. 互动性提升
6. SEO优化

请提供具体的优化建议和修改建议。
"""
            # 处理思考模式
            if not self.enable_thinking:
                prompt += "/no_think"
            
            return self.ollama_client.generate(prompt, stream=self.enable_stream) or "生成失败"
        
        return [
            Tool(
                name="生成标题",
                func=generate_title_tool,
                description="为小红书内容生成吸引人的标题，输入内容描述即可"
            ),
            Tool(
                name="生成正文",
                func=generate_content_tool,
                description="根据需求生成完整的小红书文案正文内容"
            ),
            Tool(
                name="生成话题标签",
                func=generate_hashtags_tool,
                description="为小红书内容生成相关的话题标签"
            ),
            Tool(
                name="内容优化",
                func=content_optimization_tool,
                description="对已有的小红书文案提供优化建议和改进方案"
            )
        ]
    
    def check_setup(self) -> bool:
        """检查智能体设置状态"""
        print("🔍 正在检查智能体设置...")
        
        # 检查Ollama连接
        if not self.ollama_client.check_connection():
            print("❌ Ollama服务连接失败")
            return False
        print("✅ Ollama服务连接正常")
        
        # 检查模型
        if not self.ollama_client.check_model_exists():
            print("⚠️  模型不存在，正在下载...")
            if not self.ollama_client.pull_model():
                print("❌ 模型下载失败")
                return False
        print("✅ 模型准备就绪")
        
        return True
    
    def generate_complete_post(self, request: ContentRequest) -> Dict[str, Any]:
        """生成完整的小红书文案"""
        
        # 构建详细的需求描述
        requirement = f"""
请为以下需求生成完整的小红书文案：

分类：{request.category.value}
主题：{request.topic}
语气风格：{request.tone}
长度：{request.length}
目标受众：{request.target_audience}
"""
        
        if request.keywords:
            requirement += f"关键词：{', '.join(request.keywords)}\n"
        
        if request.special_requirements:
            requirement += f"特殊要求：{request.special_requirements}\n"
        
        requirement += "\n请分别生成标题、正文内容和话题标签。"
        
        try:
            # 使用智能体生成内容
            result = self.agent.run(requirement)
            
            return {
                "success": True,
                "content": result,
                "request": request.__dict__
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "request": request.__dict__
            }
    
    def optimize_content(self, content: str) -> Dict[str, Any]:
        """优化现有内容"""
        try:
            optimization_query = f"请优化以下小红书文案：\n\n{content}"
            result = self.agent.run(optimization_query)
            
            return {
                "success": True,
                "original": content,
                "optimized": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "original": content
            }
    
    def chat(self, message: str) -> str:
        """与智能体对话"""
        try:
            response = self.agent.run(message)
            return response
        except Exception as e:
            return f"对话出错：{str(e)}"
    
    def update_config(self, enable_stream: bool = None, enable_thinking: bool = None):
        """更新配置"""
        if enable_stream is not None:
            self.enable_stream = enable_stream
            self.llm.enable_stream = enable_stream
        
        if enable_thinking is not None:
            self.enable_thinking = enable_thinking
            self.llm.enable_thinking = enable_thinking
    


    def generate_complete_post_stream(self, request: ContentRequest):
        """流式生成完整的小红书文案"""
        
        # 构建详细的需求描述
        requirement = f"""
请为以下需求生成完整的小红书文案：

分类：{request.category.value}
主题：{request.topic}
语气风格：{request.tone}
长度：{request.length}
目标受众：{request.target_audience}
"""
        
        if request.keywords:
            requirement += f"关键词：{', '.join(request.keywords)}\n"
        
        if request.special_requirements:
            requirement += f"特殊要求：{request.special_requirements}\n"
        
        requirement += "\n请分别生成标题、正文内容和话题标签。"
        
        # 处理思考模式
        if not self.enable_thinking:
            requirement += "/no_think"
        
        # 使用流式生成器
        return self.ollama_client.generate_stream(requirement)
    
    def chat_stream(self, message: str):
        """流式对话"""
        try:
            # 构建对话消息
            messages = [{"role": "user", "content": message}]
            
            # 如果有对话历史，添加到消息中
            chat_history = self.memory.chat_memory.messages
            if chat_history:
                # 转换LangChain消息格式到Ollama格式
                for msg in chat_history[-10:]:  # 只保留最近10条消息
                    if hasattr(msg, 'content'):
                        if isinstance(msg, HumanMessage):
                            messages.insert(-1, {"role": "user", "content": msg.content})
                        elif isinstance(msg, AIMessage):
                            messages.insert(-1, {"role": "assistant", "content": msg.content})
            
            # 使用流式生成器
            return self.ollama_client.chat_stream(messages)
        except Exception as e:
            def error_generator():
                yield f"对话出错：{str(e)}"
            return error_generator()
    
    def optimize_content_stream(self, content: str):
        """流式优化现有内容"""
        optimization_query = f"请优化以下小红书文案：\n\n{content}"
        
        # 处理思考模式
        if not self.enable_thinking:
            optimization_query += "/no_think"
        
        # 使用流式生成器
        return self.ollama_client.generate_stream(optimization_query)

    def intelligent_loop(self, content: str, user_feedback: str, content_request: ContentRequest = None):
        """智能体回环处理
        
        Args:
            content: 当前生成的内容
            user_feedback: 用户反馈 ("不满意", "满意", "需要优化", "重新生成")
            content_request: 原始内容请求，用于重新生成
            
        Returns:
            Dict: 处理结果
        """
        try:
            if user_feedback == "不满意" or user_feedback == "重新生成":
                # 用户不满意，重新生成内容
                if content_request:
                    return self.regenerate_with_improvements(content_request, content)
                else:
                    # 如果没有原始请求，尝试从内容中推断并重新生成
                    return self.regenerate_from_content(content)
                    
            elif user_feedback == "满意":
                # 用户满意，询问是否需要优化
                return {
                    "success": True,
                    "action": "ask_optimization",
                    "message": "很高兴您满意这个文案！是否需要我进一步优化内容？",
                    "options": ["需要优化", "不需要优化，已完成"]
                }
                
            elif user_feedback == "需要优化":
                # 用户需要优化，执行智能优化
                return self.optimize_content(content)
                
            elif user_feedback == "不需要优化，已完成":
                # 用户完全满意，结束流程
                return {
                    "success": True,
                    "action": "completed",
                    "message": "创作完成！如需要新的文案，请开始新的创作流程。",
                    "final_content": content
                }
                
            else:
                # 未知反馈，提供帮助
                return {
                    "success": False,
                    "error": "未识别的反馈类型",
                    "message": "请选择：不满意、满意、需要优化 或 不需要优化，已完成"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "处理过程中出现错误，请重试"
            }
    
    def regenerate_with_improvements(self, request: ContentRequest, previous_content: str):
        """基于用户不满意重新生成改进版本"""
        try:
            # 分析之前的内容并生成改进提示
            improvement_prompt = f"""
基于以下需求重新生成小红书文案，需要避免之前内容的不足：

原始需求：
- 分类：{request.category.value}
- 主题：{request.topic}
- 语气风格：{request.tone}
- 长度：{request.length}
- 目标受众：{request.target_audience}

之前生成的内容：
{previous_content}

请重新创作，要求：
1. 保持主题和基本要求不变
2. 换一个全新的角度和表达方式
3. 增加更多吸引力和创意
4. 确保内容质量更高
5. 带emoji、分段清晰
"""
            
            if request.keywords:
                improvement_prompt += f"- 关键词：{', '.join(request.keywords)}\n"
            
            if request.special_requirements:
                improvement_prompt += f"- 特殊要求：{request.special_requirements}\n"
            
            # 处理思考模式
            if not self.enable_thinking:
                improvement_prompt += "/no_think"
            
            result = self.ollama_client.generate(improvement_prompt, stream=self.enable_stream)
            
            return {
                "success": True,
                "action": "regenerated",
                "content": result,
                "message": "已重新生成改进版本，请查看是否满意"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "error"
            }
    
    def regenerate_from_content(self, content: str):
        """从现有内容推断需求并重新生成"""
        try:
            regeneration_prompt = f"""
请分析以下小红书文案，然后生成一个全新的改进版本：

现有内容：
{content}

要求：
1. 保持相同的主题和目标
2. 完全重新创作，不要重复现有表达
3. 提升内容的吸引力和质量
4. 保持小红书平台特色
5. 带emoji、分段清晰

请生成全新的改进版本。
"""
            
            # 处理思考模式
            if not self.enable_thinking:
                regeneration_prompt += "/no_think"
            
            result = self.ollama_client.generate(regeneration_prompt, stream=self.enable_stream)
            
            return {
                "success": True,
                "action": "regenerated", 
                "content": result,
                "message": "已基于原内容重新生成改进版本"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "error"
            }
    
    def intelligent_loop_stream(self, content: str, user_feedback: str, content_request: ContentRequest = None):
        """流式智能体回环处理"""
        try:
            if user_feedback == "不满意" or user_feedback == "重新生成":
                # 重新生成流式版本
                if content_request:
                    return self.regenerate_with_improvements_stream(content_request, content)
                else:
                    return self.regenerate_from_content_stream(content)
                    
            elif user_feedback == "需要优化":
                # 流式优化
                return self.optimize_content_stream(content)
                
            else:
                # 对于其他情况，返回简单的生成器
                def simple_response():
                    if user_feedback == "满意":
                        yield "很高兴您满意这个文案！是否需要我进一步优化内容？"
                    elif user_feedback == "不需要优化，已完成":
                        yield "创作完成！如需要新的文案，请开始新的创作流程。"
                    else:
                        yield "请选择：不满意、满意、需要优化 或 不需要优化，已完成"
                
                return simple_response()
                
        except Exception as e:
            def error_response():
                yield f"处理过程中出现错误：{str(e)}"
            return error_response()
    
    def regenerate_with_improvements_stream(self, request: ContentRequest, previous_content: str):
        """流式重新生成改进版本"""
        improvement_prompt = f"""
基于以下需求重新生成小红书文案，需要避免之前内容的不足：

原始需求：
- 分类：{request.category.value}
- 主题：{request.topic}
- 语气风格：{request.tone}
- 长度：{request.length}
- 目标受众：{request.target_audience}

之前生成的内容：
{previous_content}

请重新创作，要求：
1. 保持主题和基本要求不变
2. 换一个全新的角度和表达方式
3. 增加更多吸引力和创意
4. 确保内容质量更高
5. 带emoji、分段清晰
"""
        
        if request.keywords:
            improvement_prompt += f"- 关键词：{', '.join(request.keywords)}\n"
        
        if request.special_requirements:
            improvement_prompt += f"- 特殊要求：{request.special_requirements}\n"
        
        # 处理思考模式
        if not self.enable_thinking:
            improvement_prompt += "/no_think"
        
        return self.ollama_client.generate_stream(improvement_prompt)
    
    def regenerate_from_content_stream(self, content: str):
        """流式从现有内容重新生成"""
        regeneration_prompt = f"""
请分析以下小红书文案，然后生成一个全新的改进版本：

现有内容：
{content}

要求：
1. 保持相同的主题和目标
2. 完全重新创作，不要重复现有表达
3. 提升内容的吸引力和质量
4. 保持小红书平台特色
5. 带emoji、分段清晰

请生成全新的改进版本。
"""
        
        # 处理思考模式
        if not self.enable_thinking:
            regeneration_prompt += "/no_think"
        
        return self.ollama_client.generate_stream(regeneration_prompt)


def main():
    """演示智能体使用"""
    print("🎉 小红书文案生成智能体启动中...")
    
    # 配置选择
    print("🔧 配置选项：")
    stream_choice = input("是否启用流式响应？(y/n，默认y): ").lower()
    enable_stream = stream_choice != 'n'
    
    thinking_choice = input("是否启用思考模式？(y/n，默认y): ").lower()
    enable_thinking = thinking_choice != 'n'
    
    print(f"✅ 配置：流式响应={enable_stream}, 思考模式={enable_thinking}")
    
    # 创建智能体
    agent = XiaohongshuAgent(enable_stream=enable_stream, enable_thinking=enable_thinking)
    
    # 检查设置
    if not agent.check_setup():
        print("❌ 智能体设置失败，请检查Ollama服务")
        return
    
    print("✅ 智能体准备就绪！")
    print("=" * 50)
    
    # 示例：生成美妆内容
    print("📝 示例：生成美妆护肤内容")
    request = ContentRequest(
        category=ContentCategory.BEAUTY,
        topic="冬季护肤保湿攻略",
        tone="专业温和",
        keywords=["保湿", "冬季", "护肤"],
        target_audience="20-30岁女性"
    )
    
    result = agent.generate_complete_post(request)
    
    if result["success"]:
        print("生成结果：")
        print(result["content"])
    else:
        print(f"生成失败：{result['error']}")
    
    print("=" * 50)
    print("💬 您可以继续与智能体对话，输入'quit'退出")
    
    # 交互模式
    while True:
        try:
            user_input = input("\n您：")
            if user_input.lower() in ['quit', 'exit', '退出']:
                break
            
            response = agent.chat(user_input)
            print(f"\n智能体：{response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 感谢使用小红书文案生成智能体！")
            break


if __name__ == "__main__":
    main() 