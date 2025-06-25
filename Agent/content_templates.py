"""
小红书内容模板库
包含各种类型的文案模板和提示词
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


class XiaohongshuTemplates:
    """小红书文案模板库"""
    
    # 标题模板
    TITLE_TEMPLATES = {
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
        ],
        "旅行攻略": [
            "{目的地}{天数}游攻略！{特色}超{评价}✈️",
            "{目的地}旅行避雷指南！{建议}必看👀",
            "{预算}玩转{目的地}！{特色}攻略来了🗺️",
            "{目的地}小众景点！{特色}人少景美📸",
            "{季节}去{目的地}！{特色}{评价}到炸裂🔥"
        ],
        "生活方式": [
            "{主题}生活方式分享！{效果}太{评价}了✨",
            "{时间段}{习惯}让我{效果}！坚持{时长}💪",
            "{主题}日常！{效果}的{数量}个小技巧🌟",
            "分享我的{主题}好物！{效果}提升{程度}📈",
            "{主题}vlog！{效果}的一天记录💕"
        ]
    }
    
    # 内容开头模板
    OPENING_TEMPLATES = {
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
        ],
        "经验分享": [
            "作为{身份}，我想分享一些{主题}经验📚",
            "用了{时间}总结出来的{主题}心得💡",
            "今天来分享我的{主题}干货！超实用✨",
            "踩过坑才知道，{主题}原来要这样做😅"
        ],
        "测评对比": [
            "终于测评完了{数量}个{产品}！结果太意外😱",
            "花了{金额}测试{产品}，哪个最值得买？",
            "实测{数量}款{产品}，差距真的很大📊",
            "亲测告诉你，{产品A}vs{产品B}哪个更好👀"
        ]
    }
    
    # 内容结尾模板
    ENDING_TEMPLATES = {
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
        ],
        "情感共鸣": [
            "希望这个分享对你们有帮助❤️",
            "愿我们都能{愿望}，一起变更好✨",
            "生活就是要对自己好一点💕",
            "每天都要开开心心的呀🌈"
        ],
        "期待互动": [
            "期待你们的使用反馈哦📝",
            "有什么问题随时找我，在线解答💌",
            "下期想看什么内容？留言告诉我👂",
            "我们一起{目标}吧！冲冲冲🔥"
        ]
    }
    
    # 话题标签模板
    HASHTAG_TEMPLATES = {
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
        ],
        "旅行攻略": [
            "#旅行攻略", "#旅游分享", "#旅行日记", "#旅游博主",
            "#旅行vlog", "#景点推荐", "#旅游推荐", "#旅行种草",
            "#出行攻略", "#旅游攻略", "#旅行笔记", "#度假分享"
        ],
        "生活方式": [
            "#生活分享", "#生活记录", "#日常生活", "#生活博主",
            "#生活vlog", "#生活方式", "#生活攻略", "#生活好物",
            "#生活小技巧", "#生活日记", "#居家生活", "#生活感悟"
        ]
    }
    
    # 完整内容模板
    COMPLETE_TEMPLATES = {
        "产品推荐": """
{开头}

✨ 产品信息：
📦 产品名称：{产品名}
💰 价格：{价格}
🛒 购买渠道：{渠道}

💎 使用体验：
{体验描述}

⭐ 推荐理由：
1️⃣ {理由1}
2️⃣ {理由2}
3️⃣ {理由3}

{结尾}

{话题标签}
""",
        
        "攻略分享": """
{开头}

📝 {主题}攻略来啦：

🔍 准备工作：
{准备事项}

📋 详细步骤：
1️⃣ {步骤1}
2️⃣ {步骤2}
3️⃣ {步骤3}

⚠️ 注意事项：
{注意事项}

💡 小贴士：
{小贴士}

{结尾}

{话题标签}
""",
        
        "体验分享": """
{开头}

📍 体验地点：{地点}
⏰ 体验时间：{时间}
💰 消费金额：{金额}

🌟 体验过程：
{过程描述}

👍 优点：
{优点}

👎 缺点：
{缺点}

