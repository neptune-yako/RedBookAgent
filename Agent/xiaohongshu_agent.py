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
    format_special_requirements_section,
    translate_category
)

from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from pydantic import Field, ConfigDict


def get_language_instruction(language: Language) -> str:
    """根据语言类型生成对应的语言指令"""
    language_instructions = {
        Language.ZH_CN: "请用简体中文回答",
        Language.EN_US: "IMPORTANT: You must respond ONLY in English. Do not use any Chinese characters. Write content in English language for English-speaking audience",
        Language.ZH_TW: "請用繁體中文回答，不要使用簡體字", 
        Language.JA_JP: "重要：必ず日本語で回答してください。中国語は使用しないでください"
    }
    return language_instructions.get(language, language_instructions[Language.ZH_CN])


def add_language_instruction_to_prompt(prompt: str, language: Language) -> str:
    """为prompt添加语言指令"""
    language_instruction = get_language_instruction(language)
    if language == Language.EN_US:
        # 对英语添加更强的指令
        return f"{language_instruction}\n\nIMPORTANT: Your entire response must be in English. This includes the title, content, and hashtags.\n\n{prompt}\n\nRemember: Write EVERYTHING in English language."
    elif language == Language.JA_JP:
        # 对日语添加更强的指令
        return f"{language_instruction}\n\n重要：回答の全てを日本語で書いてください。\n\n{prompt}\n\n注意：タイトル、内容、ハッシュタグすべて日本語で書いてください。"
    elif language == Language.ZH_TW:
        # 对繁体中文添加更强的指令
        return f"{language_instruction}\n\n重要：請使用繁體中文，不要使用簡體字。\n\n{prompt}\n\n記住：標題、內容、標籤都要用繁體中文。"
    else:
        return f"{language_instruction}。\n\n{prompt}"


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
    TECH = "科技数码"
    EMOTION = "情感生活"
    CAREER = "职场发展"
    EDUCATION = "教育学习"


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
            language = Language.ZH_CN  # 默认语言
            if "|language:" in query:
                query_parts = query.split("|language:")
                if len(query_parts) > 1:
                    # 处理语言代码，可能包含其他内容
                    lang_part = query_parts[1]
                    # 提取语言代码（取第一个|之前的部分）
                    if "|" in lang_part:
                        lang_code = lang_part.split("|")[0].strip()
                    else:
                        lang_code = lang_part.strip()
                    try:
                        language = Language(lang_code)
                        # 重新构建查询，去掉语言标记
                        query = query_parts[0].strip()
                        if len(query_parts) > 1 and "|" in query_parts[1]:
                            remaining_parts = "|".join(query_parts[1].split("|")[1:])
                            if remaining_parts.strip():
                                query += "|" + remaining_parts
                    except ValueError:
                        language = Language.ZH_CN  # 解析失败时使用默认语言
            
            prompt_template = get_prompt_template("title_generation", language)
            prompt = prompt_template.format(query=query)
            
            # 添加语言指令
            prompt = add_language_instruction_to_prompt(prompt, language)
            
            # 处理思考模式
            if not self.enable_thinking:
                prompt += "/no_think"
            
            return self.ollama_client.generate(prompt, stream=self.enable_stream) or "生成失败"
        
        def generate_content_tool(query: str) -> str:
            """生成小红书正文内容的工具"""
            # 从查询中提取语言信息
            language = Language.ZH_CN  # 默认语言
            if "|language:" in query:
                query_parts = query.split("|language:")
                if len(query_parts) > 1:
                    # 处理语言代码，可能包含其他内容
                    lang_part = query_parts[1]
                    # 提取语言代码（取第一个|之前的部分）
                    if "|" in lang_part:
                        lang_code = lang_part.split("|")[0].strip()
                    else:
                        lang_code = lang_part.strip()
                    try:
                        language = Language(lang_code)
                        # 重新构建查询，去掉语言标记
                        query = query_parts[0].strip()
                        if len(query_parts) > 1 and "|" in query_parts[1]:
                            remaining_parts = "|".join(query_parts[1].split("|")[1:])
                            if remaining_parts.strip():
                                query += "|" + remaining_parts
                    except ValueError:
                        language = Language.ZH_CN  # 解析失败时使用默认语言
            
            prompt_template = get_prompt_template("content_writing", language)
            prompt = prompt_template.format(query=query)
            
            # 添加语言指令
            prompt = add_language_instruction_to_prompt(prompt, language)
            
            # 处理思考模式
            if not self.enable_thinking:
                prompt += "/no_think"
            
            return self.ollama_client.generate(prompt, stream=self.enable_stream) or "生成失败"
        
        def generate_hashtags_tool(query: str) -> str:
            """生成小红书话题标签的工具"""
            # 从查询中提取语言信息
            language = Language.ZH_CN  # 默认语言
            if "|language:" in query:
                query_parts = query.split("|language:")
                if len(query_parts) > 1:
                    # 处理语言代码，可能包含其他内容
                    lang_part = query_parts[1]
                    # 提取语言代码（取第一个|之前的部分）
                    if "|" in lang_part:
                        lang_code = lang_part.split("|")[0].strip()
                    else:
                        lang_code = lang_part.strip()
                    try:
                        language = Language(lang_code)
                        # 重新构建查询，去掉语言标记
                        query = query_parts[0].strip()
                        if len(query_parts) > 1 and "|" in query_parts[1]:
                            remaining_parts = "|".join(query_parts[1].split("|")[1:])
                            if remaining_parts.strip():
                                query += "|" + remaining_parts
                    except ValueError:
                        language = Language.ZH_CN  # 解析失败时使用默认语言
            
            prompt_template = get_prompt_template("hashtag_generation", language)
            prompt = prompt_template.format(query=query)
            
            # 添加语言指令
            prompt = add_language_instruction_to_prompt(prompt, language)
            
            # 处理思考模式
            if not self.enable_thinking:
                prompt += "/no_think"
            
            return self.ollama_client.generate(prompt, stream=self.enable_stream) or "生成失败"
        
        def content_optimization_tool(query: str) -> str:
            """内容优化建议工具"""
            # 从查询中提取语言信息
            language = Language.ZH_CN  # 默认语言
            if "|language:" in query:
                query_parts = query.split("|language:")
                if len(query_parts) > 1:
                    # 处理语言代码，可能包含其他内容
                    lang_part = query_parts[1]
                    # 提取语言代码（取第一个|之前的部分）
                    if "|" in lang_part:
                        lang_code = lang_part.split("|")[0].strip()
                    else:
                        lang_code = lang_part.strip()
                    try:
                        language = Language(lang_code)
                        # 重新构建查询，去掉语言标记
                        query = query_parts[0].strip()
                        if len(query_parts) > 1 and "|" in query_parts[1]:
                            remaining_parts = "|".join(query_parts[1].split("|")[1:])
                            if remaining_parts.strip():
                                query += "|" + remaining_parts
                    except ValueError:
                        language = Language.ZH_CN  # 解析失败时使用默认语言
            
            prompt_template = get_prompt_template("content_optimization", language)
            prompt = prompt_template.format(content=query)
            
            # 添加语言指令
            prompt = add_language_instruction_to_prompt(prompt, language)
            
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
        
        # 翻译分类到目标语言
        translated_category = translate_category(request.category.value, language)
        
        requirement = prompt_template.format(
            category=translated_category,
            topic=request.topic,
            tone=request.tone,
            length=request.length,
            target_audience=request.target_audience,
            keywords_section=keywords_section,
            special_requirements_section=special_requirements_section
        )
        
        # 添加语言指令和语言标记
        requirement = add_language_instruction_to_prompt(requirement, language)
        requirement = f"|language:{request.language}|{requirement}"
        
        try:
            # 处理思考模式
            if not self.enable_thinking:
                requirement += "/no_think"
            
            # 直接使用 Ollama 客户端生成内容，避免 LangChain Agent 的中文干扰
            result = self.ollama_client.generate(requirement, stream=self.enable_stream)
            
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
            
            # 添加语言指令
            optimization_query = add_language_instruction_to_prompt(optimization_query, lang)
            
            # 处理思考模式
            if not self.enable_thinking:
                optimization_query += "/no_think"
            
            # 直接使用 Ollama 客户端，避免 LangChain Agent 的中文干扰
            result = self.ollama_client.generate(optimization_query, stream=self.enable_stream)
            
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
            
            # 使用标准化的语言指令，并将语言信息附加到消息中
            language_instruction = get_language_instruction(lang)
            contextualized_message = f"{language_instruction}。|language:{language}|用户消息：{message}"
            
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
        
        # 翻译分类到目标语言
        translated_category = translate_category(request.category.value, language)
        
        requirement = prompt_template.format(
            category=translated_category,
            topic=request.topic,
            tone=request.tone,
            length=request.length,
            target_audience=request.target_audience,
            keywords_section=keywords_section,
            special_requirements_section=special_requirements_section
        )
        
        # 添加语言指令
        requirement = add_language_instruction_to_prompt(requirement, language)
        
        # 处理思考模式 - 优先使用参数，否则使用实例设置
        thinking_enabled = enable_thinking if enable_thinking is not None else self.enable_thinking
        if not thinking_enabled:
            requirement += "/no_think"
        
        # 准备系统级语言提示
        system_prompt = None
        if language == Language.EN_US:
            system_prompt = "You are a professional content creator for Xiaohongshu (Little Red Book). You must respond ONLY in English. Never use Chinese characters in your response."
        elif language == Language.JA_JP:
            system_prompt = "あなたは小紅書（シャオホンシュー）のプロのコンテンツクリエイターです。必ず日本語のみで回答してください。中国語は決して使用しないでください。"
        elif language == Language.ZH_TW:
            system_prompt = "您是小紅書的專業內容創作者。請使用繁體中文回答，不要使用簡體字。"
        
        # 使用流式生成器，传递系统提示
        return self.ollama_client.generate_stream(requirement, system_prompt)

    def chat_stream(self, message: str, language: str = "zh-CN", enable_thinking: bool = None):
        """流式对话"""
        try:
            # 为聊天消息添加语言上下文
            try:
                lang = Language(language)
            except ValueError:
                lang = Language.ZH_CN
            
            # 使用标准化的语言指令，并将语言信息附加到消息中
            language_instruction = get_language_instruction(lang)
            contextualized_message = f"{language_instruction}。|language:{language}|用户消息：{message}"
            
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
        
        # 添加语言指令
        optimization_query = add_language_instruction_to_prompt(optimization_query, lang)
        
        # 处理思考模式 - 优先使用参数，否则使用实例设置
        thinking_enabled = enable_thinking if enable_thinking is not None else self.enable_thinking
        if not thinking_enabled:
            optimization_query += "/no_think"
        
        # 准备系统级语言提示
        system_prompt = None
        if lang == Language.EN_US:
            system_prompt = "You are a professional content optimizer for Xiaohongshu (Little Red Book). You must respond ONLY in English. Never use Chinese characters in your response."
        elif lang == Language.JA_JP:
            system_prompt = "あなたは小紅書（シャオホンシュー）のプロのコンテンツ最適化専門家です。必ず日本語のみで回答してください。中国語は決して使用しないでください。"
        elif lang == Language.ZH_TW:
            system_prompt = "您是小紅書の專業內容優化專家。請使用繁體中文回答，不要使用簡體字。"
        
        # 使用流式生成器，传递系统提示
        return self.ollama_client.generate_stream(optimization_query, system_prompt)

    def intelligent_loop(self, content: str, user_feedback: str, content_request: ContentRequest = None, language: str = "zh-CN"):
        """智能体回环处理
        
        Args:
            content: 当前生成的内容
            user_feedback: 用户反馈 ("不满意", "满意", "需要优化", "重新生成")
            content_request: 原始内容请求，用于重新生成
            language: 回复语言，默认简体中文
            
        Returns:
            Dict: 处理结果
        """
        # 获取语言参数
        try:
            lang = Language(language)
        except ValueError:
            lang = Language.ZH_CN
        
        # 定义多语言消息
        messages = {
            Language.ZH_CN: {
                "satisfied_ask": "很高兴您满意这个文案！是否需要我进一步优化内容？",
                "completed": "创作完成！如需要新的文案，请开始新的创作流程。",
                "unknown_feedback": "请选择：不满意、满意、需要优化 或 不需要优化，已完成",
                "error_occurred": "处理过程中出现错误，请重试",
                "options": ["需要优化", "不需要优化，已完成"]
            },
            Language.EN_US: {
                "satisfied_ask": "Glad you're satisfied with this content! Would you like me to further optimize it?",
                "completed": "Creation completed! Start a new creation process if you need new content.",
                "unknown_feedback": "Please choose: Not satisfied, Satisfied, Need optimization, or No optimization needed, completed",
                "error_occurred": "An error occurred during processing, please try again",
                "options": ["Need optimization", "No optimization needed, completed"]
            },
            Language.ZH_TW: {
                "satisfied_ask": "很高興您滿意這個文案！是否需要我進一步優化內容？",
                "completed": "創作完成！如需要新的文案，請開始新的創作流程。",
                "unknown_feedback": "請選擇：不滿意、滿意、需要優化 或 不需要優化，已完成",
                "error_occurred": "處理過程中出現錯誤，請重試",
                "options": ["需要優化", "不需要優化，已完成"]
            },
            Language.JA_JP: {
                "satisfied_ask": "このコンテンツに満足していただけて嬉しいです！さらに最適化しますか？",
                "completed": "作成完了！新しいコンテンツが必要な場合は、新しい作成プロセスを開始してください。",
                "unknown_feedback": "選択してください：不満、満足、最適化が必要、または最適化不要、完了",
                "error_occurred": "処理中にエラーが発生しました。もう一度お試しください",
                "options": ["最適化が必要", "最適化不要、完了"]
            }
        }
        
        try:
            if user_feedback == "不满意" or user_feedback == "重新生成":
                # 用户不满意，重新生成内容
                if content_request:
                    return self.regenerate_with_improvements(content_request, content)
                else:
                    # 如果没有原始请求，尝试从内容中推断并重新生成
                    return self.regenerate_from_content(content, language)
                    
            elif user_feedback == "满意":
                # 用户满意，询问是否需要优化
                return {
                    "success": True,
                    "action": "ask_optimization",
                    "message": messages[lang]["satisfied_ask"],
                    "options": messages[lang]["options"]
                }
                
            elif user_feedback == "需要优化":
                # 用户需要优化，执行智能优化
                return self.optimize_content(content, language)
                
            elif user_feedback == "不需要优化，已完成":
                # 用户完全满意，结束流程
                return {
                    "success": True,
                    "action": "completed",
                    "message": messages[lang]["completed"],
                    "final_content": content
                }
                
            else:
                # 未知反馈，提供帮助
                return {
                    "success": False,
                    "error": "未识别的反馈类型",
                    "message": messages[lang]["unknown_feedback"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": messages[lang]["error_occurred"]
            }
    
    def regenerate_with_improvements(self, request: ContentRequest, previous_content: str):
        """基于用户不满意重新生成改进版本"""
        try:
            # 获取语言参数
            try:
                language = Language(request.language) if hasattr(request, 'language') and request.language else Language.ZH_CN
            except ValueError:
                language = Language.ZH_CN
            
            # 定义多语言消息
            messages = {
                Language.ZH_CN: "已重新生成改进版本，请查看是否满意",
                Language.EN_US: "Regenerated improved version, please check if you're satisfied",
                Language.ZH_TW: "已重新生成改進版本，請查看是否滿意",
                Language.JA_JP: "改良版を再生成しました。満足いただけるかご確認ください"
            }
            
            # 使用国际化模板
            prompt_template = get_prompt_template("regeneration_with_improvements", language)
            
            # 格式化关键词和特殊要求
            keywords_section = format_keywords_section(request.keywords, language)
            special_requirements_section = format_special_requirements_section(request.special_requirements, language)
            
            # 翻译分类到目标语言
            translated_category = translate_category(request.category.value, language)
            
            improvement_prompt = prompt_template.format(
                category=translated_category,
                topic=request.topic,
                tone=request.tone,
                length=request.length,
                target_audience=request.target_audience,
                keywords_section=keywords_section,
                special_requirements_section=special_requirements_section,
                previous_content=previous_content
            )
            
            # 添加语言指令
            improvement_prompt = add_language_instruction_to_prompt(improvement_prompt, language)
            
            # 处理思考模式
            if not self.enable_thinking:
                improvement_prompt += "/no_think"
            
            result = self.ollama_client.generate(improvement_prompt, stream=self.enable_stream)
            
            return {
                "success": True,
                "action": "regenerated",
                "content": result,
                "message": messages[language]
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
            
            # 定义多语言消息
            messages = {
                Language.ZH_CN: "已基于原内容重新生成改进版本",
                Language.EN_US: "Regenerated improved version based on original content",
                Language.ZH_TW: "已基於原內容重新生成改進版本",
                Language.JA_JP: "元のコンテンツに基づいて改良版を再生成しました"
            }
            
            # 使用国际化模板
            prompt_template = get_prompt_template("regeneration_from_content", lang)
            regeneration_prompt = prompt_template.format(content=content)
            
            # 添加语言指令
            regeneration_prompt = add_language_instruction_to_prompt(regeneration_prompt, lang)
            
            # 处理思考模式
            if not self.enable_thinking:
                regeneration_prompt += "/no_think"
            
            result = self.ollama_client.generate(regeneration_prompt, stream=self.enable_stream)
            
            return {
                "success": True,
                "action": "regenerated", 
                "content": result,
                "message": messages[lang]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "error"
            }
    
    def intelligent_loop_stream(self, content: str, user_feedback: str, content_request: ContentRequest = None, language: str = "zh-CN"):
        """流式智能体回环处理"""
        # 获取语言参数
        try:
            lang = Language(language)
        except ValueError:
            lang = Language.ZH_CN
        
        # 定义多语言消息
        messages = {
            Language.ZH_CN: {
                "satisfied": "很高兴您满意这个文案！是否需要我进一步优化内容？",
                "completed": "创作完成！如需要新的文案，请开始新的创作流程。",
                "unknown": "请选择：不满意、满意、需要优化 或 不需要优化，已完成",
                "error": "处理过程中出现错误："
            },
            Language.EN_US: {
                "satisfied": "Glad you're satisfied with this content! Would you like me to further optimize it?",
                "completed": "Creation completed! Start a new creation process if you need new content.",
                "unknown": "Please choose: Not satisfied, Satisfied, Need optimization, or No optimization needed, completed",
                "error": "An error occurred during processing: "
            },
            Language.ZH_TW: {
                "satisfied": "很高興您滿意這個文案！是否需要我進一步優化內容？",
                "completed": "創作完成！如需要新的文案，請開始新的創作流程。",
                "unknown": "請選擇：不滿意、滿意、需要優化 或 不需要優化，已完成",
                "error": "處理過程中出現錯誤："
            },
            Language.JA_JP: {
                "satisfied": "このコンテンツに満足していただけて嬉しいです！さらに最適化しますか？",
                "completed": "作成完了！新しいコンテンツが必要な場合は、新しい作成プロセスを開始してください。",
                "unknown": "選択してください：不満、満足、最適化が必要、または最適化不要、完了",
                "error": "処理中にエラーが発生しました："
            }
        }
        
        try:
            if user_feedback == "不满意" or user_feedback == "重新生成":
                # 重新生成流式版本
                if content_request:
                    return self.regenerate_with_improvements_stream(content_request, content)
                else:
                    return self.regenerate_from_content_stream(content, language)
                    
            elif user_feedback == "需要优化":
                # 流式优化
                return self.optimize_content_stream(content, language)
                
            else:
                # 对于其他情况，返回简单的生成器
                def simple_response():
                    if user_feedback == "满意":
                        yield messages[lang]["satisfied"]
                    elif user_feedback == "不需要优化，已完成":
                        yield messages[lang]["completed"]
                    else:
                        yield messages[lang]["unknown"]
                
                return simple_response()
                
        except Exception as e:
            def error_response():
                yield f"{messages[lang]['error']}{str(e)}"
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
        
        # 翻译分类到目标语言
        translated_category = translate_category(request.category.value, language)
        
        improvement_prompt = prompt_template.format(
            category=translated_category,
            topic=request.topic,
            tone=request.tone,
            length=request.length,
            target_audience=request.target_audience,
            keywords_section=keywords_section,
            special_requirements_section=special_requirements_section,
            previous_content=previous_content
        )
        
        # 添加语言指令
        improvement_prompt = add_language_instruction_to_prompt(improvement_prompt, language)
        
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
        
        # 添加语言指令
        regeneration_prompt = add_language_instruction_to_prompt(regeneration_prompt, lang)
        
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