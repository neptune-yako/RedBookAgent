"""
小红书文案生成智能体 - 国际化支持模块
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass


class Language(str, Enum):
    """支持的语言枚举"""
    ZH_CN = "zh-CN"  # 简体中文
    EN_US = "en-US"  # 英语（美国）
    ZH_TW = "zh-TW"  # 繁体中文
    JA_JP = "ja-JP"  # 日语


# 多语言提示词模板
PROMPT_TEMPLATES: Dict[Language, Dict[str, str]] = {
    Language.ZH_CN: {
        "content_generation": """
请为以下需求生成完整的小红书文案：

分类：{category}
主题：{topic}
语气风格：{tone}
长度：{length}
目标受众：{target_audience}
{keywords_section}
{special_requirements_section}

请分别生成标题、正文内容和话题标签。

要求：
1. 标题要有吸引力和话题性，适当使用emoji表情
2. 正文要有价值和实用性，带emoji、分段清晰
3. 结尾要有互动引导
4. 话题标签要符合小红书规范
5. 整体风格要符合小红书调性
""",
        
        "content_optimization": """
请优化以下小红书文案，让它更加吸引人和有效：

原文案：
{content}

请从以下角度进行优化：
1. 提升标题吸引力
2. 改善内容结构和可读性
3. 优化用词表达
4. 增强互动性
5. 完善话题标签

请提供优化后的完整文案。
""",
        
        "title_generation": """
作为小红书爆款标题专家，请为以下内容生成3个吸引人的标题：

内容描述：{query}

要求：
1. 标题要有吸引力和话题性
2. 适当使用emoji表情
3. 长度控制在15-25字
4. 符合小红书用户习惯
5. 每个标题风格要有差异

请生成3个标题，用序号分别标注。
""",
        
        "content_writing": """
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
""",
        
        "hashtag_generation": """
作为小红书话题标签专家，请为以下内容生成相关的话题标签：

内容：{query}

要求：
1. 生成8-12个相关话题标签
2. 包含热门标签和精准标签
3. 标签要符合小红书规范
4. 用#号标注每个标签
5. 按照热度和相关性排序

请生成话题标签列表。
""",
        
        "regeneration_with_improvements": """
用户对之前的文案不满意，请根据原始需求重新生成一个更好的版本：

原始需求：
分类：{category}
主题：{topic}
语气风格：{tone}
长度：{length}
目标受众：{target_audience}
{keywords_section}
{special_requirements_section}

之前的文案：
{previous_content}

请生成一个全新的、更优质的文案版本，避免重复之前的内容和表达方式。
""",
        
        "regeneration_from_content": """
用户对以下文案不满意，请重新生成一个更好的版本：

原文案：
{content}

请分析原文案的主题和风格，生成一个全新的、更优质的文案版本。
要求：
1. 保持相同的主题方向
2. 改进表达方式和结构
3. 增强吸引力和互动性
4. 避免重复原文案的表达
"""
    },
    
    Language.EN_US: {
        "content_generation": """
Please generate complete Xiaohongshu (Little Red Book) content for the following requirements:

Category: {category}
Topic: {topic}
Tone: {tone}
Length: {length}
Target Audience: {target_audience}
{keywords_section}
{special_requirements_section}

Please generate title, main content, and hashtags separately.

Requirements:
1. Title should be attractive and topical, with appropriate emoji usage
2. Content should be valuable and practical, with emojis and clear paragraphs
3. Ending should encourage interaction
4. Hashtags should comply with Xiaohongshu standards
5. Overall style should match Xiaohongshu tone
""",
        
        "content_optimization": """
Please optimize the following Xiaohongshu content to make it more attractive and effective:

Original Content:
{content}

Please optimize from these aspects:
1. Enhance title attractiveness
2. Improve content structure and readability
3. Optimize word choice and expression
4. Strengthen interactivity
5. Perfect hashtags

Please provide the complete optimized content.
""",
        
        "title_generation": """
As a Xiaohongshu viral title expert, please generate 3 attractive titles for the following content:

Content Description: {query}

Requirements:
1. Titles should be attractive and topical
2. Appropriate emoji usage
3. Length control within 15-25 characters
4. Match Xiaohongshu user habits
5. Each title should have different style

Please generate 3 titles with numbered labels.
""",
        
        "content_writing": """
As a Xiaohongshu content creation expert, please generate complete Xiaohongshu content for the following requirements:

Requirements: {query}

Requirements:
1. Opening should have an attractive hook
2. Content should be valuable and practical
3. Include emojis and clear paragraphs
4. Ending should encourage interaction
5. Overall style should match Xiaohongshu tone
6. Word count should be 200-500 words

Please generate complete Xiaohongshu content.
""",
        
        "hashtag_generation": """