📊 综合评分：{评分}/10分

{结尾}

{话题标签}
"""
    }
    
    @classmethod
    def get_templates_by_category(cls, category: str) -> Dict[str, List[str]]:
        """根据分类获取模板"""
        templates = {}
        
        if category in cls.TITLE_TEMPLATES:
            templates["标题"] = cls.TITLE_TEMPLATES[category]
        
        if category in cls.HASHTAG_TEMPLATES:
            templates["话题标签"] = cls.HASHTAG_TEMPLATES[category]
        
        templates["开头"] = cls.OPENING_TEMPLATES
        templates["结尾"] = cls.ENDING_TEMPLATES
        templates["完整模板"] = cls.COMPLETE_TEMPLATES
        
        return templates
    
    @classmethod
    def get_random_template(cls, template_type: TemplateType, category: str = None) -> str:
        """获取随机模板"""
        import random
        
        if template_type == TemplateType.TITLE and category:
            if category in cls.TITLE_TEMPLATES:
                return random.choice(cls.TITLE_TEMPLATES[category])
        
        elif template_type == TemplateType.HASHTAG and category:
            if category in cls.HASHTAG_TEMPLATES:
                tags = cls.HASHTAG_TEMPLATES[category]
                return " ".join(random.sample(tags, min(6, len(tags))))
        
        elif template_type == TemplateType.OPENING:
            opening_type = random.choice(list(cls.OPENING_TEMPLATES.keys()))
            return random.choice(cls.OPENING_TEMPLATES[opening_type])
        
        elif template_type == TemplateType.ENDING:
            ending_type = random.choice(list(cls.ENDING_TEMPLATES.keys()))
            return random.choice(cls.ENDING_TEMPLATES[ending_type])
        
        return ""
    
    @classmethod
    def generate_structured_prompt(cls, category: str, topic: str, style: str = "活泼") -> str:
        """生成结构化的提示词"""
        
        prompt = f"""
请为小红书生成一篇关于"{topic}"的{category}内容，要求：

📋 内容要求：
1. 语气风格：{style}
2. 目标受众：小红书用户
3. 内容长度：200-400字
4. 结构清晰，易于阅读

📝 内容结构：
1. 吸引人的开头（使用emoji）
2. 有价值的主体内容（分点描述）
3. 引导互动的结尾
4. 相关话题标签

🎯 优化要点：
- 适当使用emoji表情
- 换行要合理
- 语言要生动有趣
- 内容要实用有价值
- 符合小红书调性

请生成完整的小红书文案。
"""
        
        return prompt


def main():
    """演示模板使用"""
    templates = XiaohongshuTemplates()
    
    print("📝 小红书内容模板库演示")
    print("=" * 40)
    
    # 演示获取分类模板
    category = "美妆护肤"
    print(f"📂 {category}分类模板：")
    
    category_templates = templates.get_templates_by_category(category)
    for template_type, template_list in category_templates.items():
        print(f"\n🏷️ {template_type}:")
        if isinstance(template_list, list):
            for i, template in enumerate(template_list[:3], 1):
                print(f"  {i}. {template}")
        elif isinstance(template_list, dict):
            for sub_type, sub_list in list(template_list.items())[:2]:
                print(f"  📌 {sub_type}: {sub_list[0] if sub_list else ''}")
    
    print("\n" + "=" * 40)
    
    # 演示随机模板
    print("🎲 随机模板演示：")
    print(f"随机标题: {templates.get_random_template(TemplateType.TITLE, category)}")
    print(f"随机开头: {templates.get_random_template(TemplateType.OPENING)}")
    print(f"随机结尾: {templates.get_random_template(TemplateType.ENDING)}")
    print(f"随机标签: {templates.get_random_template(TemplateType.HASHTAG, category)}")
    
    print("\n" + "=" * 40)
    
    # 演示结构化提示词
    print("🔧 结构化提示词：")
    prompt = templates.generate_structured_prompt(category, "冬季护肤保湿攻略", "专业温和")
    print(prompt)


if __name__ == "__main__":
    main() 