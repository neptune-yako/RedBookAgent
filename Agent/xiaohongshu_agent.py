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
from .i18n_agent import (
    Language, 
    get_prompt_template, 
    format_keywords_section, 
    format_special_requirements_section
)

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
    language: str = "zh-CN"  # 新增语言参数


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
            # 从查询中提取语言信息，如果没有则使用默认语言
            language = Language.ZH_CN
            if "|language:" in query:
                query_parts = query.split("|language:")
                if len(query_parts) > 1:
                    lang_code = query_parts[1].strip()
                    try:
                        language = Language(lang_code)
                        query = query_parts[0].strip()
                    except ValueError:
                        pass
            
            prompt_template = get_prompt_template("title_generation", language)
            prompt = prompt_template.format(query=query)
            
            # 处理思考模式
            if not self.enable_thinking:
                prompt += "/no_think"
            
            return self.ollama_client.generate(prompt, stream=self.enable_stream) or "生成失败"
        
        def generate_content_tool(query: str) -> str:
            """生成小红书正文内容的工具"""
            # 从查询中提取语言信息
            language = Language.ZH_CN
            if "|language:" in query:
                query_parts = query.split("|language:")
                if len(query_parts) > 1:
                    lang_code = query_parts[1].strip()
                    try:
                        language = Language(lang_code)
                        query = query_parts[0].strip()
                    except ValueError:
                        pass
            
            prompt_template = get_prompt_template("content_writing", language)
            prompt = prompt_template.format(query=query)
            
            # 处理思考模式
            if not self.enable_thinking:
                prompt += "/no_think"
            
            return self.ollama_client.generate(prompt, stream=self.enable_stream) or "生成失败"
        
        def generate_hashtags_tool(query: str) -> str:
            """生成小红书话题标签的工具"""
            # 从查询中提取语言信息
            language = Language.ZH_CN
            if "|language:" in query:
                query_parts = query.split("|language:")
                if len(query_parts) > 1:
                    lang_code = query_parts[1].strip()
                    try:
                        language = Language(lang_code)
                        query = query_parts[0].strip()
                    except ValueError:
                        pass
            
            prompt_template = get_prompt_template("hashtag_generation", language)
            prompt = prompt_template.format(query=query)
            
            # 处理思考模式
            if not self.enable_thinking:
                prompt += "/no_think"
            
            return self.ollama_client.generate(prompt, stream=self.enable_stream) or "生成失败"
        
        def content_optimization_tool(query: str) -> str:
            """内容优化建议工具"""
            # 从查询中提取语言信息
            language = Language.ZH_CN
            if "|language:" in query:
                query_parts = query.split("|language:")
                if len(query_parts) > 1:
                    lang_code = query_parts[1].strip()
                    try:
                        language = Language(lang_code)
                        query = query_parts[0].strip()
                    except ValueError:
                        pass
            
            prompt_template = get_prompt_template("content_optimization", language)
            prompt = prompt_template.format(content=query)
            
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
        
        try:
            # 获取语言参数
            language = Language(request.language) if hasattr(request, 'language') and request.language else Language.ZH_CN
        except ValueError:
            language = Language.ZH_CN
        
        # 使用国际化模板构建需求描述
        prompt_template = get_prompt_template("content_generation", language)
        
        # 格式化关键词和特殊要求
        keywords_section = format_keywords_section(request.keywords, language)
        special_requirements_section = format_special_requirements_section(request.special_requirements, language)
        
        requirement = prompt_template.format(
            category=request.category.value,
            topic=request.topic,
            tone=request.tone,
            length=request.length,
            target_audience=request.target_audience,
            keywords_section=keywords_section,
            special_requirements_section=special_requirements_section
        )
        
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
    
    def optimize_content(self, content: str, language: str = "zh-CN") -> Dict[str, Any]:
        """优化现有内容"""
        try:
            # 获取语言参数
            try:
                lang = Language(language)
            except ValueError:
                lang = Language.ZH_CN
            
            # 使用国际化模板
            prompt_template = get_prompt_template("content_optimization", lang)
            optimization_query = prompt_template.format(content=content)
            
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
    
    def chat(self, message: str, language: str = "zh-CN") -> str:
        """与智能体对话"""
        try:
            # 为聊天消息添加语言上下文
            try:
                lang = Language(language)
            except ValueError:
                lang = Language.ZH_CN
            
            # 根据语言添加对话上下文
            if lang == Language.EN_US:
                contextualized_message = f"Please respond in English. User message: {message}"
            elif lang == Language.ZH_TW:
                contextualized_message = f"請用繁體中文回答。用戶訊息：{message}"
            elif lang == Language.JA_JP:
                contextualized_message = f"日本語で回答してください。ユーザーメッセージ：{message}"
            else:
                contextualized_message = f"请用简体中文回答。用户消息：{message}"
            
            response = self.agent.run(contextualized_message)
            return response
        except Exception as e:
            # 根据语言返回错误消息
            error_messages = {
                Language.ZH_CN: f"对话出错：{str(e)}",
                Language.EN_US: f"Chat error: {str(e)}",
                Language.ZH_TW: f"對話出錯：{str(e)}",
                Language.JA_JP: f"チャットエラー：{str(e)}"
            }
            try:
                lang = Language(language)
                return error_messages.get(lang, error_messages[Language.ZH_CN])
            except ValueError:
                return error_messages[Language.ZH_CN]
    
    def update_config(self, enable_stream: bool = None, enable_thinking: bool = None):
        """更新配置"""
        if enable_stream is not None:
            self.enable_stream = enable_stream
            self.llm.enable_stream = enable_stream
        
        if enable_thinking is not None:
            self.enable_thinking = enable_thinking
            self.llm.enable_thinking = enable_thinking
    
    def generate_complete_post_stream(self, request: ContentRequest, enable_thinking: bool = None):
        """流式生成完整的小红书文案"""
        
        try:
            # 获取语言参数
            language = Language(request.language) if hasattr(request, 'language') and request.language else Language.ZH_CN
        except ValueError:
            language = Language.ZH_CN
        
        # 使用国际化模板构建需求描述
        prompt_template = get_prompt_template("content_generation", language)
        
        # 格式化关键词和特殊要求
        keywords_section = format_keywords_section(request.keywords, language)
        special_requirements_section = format_special_requirements_section(request.special_requirements, language)
        
        requirement = prompt_template.format(
            category=request.category.value,
            topic=request.topic,
            tone=request.tone,
            length=request.length,
            target_audience=request.target_audience,
            keywords_section=keywords_section,
            special_requirements_section=special_requirements_section
        )
        
        # 处理思考模式 - 优先使用参数，否则使用实例设置
        thinking_enabled = enable_thinking if enable_thinking is not None else self.enable_thinking
        if not thinking_enabled:
            requirement += "/no_think"
        
        # 使用流式生成器
        return self.ollama_client.generate_stream(requirement)

    def chat_stream(self, message: str, language: str = "zh-CN", enable_thinking: bool = None):
        """流式对话"""
        try:
            # 为聊天消息添加语言上下文
            try:
                lang = Language(language)
            except ValueError:
                lang = Language.ZH_CN
            
            # 根据语言添加对话上下文
            if lang == Language.EN_US:
                contextualized_message = f"Please respond in English. User message: {message}"
            elif lang == Language.ZH_TW:
                contextualized_message = f"請用繁體中文回答。用戶訊息：{message}"
            elif lang == Language.JA_JP:
                contextualized_message = f"日本語で回答してください。ユーザーメッセージ：{message}"
            else:
                contextualized_message = f"请用简体中文回答。用户消息：{message}"
            
            # 处理思考模式 - 优先使用参数，否则使用实例设置
            thinking_enabled = enable_thinking if enable_thinking is not None else self.enable_thinking
            if not thinking_enabled and not contextualized_message.endswith("/no_think"):
                contextualized_message += "/no_think"
            
            # 构建对话消息
            messages = [{"role": "user", "content": contextualized_message}]
            
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
                # 根据语言返回错误消息
                error_messages = {
                    Language.ZH_CN: f"对话出错：{str(e)}",
                    Language.EN_US: f"Chat error: {str(e)}",
                    Language.ZH_TW: f"對話出錯：{str(e)}",
                    Language.JA_JP: f"チャットエラー：{str(e)}"
                }
                try:
                    lang = Language(language)
                    yield error_messages.get(lang, error_messages[Language.ZH_CN])
                except ValueError:
                    yield error_messages[Language.ZH_CN]
            return error_generator()

    def optimize_content_stream(self, content: str, language: str = "zh-CN", enable_thinking: bool = None):
        """流式优化现有内容"""
        try:
            # 获取语言参数
            lang = Language(language)
        except ValueError:
            lang = Language.ZH_CN
        
        # 使用国际化模板
        prompt_template = get_prompt_template("content_optimization", lang)
        optimization_query = prompt_template.format(content=content)
        
        # 处理思考模式 - 优先使用参数，否则使用实例设置
        thinking_enabled = enable_thinking if enable_thinking is not None else self.enable_thinking
        if not thinking_enabled:
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
            # 获取语言参数
            try:
                language = Language(request.language) if hasattr(request, 'language') and request.language else Language.ZH_CN
            except ValueError:
                language = Language.ZH_CN
            
            # 使用国际化模板
            prompt_template = get_prompt_template("regeneration_with_improvements", language)
            
            # 格式化关键词和特殊要求
            keywords_section = format_keywords_section(request.keywords, language)
            special_requirements_section = format_special_requirements_section(request.special_requirements, language)
            
            improvement_prompt = prompt_template.format(
                category=request.category.value,
                topic=request.topic,
                tone=request.tone,
                length=request.length,
                target_audience=request.target_audience,
                keywords_section=keywords_section,
                special_requirements_section=special_requirements_section,
                previous_content=previous_content
            )
            
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
    
    def regenerate_from_content(self, content: str, language: str = "zh-CN"):
        """从现有内容推断需求并重新生成"""
        try:
            # 获取语言参数
            try:
                lang = Language(language)
            except ValueError:
                lang = Language.ZH_CN
            
            # 使用国际化模板
            prompt_template = get_prompt_template("regeneration_from_content", lang)
            regeneration_prompt = prompt_template.format(content=content)
            
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
        # 获取语言参数
        try:
            language = Language(request.language) if hasattr(request, 'language') and request.language else Language.ZH_CN
        except ValueError:
            language = Language.ZH_CN
        
        # 使用国际化模板
        prompt_template = get_prompt_template("regeneration_with_improvements", language)
        
        # 格式化关键词和特殊要求
        keywords_section = format_keywords_section(request.keywords, language)
        special_requirements_section = format_special_requirements_section(request.special_requirements, language)
        
        improvement_prompt = prompt_template.format(
            category=request.category.value,
            topic=request.topic,
            tone=request.tone,
            length=request.length,
            target_audience=request.target_audience,
            keywords_section=keywords_section,
            special_requirements_section=special_requirements_section,
            previous_content=previous_content
        )
        
        # 处理思考模式
        if not self.enable_thinking:
            improvement_prompt += "/no_think"
        
        return self.ollama_client.generate_stream(improvement_prompt)
    
    def regenerate_from_content_stream(self, content: str, language: str = "zh-CN"):
        """流式从现有内容重新生成"""
        # 获取语言参数
        try:
            lang = Language(language)
        except ValueError:
            lang = Language.ZH_CN
        
        # 使用国际化模板
        prompt_template = get_prompt_template("regeneration_from_content", lang)
        regeneration_prompt = prompt_template.format(content=content)
        
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