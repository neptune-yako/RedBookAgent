"""
小红书内容模板库 - 增强版国际化支持
包含各种类型的文案模板和提示词，支持多语言
"""

from typing import Dict, List
from enum import Enum


class TemplateType(Enum):
    """模板类型"""
    TITLE = "标题模板"
    CONTENT = "内容模板"
    HASHTAG = "话题标签模板"
    OPENING = "开头模板"
    ENDING = "结尾模板"


class Language(str, Enum):
    """支持的语言枚举"""
    ZH_CN = "zh-CN"  # 简体中文
    EN_US = "en-US"  # 英语（美国）
    ZH_TW = "zh-TW"  # 繁体中文
    JA_JP = "ja-JP"  # 日语


class XiaohongshuTemplates:
    """小红书文案模板库 - 国际化版本"""
    
    # 多语言标题模板
    TITLE_TEMPLATES = {
        Language.ZH_CN: {
            "美妆护肤": [
                "{产品名}真的绝绝子！{效果}太惊喜了💕",
                "姐妹们！这个{产品类型}我要吹爆🔥{效果}",
                "{时间}用{产品名}，{效果}到哭😭",
                "买它买它！{产品名}{效果}真的太香了✨",
                "平价{产品类型}天花板！{效果}不输大牌💰"
            ],
            "时尚穿搭": [
                "{风格}穿搭公式！{场合}这样穿超{效果}✨",
                "{身材}女孩的{季节}穿搭攻略👗{效果}",
                "{价位}{单品}搭配指南！{效果}到飞起🔥",
                "{风格}风穿搭模板！照着穿就很{效果}💕",
                "{单品}的{数量}种穿法！{效果}又{效果2}👌"
            ],
            "美食探店": [
                "{地点}这家{餐厅类型}绝了！{特色}太{评价}😋",
                "终于找到{口味}{餐厅类型}！{特色}爱了爱了💕",
                "{地点}宝藏{餐厅类型}！{特色}{价位}真香🔥",
                "姐妹们冲！{餐厅名}{特色}yyds✨",
                "{节日}必去！{地点}{餐厅类型}{特色}绝绝子🎉"
            ]
        },
        
        Language.EN_US: {
            "美妆护肤": [
                "{Product_Name} is absolutely amazing! {Effect} is so surprising💕",
                "Girls! I have to rave about this {Product_Type}🔥{Effect}",
                "Used {Product_Name} for {Time}, {Effect} made me cry😭",
                "Buy it buy it! {Product_Name} {Effect} is really worth it✨",
                "Budget {Product_Type} champion! {Effect} rivals luxury brands💰"
            ],
            "时尚穿搭": [
                "{Style} outfit formula! Dress like this for {Occasion} super {Effect}✨",
                "{Body_Type} girls' {Season} outfit guide👗{Effect}",
                "{Price_Range} {Item} styling guide! {Effect} to the max🔥",
                "{Style} style outfit template! Just copy and you'll look {Effect}💕",
                "{Item} in {Number} ways! {Effect} and {Effect2}👌"
            ],
            "美食探店": [
                "This {Restaurant_Type} in {Location} is incredible! {Specialty} is so {Rating}😋",
                "Finally found this {Flavor} {Restaurant_Type}! {Specialty} love it💕",
                "Hidden gem {Restaurant_Type} in {Location}! {Specialty} {Price} so worth it🔥",
                "Girls let's go! {Restaurant_Name} {Specialty} is the best✨",
                "Must-visit for {Holiday}! {Location} {Restaurant_Type} {Specialty} is amazing🎉"
            ]
        },
        
        Language.ZH_TW: {
            "美妝護膚": [
                "{產品名}真的絕絕子！{效果}太驚喜了💕",
                "姐妹們！這個{產品類型}我要吹爆🔥{效果}",
                "{時間}用{產品名}，{效果}到哭😭",
                "買它買它！{產品名}{效果}真的太香了✨",
                "平價{產品類型}天花板！{效果}不輸大牌💰"
            ],
            "時尚穿搭": [
                "{風格}穿搭公式！{場合}這樣穿超{效果}✨",
                "{身材}女孩的{季節}穿搭攻略👗{效果}",
                "{價位}{單品}搭配指南！{效果}到飛起🔥",
                "{風格}風穿搭模板！照著穿就很{效果}💕",
                "{單品}的{數量}種穿法！{效果}又{效果2}👌"
            ],
            "美食探店": [
                "{地點}這家{餐廳類型}絕了！{特色}太{評價}😋",
                "終於找到{口味}{餐廳類型}！{特色}愛了愛了💕",
                "{地點}寶藏{餐廳類型}！{特色}{價位}真香🔥",
                "姐妹們衝！{餐廳名}{特色}yyds✨",
                "{節日}必去！{地點}{餐廳類型}{特色}絕絕子🎉"
            ]
        },
        
        Language.JA_JP: {
            "美容スキンケア": [
                "{製品名}本当にすごい！{効果}がとても驚きです💕",
                "みんな！この{製品タイプ}を絶対おすすめします🔥{効果}",
                "{時間}使った{製品名}、{効果}で感動😭",
                "絶対買って！{製品名}の{効果}は本当に素晴らしい✨",
                "プチプラ{製品タイプ}の王者！{効果}は高級ブランドに負けない💰"
            ],
            "ファッションコーデ": [
                "{スタイル}コーデの公式！{場面}でこう着れば超{効果}✨",
                "{体型}の女の子の{季節}コーデ攻略👗{効果}",
                "{価格帯}{アイテム}スタイリングガイド！{効果}が最高🔥",
                "{スタイル}風コーデテンプレート！真似するだけで{効果}💕",
                "{アイテム}の{数}通りの着方！{効果}で{効果2}👌"
            ],
            "グルメ探訪": [
                "{場所}のこの{レストランタイプ}最高！{特色}がとても{評価}😋",
                "やっと見つけた{味}{レストランタイプ}！{特色}大好き💕",
                "{場所}の隠れた{レストランタイプ}！{特色}{価格}で最高🔥",
                "みんな行こう！{レストラン名}の{特色}が最高✨",
                "{祝日}は絶対！{場所}の{レストランタイプ}{特色}が素晴らしい🎉"
            ]
        }
    }
    
    # 多语言开头模板
    OPENING_TEMPLATES = {
        Language.ZH_CN: {
            "惊喜发现": [
                "姐妹们！我发现了一个宝藏{类型}💎",
                "真的是意外惊喜！没想到{产品/地点}{效果}",
                "今天要来分享一个超级惊喜的发现✨",
                "不得不说，这次真的是捡到宝了🎯"
            ],
            "问题解决": [
                "还在为{问题}烦恼吗？这个方法绝了🔥",
                "终于解决了困扰我很久的{问题}💪",
                "姐妹们是不是都有{问题}的困扰？",
                "如果你也有{问题}，一定要试试这个方法👇"
            ]
        },
        
        Language.EN_US: {
            "Amazing Discovery": [
                "Girls! I discovered an amazing {Type}💎",
                "What a pleasant surprise! Didn't expect {Product/Place} to {Effect}",
                "Today I want to share an incredible discovery✨",
                "I have to say, this is really a great find🎯"
            ],
            "Problem Solving": [
                "Still worried about {Problem}? This method is amazing🔥",
                "Finally solved the {Problem} that's been bothering me💪",
                "Do you girls also have {Problem} troubles?",
                "If you also have {Problem}, you must try this method👇"
            ]
        },
        
        Language.ZH_TW: {
            "驚喜發現": [
                "姐妹們！我發現了一個寶藏{類型}💎",
                "真的是意外驚喜！沒想到{產品/地點}{效果}",
                "今天要來分享一個超級驚喜的發現✨",
                "不得不說，這次真的是撿到寶了🎯"
            ],
            "問題解決": [
                "還在為{問題}煩惱嗎？這個方法絕了🔥",
                "終於解決了困擾我很久的{問題}💪",
                "姐妹們是不是都有{問題}的困擾？",
                "如果妳也有{問題}，一定要試試這個方法👇"
            ]
        },
        
        Language.JA_JP: {
            "素晴らしい発見": [
                "みんな！素晴らしい{タイプ}を発見しました💎",
                "本当に嬉しい驚き！{製品/場所}が{効果}とは思わなかった",
                "今日は素晴らしい発見をシェアしたいと思います✨",
                "本当に良いものを見つけました🎯"
            ],
            "問題解決": [
                "{問題}でお悩みですか？この方法は最高です🔥",
                "長い間悩んでいた{問題}をやっと解決しました💪",
                "みんなも{問題}で困ってませんか？",
                "{問題}がある方は、ぜひこの方法を試してみて👇"
            ]
        }
    }
    
    # 多语言结尾模板
    ENDING_TEMPLATES = {
        Language.ZH_CN: {
            "互动引导": [
                "你们还有什么想知道的？评论区聊聊💬",
                "有没有姐妹和我一样{感受}的？举个手🙋‍♀️",
                "还有什么{主题}好物推荐吗？分享一下✨",
                "你们觉得怎么样？快来评论区告诉我👇"
            ],
            "行动呼吁": [
                "心动不如行动！赶紧去试试吧🏃‍♀️",
                "还不快去{行动}！晚了就没了⏰",
                "建议收藏起来慢慢看，很实用哦📌",
                "记得点赞关注哦，后续更新更多{内容}💕"
            ]
        },
        
        Language.EN_US: {
            "Interactive Guidance": [
                "What else do you want to know? Let's chat in the comments💬",
                "Are there any girls who feel the same {Feeling} as me? Raise your hand🙋‍♀️",
                "Any other {Topic} recommendations? Please share✨",
                "What do you think? Tell me in the comments👇"
            ],
            "Call to Action": [
                "Better to act than just think! Go try it now🏃‍♀️",
                "Hurry up and {Action}! It'll be gone if you're late⏰",
                "Suggest saving this for later reading, very useful📌",
                "Remember to like and follow for more {Content} updates💕"
            ]
        },
        
        Language.ZH_TW: {
            "互動引導": [
                "妳們還有什麼想知道的？評論區聊聊💬",
                "有沒有姐妹和我一樣{感受}的？舉個手🙋‍♀️",
                "還有什麼{主題}好物推薦嗎？分享一下✨",
                "妳們覺得怎麼樣？快來評論區告訴我👇"
            ],
            "行動呼籲": [
                "心動不如行動！趕緊去試試吧🏃‍♀️",
                "還不快去{行動}！晚了就沒了⏰",
                "建議收藏起來慢慢看，很實用哦📌",
                "記得點贊關注哦，後續更新更多{內容}💕"
            ]
        },
        
        Language.JA_JP: {
            "インタラクション促進": [
                "他に知りたいことはありますか？コメント欄で話しましょう💬",
                "私と同じ{感情}の人はいますか？手を上げて🙋‍♀️",
                "他にも{テーマ}のおすすめはありますか？シェアしてください✨",
                "どう思いますか？コメント欄で教えてください👇"
            ],
            "行動促進": [
                "思い立ったら即行動！早速試してみましょう🏃‍♀️",
                "早く{行動}しないと！遅れると無くなりますよ⏰",
                "保存してゆっくり読むことをおすすめします、とても実用的です📌",
                "いいねとフォローをお忘れなく、もっと{コンテンツ}を更新します💕"
            ]
        }
    }
    
    # 多语言话题标签模板
    HASHTAG_TEMPLATES = {
        Language.ZH_CN: {
            "美妆护肤": [
                "#护肤日记", "#美妆分享", "#种草笔记", "#护肤心得",
                "#美妆评测", "#化妆技巧", "#护肤品推荐", "#美妆好物",
                "#彩妆教程", "#护肤攻略", "#美妆博主", "#化妆品测评"
            ],
            "时尚穿搭": [
                "#穿搭分享", "#今日穿搭", "#穿搭攻略", "#时尚穿搭",
                "#穿搭日记", "#outfit", "#搭配技巧", "#穿搭博主",
                "#时尚博主", "#穿搭灵感", "#服装搭配", "#穿搭模板"
            ],
            "美食探店": [
                "#美食探店", "#美食分享", "#探店笔记", "#美食推荐",
                "#餐厅推荐", "#美食博主", "#吃播", "#美食攻略",
                "#探店日记", "#美食种草", "#餐厅测评", "#美食vlog"
            ]
        },
        
        Language.EN_US: {
            "Beauty & Skincare": [
                "#SkincareRoutine", "#BeautyShare", "#ProductReview", "#SkincareJourney",
                "#MakeupReview", "#BeautyTips", "#SkincareRecommendations", "#BeautyFinds",
                "#MakeupTutorial", "#SkincareGuide", "#BeautyBlogger", "#CosmeticReview"
            ],
            "Fashion & Style": [
                "#OOTD", "#StyleShare", "#FashionTips", "#StyleInspo",
                "#FashionDiary", "#OutfitIdeas", "#StyleGuide", "#Fashionista",
                "#StyleBlogger", "#FashionLook", "#WardrobeEssentials", "#StyleTemplate"
            ],
            "Food & Dining": [
                "#FoodieFinds", "#RestaurantReview", "#FoodShare", "#FoodRecommendations",
                "#DiningOut", "#FoodBlogger", "#FoodLover", "#FoodGuide",
                "#FoodDiary", "#MustTry", "#RestaurantGuide", "#FoodVlog"
            ]
        },
        
        Language.ZH_TW: {
            "美妝護膚": [
                "#護膚日記", "#美妝分享", "#種草筆記", "#護膚心得",
                "#美妝評測", "#化妝技巧", "#護膚品推薦", "#美妝好物",
                "#彩妝教程", "#護膚攻略", "#美妝博主", "#化妝品測評"
            ],
            "時尚穿搭": [
                "#穿搭分享", "#今日穿搭", "#穿搭攻略", "#時尚穿搭",
                "#穿搭日記", "#outfit", "#搭配技巧", "#穿搭博主",
                "#時尚博主", "#穿搭靈感", "#服裝搭配", "#穿搭模板"
            ],
            "美食探店": [
                "#美食探店", "#美食分享", "#探店筆記", "#美食推薦",
                "#餐廳推薦", "#美食博主", "#吃播", "#美食攻略",
                "#探店日記", "#美食種草", "#餐廳測評", "#美食vlog"
            ]
        },
        
        Language.JA_JP: {
            "美容・スキンケア": [
                "#スキンケア日記", "#美容シェア", "#コスメレビュー", "#スキンケア体験",
                "#メイクレビュー", "#美容テクニック", "#スキンケアおすすめ", "#美容アイテム",
                "#メイクチュートリアル", "#スキンケア攻略", "#美容ブロガー", "#コスメ評価"
            ],
            "ファッション・コーデ": [
                "#コーデシェア", "#今日のコーデ", "#ファッション攻略", "#コーデ術",
                "#ファッション日記", "#outfit", "#スタイリング", "#ファッションブロガー",
                "#おしゃれ", "#コーデアイデア", "#ファッションコーデ", "#スタイル"
            ],
            "グルメ・レストラン": [
                "#グルメ探訪", "#美食シェア", "#レストランレビュー", "#グルメおすすめ",
                "#お店紹介", "#グルメブロガー", "#食べ歩き", "#グルメガイド",
                "#食事記録", "#グルメ発見", "#レストラン評価", "#グルメvlog"
            ]
        }
    }
    
    @classmethod
    def get_templates_by_category(cls, category: str, language: Language = Language.ZH_CN) -> Dict[str, List[str]]:
        """根据分类和语言获取模板"""
        return {
            "titles": cls.TITLE_TEMPLATES.get(language, {}).get(category, []),
            "openings": cls.OPENING_TEMPLATES.get(language, {}).get("惊喜发现", []),
            "endings": cls.ENDING_TEMPLATES.get(language, {}).get("互动引导", []),
            "hashtags": cls.HASHTAG_TEMPLATES.get(language, {}).get(category, [])
        }
    
    @classmethod
    def get_random_template(cls, template_type: TemplateType, category: str = None, language: Language = Language.ZH_CN) -> str:
        """随机获取模板"""
        import random
        
        if template_type == TemplateType.TITLE and category:
            templates = cls.TITLE_TEMPLATES.get(language, {}).get(category, [])
        elif template_type == TemplateType.OPENING:
            templates = cls.OPENING_TEMPLATES.get(language, {}).get("惊喜发现", [])
        elif template_type == TemplateType.ENDING:
            templates = cls.ENDING_TEMPLATES.get(language, {}).get("互动引导", [])
        elif template_type == TemplateType.HASHTAG and category:
            templates = cls.HASHTAG_TEMPLATES.get(language, {}).get(category, [])
        else:
            return ""
        
        return random.choice(templates) if templates else ""
    
    @classmethod
    def generate_structured_prompt(cls, category: str, topic: str, style: str = "活泼", language: Language = Language.ZH_CN) -> str:
        """生成结构化提示词"""
        templates = cls.get_templates_by_category(category, language)
        
        if language == Language.ZH_CN:
            prompt = f"""
请为"{topic}"生成一篇{category}类型的小红书文案：

参考模板：
- 标题模板：{templates['titles'][:2] if templates['titles'] else '无'}
- 开头模板：{templates['openings'][:2] if templates['openings'] else '无'}  
- 结尾模板：{templates['endings'][:2] if templates['endings'] else '无'}
- 话题标签：{templates['hashtags'][:5] if templates['hashtags'] else '无'}

要求：
1. 语气风格：{style}
2. 内容要有价值和吸引力
3. 结构清晰，分段明确
4. 适当使用emoji
5. 包含互动引导
"""
        elif language == Language.EN_US:
            prompt = f"""
Please generate a Xiaohongshu post for "{topic}" in {category} category:

Reference templates:
- Title templates: {templates['titles'][:2] if templates['titles'] else 'None'}
- Opening templates: {templates['openings'][:2] if templates['openings'] else 'None'}
- Ending templates: {templates['endings'][:2] if templates['endings'] else 'None'}
- Hashtags: {templates['hashtags'][:5] if templates['hashtags'] else 'None'}

Requirements:
1. Tone: {style}
2. Content should be valuable and attractive
3. Clear structure with proper paragraphs
4. Appropriate emoji usage
5. Include interaction guidance
"""
        elif language == Language.ZH_TW:
            prompt = f"""
請為"{topic}"生成一篇{category}類型的小紅書文案：

參考模板：
- 標題模板：{templates['titles'][:2] if templates['titles'] else '無'}
- 開頭模板：{templates['openings'][:2] if templates['openings'] else '無'}
- 結尾模板：{templates['endings'][:2] if templates['endings'] else '無'}
- 話題標籤：{templates['hashtags'][:5] if templates['hashtags'] else '無'}

要求：
1. 語氣風格：{style}
2. 內容要有價值和吸引力
3. 結構清晰，分段明確
4. 適當使用emoji
5. 包含互動引導
"""
        else:  # Japanese
            prompt = f"""
"{topic}"について{category}カテゴリのXiaohongshu投稿を生成してください：

参考テンプレート：
- タイトルテンプレート：{templates['titles'][:2] if templates['titles'] else 'なし'}
- 開始テンプレート：{templates['openings'][:2] if templates['openings'] else 'なし'}
- 終了テンプレート：{templates['endings'][:2] if templates['endings'] else 'なし'}
- ハッシュタグ：{templates['hashtags'][:5] if templates['hashtags'] else 'なし'}

要求：
1. トーン：{style}
2. 価値があり魅力的な内容
3. 明確な構造と段落分け
4. 適切な絵文字の使用
5. インタラクション促進を含む
"""
        
        return prompt