As a Xiaohongshu hashtag expert, please generate relevant hashtags for the following content:

Content: {query}

Requirements:
1. Generate 8-12 relevant hashtags
2. Include both popular and precise tags
3. Tags should comply with Xiaohongshu standards
4. Mark each tag with # symbol
5. Sort by popularity and relevance

Please generate hashtag list.
""",
        
        "regeneration_with_improvements": """
The user is not satisfied with the previous content. Please regenerate a better version based on the original requirements:

Original Requirements:
Category: {category}
Topic: {topic}
Tone: {tone}
Length: {length}
Target Audience: {target_audience}
{keywords_section}
{special_requirements_section}

Previous Content:
{previous_content}

Please generate a brand new, higher quality content version, avoiding repetition of previous content and expressions.
""",
        
        "regeneration_from_content": """
The user is not satisfied with the following content. Please regenerate a better version:

Original Content:
{content}

Please analyze the theme and style of the original content and generate a brand new, higher quality content version.
Requirements:
1. Maintain the same thematic direction
2. Improve expression and structure
3. Enhance attractiveness and interactivity
4. Avoid repeating original expressions
"""
    },
    
    Language.ZH_TW: {
        "content_generation": """
請為以下需求生成完整的小紅書文案：

分類：{category}
主題：{topic}
語氣風格：{tone}
長度：{length}
目標受眾：{target_audience}
{keywords_section}
{special_requirements_section}

請分別生成標題、正文內容和話題標籤。

要求：
1. 標題要有吸引力和話題性，適當使用emoji表情
2. 正文要有價值和實用性，帶emoji、分段清晰
3. 結尾要有互動引導
4. 話題標籤要符合小紅書規範
5. 整體風格要符合小紅書調性
""",
        
        "content_optimization": """
請優化以下小紅書文案，讓它更加吸引人和有效：

原文案：
{content}

請從以下角度進行優化：
1. 提升標題吸引力
2. 改善內容結構和可讀性
3. 優化用詞表達
4. 增強互動性
5. 完善話題標籤

請提供優化後的完整文案。
""",
        
        "title_generation": """
作為小紅書爆款標題專家，請為以下內容生成3個吸引人的標題：

內容描述：{query}

要求：
1. 標題要有吸引力和話題性
2. 適當使用emoji表情
3. 長度控制在15-25字
4. 符合小紅書用戶習慣
5. 每個標題風格要有差異

請生成3個標題，用序號分別標註。
""",
        
        "content_writing": """
作為小紅書內容創作專家，請為以下需求生成完整的小紅書文案：

需求：{query}

要求：
1. 開頭要有吸引人的hook
2. 內容要有價值和實用性
3. 帶emoji、分段清晰
4. 結尾要有互動引導
5. 整體風格要符合小紅書調性
6. 字數控制在200-500字

請生成完整的小紅書文案。
""",
        
        "hashtag_generation": """
作為小紅書話題標籤專家，請為以下內容生成相關的話題標籤：

內容：{query}

要求：
1. 生成8-12個相關話題標籤
2. 包含熱門標籤和精準標籤
3. 標籤要符合小紅書規範
4. 用#號標註每個標籤
5. 按照熱度和相關性排序

請生成話題標籤列表。
""",
        
        "regeneration_with_improvements": """
用戶對之前的文案不滿意，請根據原始需求重新生成一個更好的版本：

原始需求：
分類：{category}
主題：{topic}
語氣風格：{tone}
長度：{length}
目標受眾：{target_audience}
{keywords_section}
{special_requirements_section}

之前的文案：
{previous_content}

請生成一個全新的、更優質的文案版本，避免重複之前的內容和表達方式。
""",
        
        "regeneration_from_content": """
用戶對以下文案不滿意，請重新生成一個更好的版本：

原文案：
{content}

請分析原文案的主題和風格，生成一個全新的、更優質的文案版本。
要求：
1. 保持相同的主題方向
2. 改進表達方式和結構
3. 增強吸引力和互動性
4. 避免重複原文案的表達
"""
    },
    
    Language.JA_JP: {
        "content_generation": """
以下の要件に基づいて、完全なXiaohongshu（小紅書）コンテンツを生成してください：

カテゴリ: {category}
トピック: {topic}
トーン: {tone}
長さ: {length}
ターゲット層: {target_audience}
{keywords_section}
{special_requirements_section}

タイトル、メインコンテンツ、ハッシュタグを別々に生成してください。

要件：
1. タイトルは魅力的で話題性があり、適切な絵文字を使用する
2. コンテンツは価値があり実用的で、絵文字と明確な段落がある
3. 終わりにはインタラクションを促す
4. ハッシュタグはXiaohongshuの基準に準拠する
5. 全体的なスタイルはXiaohongshuのトーンに合わせる
""",
        
        "content_optimization": """
