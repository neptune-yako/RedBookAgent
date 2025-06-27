"""
数据模型定义
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
try:
    from typing import Union
except ImportError:
    from typing_extensions import Union
from pydantic import BaseModel, Field, ConfigDict

from .i18n import I18nMixin, Language


class ContentGenerationRequest(I18nMixin):
    category: str = Field(
        ..., 
        description="内容分类",
        example="美食探店"
    )
    topic: str = Field(
        ..., 
        description="主题内容",
        example="新开的日式料理店体验"
    )
    tone: str = Field(
        default="活泼可爱", 
        description="""语调风格 - 控制生成文案的语言风格和表达方式
        可选值：
        • 活泼可爱 - 年轻化、emoji丰富、互动性强（如：姐妹们！这家店绝了！😍）
        • 温馨治愈 - 温暖、舒缓、情感丰富（如：在忙碌生活中找到温暖角落...）
        • 专业详细 - 客观、专业、信息量大（如：经实地体验，该餐厅表现优异）
        • 幽默搞笑 - 轻松、有趣、调侃式（如：本吃货又被套路了😂）
        • 简洁明了 - 直接、简练、要点突出（如：新店推荐，值得一试）""",
        example="活泼可爱"
    )
    length: str = Field(
        default="中等", 
        description="""内容长度 - 控制生成文案的篇幅
        可选值：
        • 短 - 100-200字，适合朋友圈分享、简单推荐
        • 中等 - 200-500字，适合标准小红书笔记，详略得当
        • 长 - 500-800字，适合深度测评、攻略分享，内容详尽""",
        example="中等"
    )
    keywords: Optional[List[str]] = Field(
        default=None, 
        description="关键词列表 - 希望在文案中重点体现的词汇",
        example=["日式料理", "新店", "美味", "性价比"]
    )
    target_audience: str = Field(
        default="年轻女性", 
        description="""目标受众 - 影响语言风格、关注点和内容重点
        常见选项：
        • 年轻女性 (18-30岁) - 关注颜值、性价比、拍照效果，语言活泼感性
        • 职场白领 (25-40岁) - 关注效率、品质、便利性，语言理性简洁
        • 学生群体 (16-25岁) - 关注性价比、潮流、实用性，语言年轻化
        • 宝妈群体 (25-45岁) - 关注安全性、实用性、家庭适用，语言温馨实用
        • 美食爱好者 - 专注美食体验，注重口味描述和专业评价
        • 时尚达人 - 关注潮流趋势，语言前卫时髦""",
        example="年轻女性"
    )
    special_requirements: str = Field(
        default="", 
        description="""特殊要求 - 用于精细化控制生成内容的额外需求
        常见要求示例：
        • "要有个人体验感" - 增加第一人称体验描述，如"我觉得"、"亲测"
        • "突出性价比" - 强调价格优势，对比同类产品
        • "适合拍照打卡" - 突出视觉效果、环境美观度
        • "包含使用教程" - 添加详细的操作步骤和使用方法
        • "强调安全性" - 突出产品的安全特点和保障
        • "注重环保理念" - 强调可持续发展、环保材料
        • "适合送礼" - 突出礼品属性、包装精美
        • "制造紧迫感" - 如限时优惠、数量有限等""",
        example="要有个人体验感，适合拍照打卡"
    )
    user_id: str = Field(
        ..., 
        description="用户ID - 用于会话管理和内容历史记录",
        example="user_001"
    )
    enable_thinking: bool = Field(
        default=True,
        description="""思考模式开关 - 控制AI是否显示思考过程
        • True - 启用思考模式，显示AI的思考和推理过程
        • False - 关闭思考模式，直接输出结果，会在prompt后添加'/no_think'""",
        example=True
    )


class ContentOptimizationRequest(I18nMixin):
    content: str = Field(..., description="待优化的内容")
    user_id: str = Field(..., description="用户ID")
    enable_thinking: bool = Field(
        default=True,
        description="""思考模式开关 - 控制AI是否显示思考过程
        • True - 启用思考模式，显示AI的思考和推理过程
        • False - 关闭思考模式，直接输出结果，会在prompt后添加'/no_think'""",
        example=True
    )


class ChatRequest(I18nMixin):
    message: str = Field(..., description="用户消息")
    user_id: str = Field(..., description="用户ID")
    enable_thinking: bool = Field(
        default=True,
        description="""思考模式开关 - 控制AI是否显示思考过程
        • True - 启用思考模式，显示AI的思考和推理过程
        • False - 关闭思考模式，直接输出结果，会在prompt后添加'/no_think'""",
        example=True
    )


class FeedbackRequest(I18nMixin):
    content: str = Field(
        ..., 
        description="当前内容 - 需要处理的文案内容",
        example="今天去了一家新开的日式料理店，味道不错，环境也很好。"
    )
    feedback: str = Field(
        ..., 
        description="""用户反馈类型
        可选值：
        • "不满意" - 完全重新生成新的文案
        • "满意" - 在当前基础上进行优化
        • "需要优化" - 保持主体内容，进行细节优化
        • "完全满意" - 结束处理流程""",
        example="需要优化"
    )
    user_id: str = Field(
        ..., 
        description="用户ID - 用于会话管理和内容历史记录",
        example="user_001"
    )
    original_request: Optional[ContentGenerationRequest] = Field(
        default=None, 
        description="原始请求 - 用于重新生成时参考原始参数（tone、length、target_audience等）"
    )


class VersionRestoreRequest(I18nMixin):
    user_id: str = Field(..., description="用户ID")
    version_index: int = Field(..., description="版本索引")


class SSEConnectionRequest(I18nMixin):
    user_id: str = Field(..., description="用户ID")
    connection_type: str = Field(default="general", description="连接类型")


class ApiResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(), description="响应时间") 