def get_category_suggestions(language: Language = Language.ZH_CN) -> Dict[str, List[str]]:
    """获取分类建议"""
    suggestions = {
        Language.ZH_CN: {
            "美妆护肤": ["护肤步骤", "产品测评", "化妆教程", "护肤心得"],
            "时尚穿搭": ["穿搭攻略", "单品推荐", "搭配技巧", "风格分析"],
            "美食探店": ["餐厅推荐", "美食制作", "探店体验", "美食攻略"],
            "旅行攻略": ["目的地推荐", "旅行准备", "景点介绍", "旅行心得"],
            "生活方式": ["日常分享", "生活技巧", "好物推荐", "生活感悟"]
        },
        Language.EN_US: {
            "Beauty & Skincare": ["Skincare routine", "Product review", "Makeup tutorial", "Beauty tips"],
            "Fashion & Style": ["Style guide", "Item recommendation", "Styling tips", "Style analysis"],
            "Food & Dining": ["Restaurant review", "Food recipes", "Dining experience", "Food guide"],
            "Travel": ["Destination guide", "Travel prep", "Attractions", "Travel experience"],
            "Lifestyle": ["Daily sharing", "Life hacks", "Product finds", "Life insights"]
        },
        Language.ZH_TW: {
            "美妝護膚": ["護膚步驟", "產品測評", "化妝教程", "護膚心得"],
            "時尚穿搭": ["穿搭攻略", "單品推薦", "搭配技巧", "風格分析"],
            "美食探店": ["餐廳推薦", "美食製作", "探店體驗", "美食攻略"],
            "旅行攻略": ["目的地推薦", "旅行準備", "景點介紹", "旅行心得"],
            "生活方式": ["日常分享", "生活技巧", "好物推薦", "生活感悟"]
        },
        Language.JA_JP: {
            "美容・スキンケア": ["スキンケア手順", "商品レビュー", "メイクチュートリアル", "美容のコツ"],
            "ファッション・コーデ": ["スタイルガイド", "アイテム紹介", "コーデ術", "スタイル分析"],
            "グルメ・レストラン": ["レストラン紹介", "料理レシピ", "グルメ体験", "美食ガイド"],
            "旅行": ["観光地ガイド", "旅行準備", "観光スポット", "旅行体験"],
            "ライフスタイル": ["日常シェア", "生活のコツ", "おすすめアイテム", "生活の気づき"]
        }
    }
    
    return suggestions.get(language, suggestions[Language.ZH_CN])