以下のXiaohongshuコンテンツを最適化して、より魅力的で効果的にしてください：

元のコンテンツ:
{content}

以下の観点から最適化してください：
1. タイトルの魅力を向上
2. コンテンツ構造と読みやすさの改善
3. 言葉選びと表現の最適化
4. インタラクティブ性の強化
5. ハッシュタグの完成

最適化された完全なコンテンツを提供してください。
""",
        
        "title_generation": """
Xiaohongshuバイラルタイトル専門家として、以下のコンテンツに対して魅力的なタイトルを3つ生成してください：

コンテンツ説明: {query}

要件：
1. タイトルは魅力的で話題性がある
2. 適切な絵文字の使用
3. 15-25文字以内の長さ制御
4. Xiaohongshuユーザーの習慣に合わせる
5. 各タイトルは異なるスタイルを持つ

番号付きラベルで3つのタイトルを生成してください。
""",
        
        "content_writing": """
Xiaohongshuコンテンツ制作専門家として、以下の要件に対して完全なXiaohongshuコンテンツを生成してください：

要件: {query}

要件：
1. 開始は魅力的なフックを持つ
2. コンテンツは価値があり実用的である
3. 絵文字と明確な段落を含む
4. 終わりにはインタラクションを促す
5. 全体的なスタイルはXiaohongshuのトーンに合わせる
6. 文字数は200-500文字

完全なXiaohongshuコンテンツを生成してください。
""",
        
        "hashtag_generation": """
Xiaohongshuハッシュタグ専門家として、以下のコンテンツに関連するハッシュタグを生成してください：

コンテンツ: {query}

要件：
1. 8-12個の関連ハッシュタグを生成
2. 人気タグと精密タグの両方を含む
3. タグはXiaohongshuの基準に準拠する
4. 各タグに#記号を付ける
5. 人気度と関連性で並べ替える

ハッシュタグリストを生成してください。
""",
        
        "regeneration_with_improvements": """
ユーザーは以前のコンテンツに満足していません。元の要件に基づいて、より良いバージョンを再生成してください：

元の要件：
カテゴリ: {category}
トピック: {topic}
トーン: {tone}
長さ: {length}
ターゲット層: {target_audience}
{keywords_section}
{special_requirements_section}

以前のコンテンツ:
{previous_content}

以前のコンテンツと表現の重複を避けて、まったく新しい、より高品質なコンテンツバージョンを生成してください。
""",
        
        "regeneration_from_content": """
ユーザーは以下のコンテンツに満足していません。より良いバージョンを再生成してください：

元のコンテンツ:
{content}

元のコンテンツのテーマとスタイルを分析し、まったく新しい、より高品質なコンテンツバージョンを生成してください。
要件：
1. 同じテーマ方向を維持
2. 表現と構造を改善
3. 魅力とインタラクティブ性を向上
4. 元の表現の重複を避ける
"""
    }
}


def get_prompt_template(template_key: str, language: Language = Language.ZH_CN) -> str:
    """
    获取指定语言的提示词模板
    
    Args:
        template_key: 模板键
        language: 目标语言
    
    Returns:
        提示词模板字符串
    """
    return PROMPT_TEMPLATES.get(language, PROMPT_TEMPLATES[Language.ZH_CN]).get(
        template_key, 
        PROMPT_TEMPLATES[Language.ZH_CN].get(template_key, template_key)
    )


def format_keywords_section(keywords: Optional[list], language: Language = Language.ZH_CN) -> str:
    """格式化关键词部分"""
    if not keywords:
        return ""
    
    labels = {
        Language.ZH_CN: "关键词：",
        Language.EN_US: "Keywords: ",
        Language.ZH_TW: "關鍵詞：",
        Language.JA_JP: "キーワード: "
    }
    
    label = labels.get(language, labels[Language.ZH_CN])
    return f"{label}{', '.join(keywords)}"


def format_special_requirements_section(special_requirements: str, language: Language = Language.ZH_CN) -> str:
    """格式化特殊要求部分"""
    if not special_requirements:
        return ""
    
    labels = {
        Language.ZH_CN: "特殊要求：",
        Language.EN_US: "Special Requirements: ",
        Language.ZH_TW: "特殊要求：",
        Language.JA_JP: "特別要件: "
    }
    
    label = labels.get(language, labels[Language.ZH_CN])
    return f"{label}{special_requirements}"


# 导出主要功能
__all__ = [
    "Language",
    "PROMPT_TEMPLATES", 
    "get_prompt_template",
    "format_keywords_section",
    "format_special_requirements_section"
] 