def main():
    """演示模板使用"""
    print("🎨 小红书模板库演示")
    
    # 测试中文模板
    print("\n=== 中文模板 ===")
    zh_templates = XiaohongshuTemplates.get_templates_by_category("美妆护肤", Language.ZH_CN)
    print(f"标题模板: {zh_templates['titles'][:2]}")
    print(f"话题标签: {zh_templates['hashtags'][:5]}")
    
    # 测试英文模板
    print("\n=== English Templates ===")
    en_templates = XiaohongshuTemplates.get_templates_by_category("Beauty & Skincare", Language.EN_US)
    print(f"Title templates: {en_templates['titles'][:2]}")
    print(f"Hashtags: {en_templates['hashtags'][:5]}")
    
    # 测试随机模板
    print("\n=== 随机模板测试 ===")
    random_title = XiaohongshuTemplates.get_random_template(TemplateType.TITLE, "美妆护肤", Language.ZH_CN)
    print(f"随机标题: {random_title}")
    
    # 测试结构化提示词
    print("\n=== 结构化提示词 ===")
    prompt = XiaohongshuTemplates.generate_structured_prompt("美妆护肤", "冬季护肤", "温和专业", Language.ZH_CN)
    print(prompt[:200] + "...")


if __name__ == "__main__":
    main() 