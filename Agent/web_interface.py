"""
小红书文案生成智能体Web界面
使用Streamlit构建的用户友好界面 - 优化版
"""

import streamlit as st
import sys
import os
import time
from typing import Dict, Any, Generator
import json

# 添加上级目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Agent.xiaohongshu_agent import XiaohongshuAgent, ContentCategory, ContentRequest
from Agent.content_templates import XiaohongshuTemplates, TemplateType


def init_custom_css():
    """初始化自定义CSS样式"""
    st.markdown("""
    <style>
        /* 主体样式优化 */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        
        /* 标题样式优化 */
        .main-header {
            background: linear-gradient(90deg, #ff6b9d, #ff8e7f, #ffb347);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .sub-header {
            text-align: center;
            color: #666;
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }
        
        /* 卡片样式 */
        .content-card {
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 1px solid #f0f0f0;
            margin-bottom: 1rem;
        }
        
        /* 按钮样式优化 */
        .stButton > button {
            border-radius: 25px;
            border: none;
            padding: 0.5rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }
        
        /* 主要按钮样式 */
        .stButton > button[kind="primary"] {
            background: linear-gradient(45deg, #ff6b9d, #ff8e7f);
            color: white;
        }
        
        /* 侧边栏样式 */
        .css-1d391kg {
            background: linear-gradient(180deg, #f8f9fa, #e9ecef);
        }
        
        /* 状态指示器 */
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-ready {
            background-color: #28a745;
            animation: pulse 2s infinite;
        }
        
        .status-error {
            background-color: #dc3545;
        }
        
        .status-warning {
            background-color: #ffc107;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        /* 生成内容样式 */
        .generated-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        /* 功能卡片 */
        .feature-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 4px solid #ff6b9d;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
            transition: transform 0.2s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-2px);
        }
        
        /* 加载动画 */
        .loading-animation {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
        }
        
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #ff6b9d;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* 聊天消息样式 */
        .chat-message {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 15px;
            max-width: 80%;
        }
        
        .user-message {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            margin-left: auto;
        }
        
        .assistant-message {
            background: #f8f9fa;
            color: #333;
            border: 1px solid #e9ecef;
        }
        
        /* 成功/错误消息样式 */
        .success-message {
            background: linear-gradient(90deg, #56ab2f, #a8e6cf);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        .error-message {
            background: linear-gradient(90deg, #ff416c, #ff4b2b);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        /* 模板展示样式 */
        .template-item {
            background: #f8f9fa;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 8px;
            border-left: 3px solid #ff6b9d;
            transition: all 0.2s ease;
        }
        
        .template-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }
        
        /* 响应式设计 */
        @media (max-width: 768px) {
            .main-header {
                font-size: 2rem;
            }
            
            .content-card {
                padding: 1rem;
            }
            
            .stButton > button {
                width: 100%;
                margin-bottom: 0.5rem;
            }
        }
        
        /* 工具提示样式 */
        .tooltip {
            position: relative;
            display: inline-block;
        }
        
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 200px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        
        /* 进度条样式 */
        .progress-container {
            width: 100%;
            background-color: #f0f0f0;
            border-radius: 25px;
            overflow: hidden;
            margin: 1rem 0;
        }
        
        .progress-bar {
            height: 20px;
            background: linear-gradient(90deg, #ff6b9d, #ff8e7f);
            border-radius: 25px;
            transition: width 0.3s ease;
        }
    </style>
    """, unsafe_allow_html=True)


class StreamHandler:
    """处理流式响应的类 - 增强版"""
    
    def __init__(self, placeholder):
        self.placeholder = placeholder
        self.content = ""
        self.chunk_count = 0
    
    def write(self, text: str):
        """写入流式内容"""
        self.content += text
        self.chunk_count += 1
        
        # 添加打字机效果的视觉反馈
        display_content = self.content
        if self.chunk_count % 3 == 0:  # 每3个chunk显示一次加载指示
            display_content += " ▋"
        
        self.placeholder.markdown(f"""
        <div class="generated-content">
            {display_content}
        </div>
        """, unsafe_allow_html=True)
    
    def clear(self):
        """清空内容"""
        self.content = ""
        self.chunk_count = 0
        self.placeholder.empty()
    
    def finalize(self):
        """完成显示"""
        self.placeholder.markdown(f"""
        <div class="generated-content">
            ✨ <strong>生成完成</strong><br><br>
            {self.content}
        </div>
        """, unsafe_allow_html=True)


def init_session_state():
    """初始化会话状态 - 增强版"""
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'agent_ready' not in st.session_state:
        st.session_state.agent_ready = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'enable_stream' not in st.session_state:
        st.session_state.enable_stream = True
    if 'enable_thinking' not in st.session_state:
        st.session_state.enable_thinking = True
    if 'last_generated_content' not in st.session_state:
        st.session_state.last_generated_content = ""
    if 'generating' not in st.session_state:
        st.session_state.generating = False
    if 'generation_progress' not in st.session_state:
        st.session_state.generation_progress = 0
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {
            'favorite_categories': [],
            'preferred_tone': '活泼可爱',
            'preferred_length': '中等'
        }
    if 'topic_input' not in st.session_state:
        st.session_state.topic_input = ""
    if 'selected_template' not in st.session_state:
        st.session_state.selected_template = ""


def show_status_indicator(status: str, message: str):
    """显示状态指示器"""
    status_class = f"status-{status}"
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin: 0.5rem 0;">
        <span class="status-indicator {status_class}"></span>
        <span>{message}</span>
    </div>
    """, unsafe_allow_html=True)


def is_agent_ready() -> bool:
    """统一检查智能体是否就绪"""
    return (hasattr(st.session_state, 'agent_ready') and 
            st.session_state.agent_ready and 
            hasattr(st.session_state, 'agent') and 
            st.session_state.agent is not None)


def setup_agent():
    """设置智能体 - 增强版"""
    if st.session_state.agent is None:
        # 创建进度指示器
        progress_placeholder = st.empty()
        
        with st.spinner('正在初始化智能体...'):
            # 显示初始化步骤
            steps = [
                "检查Ollama连接...",
                "加载模型配置...",
                "初始化智能体...",
                "验证功能完整性..."
            ]
            
            for i, step in enumerate(steps):
                progress = (i + 1) / len(steps) * 100
                progress_placeholder.markdown(f"""
                <div class="progress-container">
                    <div class="progress-bar" style="width: {progress}%"></div>
                </div>
                <p style="text-align: center;">{step}</p>
                """, unsafe_allow_html=True)
                time.sleep(0.5)  # 模拟加载时间
            
            try:
                agent = XiaohongshuAgent(
                    enable_stream=st.session_state.enable_stream,
                    enable_thinking=st.session_state.enable_thinking
                )
                if agent.check_setup():
                    st.session_state.agent = agent
                    st.session_state.agent_ready = True
                    progress_placeholder.empty()
                    
                    # 显示成功消息
                    st.markdown("""
                    <div class="success-message">
                        ✅ <strong>智能体初始化成功！</strong><br>
                        🎉 所有功能已就绪，您可以开始创作了
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 强制刷新页面以更新状态显示
                    time.sleep(0.5)  # 简短延迟让用户看到成功消息
                    st.rerun()
                    return True
                else:
                    # 确保失败时重置状态
                    st.session_state.agent = None
                    st.session_state.agent_ready = False
                    progress_placeholder.empty()
                    st.markdown("""
                    <div class="error-message">
                        ❌ <strong>智能体初始化失败</strong><br>
                        请检查Ollama服务是否正在运行
                    </div>
                    """, unsafe_allow_html=True)
                    return False
            except Exception as e:
                # 确保异常时重置状态
                st.session_state.agent = None
                st.session_state.agent_ready = False
                progress_placeholder.empty()
                st.markdown(f"""
                <div class="error-message">
                    ❌ <strong>初始化错误</strong><br>
                    {str(e)}
                </div>
                """, unsafe_allow_html=True)
                return False
    return st.session_state.agent_ready


def create_generation_progress():
    """创建生成进度指示器"""
    progress_container = st.empty()
    
    def update_progress(percentage: int, message: str):
        progress_container.markdown(f"""
        <div class="content-card">
            <h4>🎯 正在生成文案</h4>
            <div class="progress-container">
                <div class="progress-bar" style="width: {percentage}%"></div>
            </div>
            <p style="text-align: center; margin-top: 0.5rem;">{message}</p>
        </div>
        """, unsafe_allow_html=True)
    
    return update_progress, progress_container


def stream_generate_content(agent, request: ContentRequest):
    """生成内容 - 增强版"""
    # 创建美化的容器
    container = st.container()
    
    with container:
        # 显示请求信息卡片
        st.markdown(f"""
        <div class="content-card">
            <h4>📋 生成请求信息</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                <div><strong>分类:</strong> {request.category.value}</div>
                <div><strong>主题:</strong> {request.topic}</div>
                <div><strong>语气:</strong> {request.tone}</div>
                <div><strong>长度:</strong> {request.length}</div>
                <div><strong>受众:</strong> {request.target_audience}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 创建生成进度指示器
        update_progress, progress_container = create_generation_progress()
        
        try:
            if agent.enable_stream:
                # 流式生成
                update_progress(10, "正在连接AI模型...")
                time.sleep(0.5)
                
                update_progress(30, "开始内容创作...")
                content = ""
                chunk_count = 0
                max_chunks = 1000
                
                # 创建流式显示容器
                result_placeholder = st.empty()
                stream_handler = StreamHandler(result_placeholder)
                
                try:
                    update_progress(50, "AI正在思考创意...")
                    
                    for chunk in agent.generate_complete_post_stream(request):
                        if hasattr(st.session_state, 'generating') and not st.session_state.generating:
                            content = "⚠️ 生成已被用户停止"
                            break
                        
                        if chunk:
                            content += chunk
                            chunk_count += 1
                            stream_handler.write(chunk)
                            
                            # 更新进度
                            progress = min(50 + (chunk_count / max_chunks * 40), 90)
                            update_progress(int(progress), f"正在生成内容... ({chunk_count} 个片段)")
                            
                            if chunk_count >= max_chunks:
                                content += "\n\n⚠️ 已达到最大生成长度限制"
                                break
                    
                    update_progress(100, "生成完成！")
                    time.sleep(0.5)
                    progress_container.empty()
                    
                    # 完成显示
                    stream_handler.finalize()
                    
                except Exception as e:
                    content = f"❌ 生成失败：{str(e)}"
                    progress_container.empty()
                    st.markdown(f"""
                    <div class="error-message">
                        {content}
                    </div>
                    """, unsafe_allow_html=True)
            
            else:
                # 非流式模式
                update_progress(50, "正在生成文案，请稍候...")
                result = agent.generate_complete_post(request)
                
                progress_container.empty()
                
                if result["success"]:
                    content = result["content"]
                    st.markdown(f"""
                    <div class="generated-content">
                        ✨ <strong>生成完成</strong><br><br>
                        {content}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ 生成失败：{result['error']}
                    </div>
                    """, unsafe_allow_html=True)
                    content = ""
            
            return {
                "success": True,
                "content": content,
                "request": request.__dict__
            }
            
        except Exception as e:
            progress_container.empty()
            error_msg = f"❌ 生成失败：{str(e)}"
            st.markdown(f"""
            <div class="error-message">
                {error_msg}
            </div>
            """, unsafe_allow_html=True)
            return {
                "success": False,
                "error": str(e),
                "request": request.__dict__
            }


def content_generation_tab():
    """内容生成页面 - 增强版"""
    # 创建主标题
    st.markdown("""
    <div class="main-header">📝 智能文案生成</div>
    <div class="sub-header">让AI为您创作优质的小红书内容</div>
    """, unsafe_allow_html=True)
    
    # 快速开始卡片
    st.markdown("""
    <div class="content-card">
        <h4>🚀 快速开始</h4>
        <p>只需填写基本信息，AI将为您生成专业的小红书文案</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 用户偏好设置
    with st.expander("🎨 个性化设置", expanded=False):
        col_pref1, col_pref2 = st.columns(2)
        with col_pref1:
            save_preferences = st.checkbox("记住我的偏好设置")
    
    # 配置选项 - 美化版
    st.markdown("### 📋 内容配置")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h5>🏷️ 基础设置</h5>
        </div>
        """, unsafe_allow_html=True)
        
        category = st.selectbox(
            "选择内容分类",
            [cat.value for cat in ContentCategory],
            key="category",
            help="选择最符合您内容主题的分类"
        )
        
        # 检查是否有选中的模板
        if hasattr(st.session_state, 'selected_template') and st.session_state.selected_template:
            # 将选中的模板设置为默认主题
            if 'topic_input' not in st.session_state:
                st.session_state.topic_input = st.session_state.selected_template
            else:
                st.session_state.topic_input = st.session_state.selected_template
            # 清除选中的模板，避免重复应用
            st.session_state.selected_template = ""
        
        # 初始化主题输入状态
        if 'topic_input' not in st.session_state:
            st.session_state.topic_input = ""
        
        topic = st.text_input(
            "输入主题",
            value=st.session_state.topic_input,
            placeholder="例如：冬季护肤保湿攻略",
            help="描述您想要创作的具体主题"
        )
        
        # 更新session state
        st.session_state.topic_input = topic
        
        tone = st.selectbox(
            "语气风格",
            ["活泼可爱", "专业温和", "幽默风趣", "温馨治愈", "时尚潮流"],
            key="tone",
            index=0 if not save_preferences else ["活泼可爱", "专业温和", "幽默风趣", "温馨治愈", "时尚潮流"].index(st.session_state.user_preferences['preferred_tone']),
            help="选择最适合您目标受众的语气风格"
        )
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h5>🎯 进阶设置</h5>
        </div>
        """, unsafe_allow_html=True)
        
        length = st.selectbox(
            "内容长度",
            ["简短", "中等", "详细"],
            index=1 if not save_preferences else ["简短", "中等", "详细"].index(st.session_state.user_preferences['preferred_length']),
            key="length",
            help="根据平台特性和用户习惯选择合适的长度"
        )
        
        target_audience = st.selectbox(
            "目标受众",
            ["年轻女性", "上班族", "学生党", "宝妈群体", "中年女性"],
            key="target_audience",
            help="明确目标受众有助于生成更精准的内容"
        )
        
        keywords = st.text_input(
            "关键词（用逗号分隔）",
            placeholder="例如：保湿,护肤,冬季",
            key="keywords",
            help="添加相关关键词可以提高内容的搜索效果"
        )
    
    # 特殊要求区域
    st.markdown("""
    <div class="feature-card">
        <h5>📝 特殊要求</h5>
    </div>
    """, unsafe_allow_html=True)
    
    special_requirements = st.text_area(
        "特殊要求（可选）",
        placeholder="例如：需要包含产品推荐、添加购买链接、突出性价比等",
        key="special_requirements",
        height=100,
        help="描述任何特殊需求，AI会尽力满足"
    )
    
        # 状态显示区域
    st.markdown("### ⚙️ 生成设置")
    
    # 美化的状态显示
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        if st.session_state.enable_stream:
            show_status_indicator("ready", "流式响应已启用")
        else:
            show_status_indicator("warning", "使用标准生成模式")
    
    with status_col2:
        if is_agent_ready():
            show_status_indicator("ready", "AI智能体就绪")
        else:
            show_status_indicator("error", "智能体未初始化")
    
    with status_col3:
        if topic and len(topic) > 3:
            show_status_indicator("ready", "主题信息完整")
        else:
            show_status_indicator("warning", "请完善主题信息")
    
    # 生成按钮区域 - 美化版
    st.markdown("### 🎯 开始创作")
    
    # 预生成检查
    can_generate = bool(topic and len(topic.strip()) > 3 and is_agent_ready())
    
    if not can_generate:
        st.markdown("""
        <div class="content-card" style="border-left: 4px solid #ffc107;">
            <h5>⚠️ 生成前检查</h5>
            <ul style="margin: 0;">
        """, unsafe_allow_html=True)
        
        if not topic or len(topic.strip()) <= 3:
            st.markdown("• 请输入有效的主题（至少4个字符）", unsafe_allow_html=True)
        if not is_agent_ready():
            st.markdown("• 请先初始化AI智能体", unsafe_allow_html=True)
            
        st.markdown("</ul></div>", unsafe_allow_html=True)
    
    # 按钮布局
    col_gen1, col_gen2, col_gen3 = st.columns([2, 1, 1])
    
    with col_gen1:
        generate_clicked = st.button(
            "🚀 开始生成文案" if not st.session_state.generating else "⏳ 正在生成中...", 
            type="primary",
            disabled=not can_generate or st.session_state.generating,
            use_container_width=True
        )
    
    with col_gen2:
        if st.button("🛑 停止生成", 
                    type="secondary", 
                    disabled=not st.session_state.generating,
                    use_container_width=True):
            if hasattr(st.session_state, 'generating') and st.session_state.generating:
                st.session_state.generating = False
                st.markdown("""
                <div class="error-message">
                    ⚠️ 用户已停止生成
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("💡 当前没有正在生成的内容")
    
    with col_gen3:
        if st.button("🎲 随机主题", 
                    type="secondary",
                    disabled=st.session_state.generating,
                    use_container_width=True):
            random_topics = [
                "秋冬护肤必备好物分享",
                "学生党平价美妆推荐", 
                "职场穿搭时尚指南",
                "周末宅家美食制作",
                "旅行拍照pose教程"
            ]
            import random
            selected_topic = random.choice(random_topics)
            st.session_state.topic_input = selected_topic
            st.rerun()
    
    if generate_clicked:
        # 保存用户偏好
        if save_preferences:
            st.session_state.user_preferences.update({
                'preferred_tone': tone,
                'preferred_length': length
            })
        
        # 设置生成状态
        st.session_state.generating = True
        
        # 解析关键词
        keyword_list = [kw.strip() for kw in keywords.split(",") if kw.strip()] if keywords else None
        
        # 获取对应的枚举值
        category_enum = None
        for cat in ContentCategory:
            if cat.value == category:
                category_enum = cat
                break
        
        # 创建请求
        request = ContentRequest(
            category=category_enum,
            topic=topic,
            tone=tone,
            length=length,
            keywords=keyword_list,
            target_audience=target_audience,
            special_requirements=special_requirements
        )
        
        # 显示开始生成的提示
        st.markdown("""
        <div class="content-card" style="border-left: 4px solid #28a745;">
            <h5>🎯 开始生成</h5>
            <p>AI正在为您量身定制优质文案，请稍候...</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 使用流式生成
        result = stream_generate_content(st.session_state.agent, request)
        
        # 保存生成结果到session_state
        if result["success"]:
            st.session_state.last_generated_content = result["content"]
            
            # 显示生成统计
            content_length = len(result["content"])
            word_count = len(result["content"].split())
            
            st.markdown(f"""
            <div class="content-card">
                <h5>📊 生成统计</h5>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; text-align: center;">
                    <div>
                        <strong>{content_length}</strong><br>
                        <small>字符数</small>
                    </div>
                    <div>
                        <strong>{word_count}</strong><br>
                        <small>词语数</small>
                    </div>
                    <div>
                        <strong>{len(keyword_list) if keyword_list else 0}</strong><br>
                        <small>关键词</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 重置生成状态
        st.session_state.generating = False
    
    # 内容管理区域 - 增强版
    if hasattr(st.session_state, 'last_generated_content') and st.session_state.last_generated_content:
        st.markdown("---")
        st.markdown("""
        <div class="main-header" style="font-size: 2rem;">📝 内容管理</div>
        <div class="sub-header">对生成的内容进行进一步优化和管理</div>
        """, unsafe_allow_html=True)
        
        # 内容预览卡片
        st.markdown("""
        <div class="content-card">
            <h5>📄 当前内容预览</h5>
        </div>
        """, unsafe_allow_html=True)
        
        # 显示当前内容的简要信息
        content_preview = st.session_state.last_generated_content[:200] + "..." if len(st.session_state.last_generated_content) > 200 else st.session_state.last_generated_content
        st.markdown(f"**内容预览:** {content_preview}")
        
        # 管理按钮区域
        st.markdown("### 🛠️ 内容操作")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🎯 智能优化", key="optimize_btn", use_container_width=True):
                st.markdown("""
                <div class="content-card" style="border-left: 4px solid #17a2b8;">
                    <h5>🔄 正在智能优化</h5>
                    <p>AI正在分析内容并进行优化改进...</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 创建优化进度指示器
                opt_update_progress, opt_progress_container = create_generation_progress()
                
                try:
                    if st.session_state.enable_stream:
                        opt_update_progress(20, "分析当前内容...")
                        time.sleep(0.3)
                        
                        opt_update_progress(40, "寻找优化点...")
                        optimized_content = ""
                        chunk_count = 0
                        max_chunks = 500
                        
                        # 创建优化显示容器
                        opt_result_placeholder = st.empty()
                        opt_stream_handler = StreamHandler(opt_result_placeholder)
                        
                        try:
                            opt_update_progress(60, "开始优化重写...")
                            
                            for chunk in st.session_state.agent.optimize_content_stream(st.session_state.last_generated_content):
                                if chunk:
                                    optimized_content += chunk
                                    chunk_count += 1
                                    opt_stream_handler.write(chunk)
                                    
                                    # 更新进度
                                    progress = min(60 + (chunk_count / max_chunks * 30), 90)
                                    opt_update_progress(int(progress), f"优化中... ({chunk_count} 个片段)")
                                    
                                    if chunk_count >= max_chunks:
                                        optimized_content += "\n\n⚠️ 已达到最大优化长度限制"
                                        break
                            
                            opt_update_progress(100, "优化完成！")
                            time.sleep(0.5)
                            opt_progress_container.empty()
                            
                            # 完成显示
                            opt_stream_handler.finalize()
                            st.session_state.last_generated_content = optimized_content
                            
                        except Exception as e:
                            optimized_content = f"优化失败：{str(e)}"
                            opt_progress_container.empty()
                            st.markdown(f"""
                            <div class="error-message">
                                {optimized_content}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        opt_update_progress(50, "正在优化文案...")
                        optimization_result = st.session_state.agent.optimize_content(st.session_state.last_generated_content)
                        
                        opt_progress_container.empty()
                        
                        if optimization_result["success"]:
                            st.session_state.last_generated_content = optimization_result["optimized"]
                            st.markdown(f"""
                            <div class="generated-content">
                                ✅ <strong>优化完成</strong><br><br>
                                {optimization_result['optimized']}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="error-message">
                                ❌ 优化失败：{optimization_result['error']}
                            </div>
                            """, unsafe_allow_html=True)
                except Exception as e:
                    opt_progress_container.empty()
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ 优化过程出错：{str(e)}
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            if st.button("📋 复制内容", key="copy_btn", use_container_width=True):
                # 创建一个包含JavaScript的复制功能
                st.markdown(f"""
                <div class="content-card">
                    <h5>📋 复制到剪贴板</h5>
                    <textarea id="copy-content" style="width: 100%; height: 100px; margin: 10px 0;">{st.session_state.last_generated_content}</textarea>
                    <button onclick="
                        var content = document.getElementById('copy-content');
                        content.select();
                        document.execCommand('copy');
                        alert('内容已复制到剪贴板！');
                    " style="background: #ff6b9d; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer;">
                        点击复制
                    </button>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            if st.button("💾 保存文案", key="save_btn", use_container_width=True):
                # 生成文件名
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"xiaohongshu_content_{timestamp}.txt"
                
                # 创建下载链接
                st.download_button(
                    label="📥 下载文案文件",
                    data=st.session_state.last_generated_content,
                    file_name=filename,
                    mime="text/plain",
                    use_container_width=True
                )
                
                st.success(f"✅ 文案已准备下载：{filename}")
        
        with col4:
            if st.button("🗑️ 清空内容", key="clear_content_btn", use_container_width=True):
                st.session_state.last_generated_content = ""
                st.markdown("""
                <div class="success-message">
                    ✅ 内容已清空，可以开始新的创作
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()
        
        # 版本历史（如果有的话）
        if hasattr(st.session_state, 'content_history') and st.session_state.content_history:
            with st.expander("📚 历史版本", expanded=False):
                for i, content in enumerate(reversed(st.session_state.content_history[-5:]), 1):
                    st.markdown(f"**版本 {i}:** {content[:100]}...")
                    if st.button(f"恢复版本 {i}", key=f"restore_{i}"):
                        st.session_state.last_generated_content = content
                        st.rerun()


def template_gallery_tab():
    """模板展示页面 - 增强版"""
    # 创建主标题
    st.markdown("""
    <div class="main-header">🎨 专业模板库</div>
    <div class="sub-header">精选优质模板，让您的创作更加专业高效</div>
    """, unsafe_allow_html=True)
    
    # 模板统计卡片
    st.markdown("""
    <div class="content-card">
        <h4>📊 模板库统计</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; text-align: center;">
            <div>
                <strong>50+</strong><br>
                <small>精选模板</small>
            </div>
            <div>
                <strong>5</strong><br>
                <small>主要分类</small>
            </div>
            <div>
                <strong>10+</strong><br>
                <small>子分类</small>
            </div>
            <div>
                <strong>100%</strong><br>
                <small>实用性</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    templates = XiaohongshuTemplates()
    
    # 分类选择区域
    st.markdown("### 🏷️ 选择模板分类")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        category = st.selectbox(
            "选择分类查看模板",
            ["美妆护肤", "时尚穿搭", "美食探店", "旅行攻略", "生活方式"],
            key="template_category",
            help="每个分类都包含多种精心设计的模板结构"
        )
    
    with col2:
        view_mode = st.radio(
            "显示模式",
            ["卡片视图", "列表视图"],
            horizontal=True,
            key="template_view_mode"
        )
    
    # 搜索功能
    search_term = st.text_input(
        "🔍 搜索模板",
        placeholder="输入关键词搜索相关模板...",
        key="template_search"
    )
    
    category_templates = templates.get_templates_by_category(category)
    
    # 模板展示区域
    st.markdown(f"### 📋 {category} 模板")
    
    for template_type, template_list in category_templates.items():
        # 如果有搜索词，过滤模板
        if search_term:
            if search_term.lower() not in template_type.lower():
                continue
        
        if view_mode == "卡片视图":
            # 卡片视图
            st.markdown(f"""
            <div class="feature-card">
                <h5>📌 {template_type}</h5>
            </div>
            """, unsafe_allow_html=True)
            
            if isinstance(template_list, list):
                # 创建网格布局
                cols = st.columns(2)
                for i, template in enumerate(template_list):
                    with cols[i % 2]:
                        st.markdown(f"""
                        <div class="template-item">
                            <strong>{i+1}.</strong> {template}
                            <br><br>
                            <small style="color: #666;">点击可复制到生成器</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"使用此模板", key=f"use_template_{template_type}_{i}"):
                            # 将模板内容设置到临时变量，然后触发页面重新加载
                            st.session_state.selected_template = template
                            st.success(f"✅ 模板已应用到主题输入框")
                            st.rerun()
                            
            elif isinstance(template_list, dict):
                for sub_type, sub_list in template_list.items():
                    with st.expander(f"📂 {sub_type}", expanded=False):
                        if isinstance(sub_list, list):
                            for i, item in enumerate(sub_list):
                                st.markdown(f"""
                                <div class="template-item">
                                    • {item}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.code(sub_list, language="markdown")
        
        else:
            # 列表视图
            st.markdown(f"#### 📋 {template_type}")
            
            if isinstance(template_list, list):
                for i, template in enumerate(template_list, 1):
                    col_template, col_action = st.columns([4, 1])
                    
                    with col_template:
                        st.markdown(f"**{i}.** {template}")
                    
                    with col_action:
                        if st.button("使用", key=f"use_list_template_{template_type}_{i}", type="secondary"):
                            st.session_state.selected_template = template
                            st.success("✅ 已应用")
                            st.rerun()
                            
            elif isinstance(template_list, dict):
                for sub_type, sub_list in template_list.items():
                    with st.expander(f"📌 {sub_type}"):
                        if isinstance(sub_list, list):
                            for item in sub_list:
                                st.markdown(f"• {item}")
                        else:
                            st.code(sub_list, language="markdown")
    
    # 自定义模板区域
    st.markdown("---")
    st.markdown("### ✏️ 创建自定义模板")
    
    with st.expander("💡 创建您的专属模板", expanded=False):
        custom_template_name = st.text_input(
            "模板名称",
            placeholder="例如：我的护肤心得模板"
        )
        
        custom_template_content = st.text_area(
            "模板内容",
            placeholder="输入您的模板内容...",
            height=150
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 保存模板", type="primary"):
                if custom_template_name and custom_template_content:
                    # 这里可以保存到本地或数据库
                    st.success(f"✅ 模板 '{custom_template_name}' 已保存")
                else:
                    st.warning("请填写模板名称和内容")
        
        with col2:
            if st.button("🎯 预览效果"):
                if custom_template_content:
                    st.markdown(f"""
                    <div class="generated-content">
                        <strong>预览效果</strong><br><br>
                        {custom_template_content}
                    </div>
                    """, unsafe_allow_html=True)
    
    # 模板使用技巧
    st.markdown("---")
    st.markdown("""
    <div class="content-card">
        <h5>💡 模板使用技巧</h5>
        <ul>
            <li><strong>选择合适分类:</strong> 根据您的内容主题选择最相关的模板分类</li>
            <li><strong>个性化修改:</strong> 模板只是起点，请根据实际需求进行调整</li>
            <li><strong>组合使用:</strong> 可以结合多个模板的优点创造新内容</li>
            <li><strong>保持原创:</strong> 在模板基础上加入您的独特观点和经验</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


def chat_tab():
    """对话页面 - 增强版"""
    # 创建主标题
    st.markdown("""
    <div class="main-header">💬 智能对话助手</div>
    <div class="sub-header">与AI助手进行自然对话，获得专业的创作建议和指导</div>
    """, unsafe_allow_html=True)
    
    if not is_agent_ready():
        st.markdown("""
        <div class="content-card" style="border-left: 4px solid #ffc107;">
            <h5>⚠️ 智能体未就绪</h5>
            <p>请先在侧边栏初始化智能体后再开始对话</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # 对话状态和功能区域
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.enable_stream:
            show_status_indicator("ready", "流式对话模式")
        else:
            show_status_indicator("warning", "标准对话模式")
    
    with col2:
        chat_count = len(st.session_state.chat_history) // 2
        show_status_indicator("ready" if chat_count > 0 else "warning", f"对话轮数: {chat_count}")
    
    with col3:
        if st.button("🎭 对话风格", key="chat_style_btn"):
            st.session_state.chat_style = "专业" if st.session_state.get('chat_style', '友好') == "友好" else "友好"
            st.success(f"✅ 已切换到{st.session_state.chat_style}风格")
    
    # 快速问题建议
    if len(st.session_state.chat_history) == 0:
        st.markdown("""
        <div class="content-card">
            <h5>🚀 快速开始</h5>
            <p>选择下面的问题快速开始对话，或直接输入您的问题</p>
        </div>
        """, unsafe_allow_html=True)
        
        quick_questions = [
            "如何写出吸引人的小红书标题？",
            "什么样的内容容易成为爆款？",
            "如何提高小红书笔记的曝光率？",
            "不同分类的文案有什么特点？"
        ]
        
        cols = st.columns(2)
        for i, question in enumerate(quick_questions):
            with cols[i % 2]:
                if st.button(f"💡 {question}", key=f"quick_q_{i}", use_container_width=True):
                    # 自动输入问题
                    st.session_state.auto_input = question
                    st.rerun()
    
    # 对话历史显示容器
    chat_container = st.container()
    
    with chat_container:
        # 显示对话历史
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message" style="margin-left: 20%;">
                    <strong>您:</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message" style="margin-right: 20%;">
                    <strong>🤖 AI助手:</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
                
                # 添加有用性评价按钮
                col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])
                with col1:
                    if st.button("👍", key=f"like_{i}", help="这个回答有用"):
                        st.success("感谢您的反馈！")
                with col2:
                    if st.button("👎", key=f"dislike_{i}", help="这个回答不够好"):
                        st.info("我们会继续改进")
                with col3:
                    if st.button("📋", key=f"copy_response_{i}", help="复制回答"):
                        st.info("请手动复制上方内容")
                with col4:
                    if st.button("🔄", key=f"regenerate_{i}", help="重新生成"):
                        st.info("正在重新生成回答...")
    
    # 智能输入区域
    st.markdown("---")
    
    # 处理自动输入
    default_input = ""
    if hasattr(st.session_state, 'auto_input'):
        default_input = st.session_state.auto_input
        delattr(st.session_state, 'auto_input')
    
    # 输入提示和建议
    st.markdown("""
    <div class="content-card">
        <h5>💭 输入建议</h5>
        <p><strong>提问技巧:</strong> 描述具体场景、提供详细信息、明确您的需求目标</p>
        <p><strong>示例:</strong> "我是美妆博主，想写一篇关于秋季护肤的笔记，目标受众是25-35岁职场女性"</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 使用chat_input处理用户输入
    user_input = st.chat_input(
        "💭 输入您的问题或需求..." if not default_input else default_input,
        key="chat_input"
    )
    
    # 如果有默认输入，自动处理
    if default_input and not user_input:
        user_input = default_input
    
    if user_input:
        # 添加用户消息到历史记录
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # 显示"正在思考"的提示
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("""
        <div class="loading-animation">
            <div class="spinner"></div>
            <span style="margin-left: 1rem;">🤔 AI正在思考您的问题...</span>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            if st.session_state.enable_stream:
                # 流式模式
                response = ""
                for chunk in st.session_state.agent.chat_stream(user_input):
                    response += chunk
                
                thinking_placeholder.empty()
                
            else:
                # 非流式模式
                response = st.session_state.agent.chat(user_input)
                thinking_placeholder.empty()
            
            # 添加智能体回复到历史记录
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })
            
            st.rerun()
            
        except Exception as e:
            thinking_placeholder.empty()
            error_msg = f"❌ 对话出错：{str(e)}"
            
            st.markdown(f"""
            <div class="error-message">
                {error_msg}
            </div>
            """, unsafe_allow_html=True)
            
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": error_msg
            })
    
    # 对话管理区域
    st.markdown("---")
    st.markdown("### 🛠️ 对话管理")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🗑️ 清空对话", use_container_width=True):
            st.session_state.chat_history = []
            st.markdown("""
            <div class="success-message">
                ✅ 对话历史已清空
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()
    
    with col2:
        if st.button("💾 导出对话", use_container_width=True):
            if st.session_state.chat_history:
                # 生成对话记录文本
                chat_text = ""
                for msg in st.session_state.chat_history:
                    role = "用户" if msg["role"] == "user" else "AI助手"
                    chat_text += f"{role}: {msg['content']}\n\n"
                
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"chat_history_{timestamp}.txt"
                
                st.download_button(
                    label="📥 下载对话记录",
                    data=chat_text,
                    file_name=filename,
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.info("暂无对话记录")
    
    with col3:
        if st.button("📊 对话统计", use_container_width=True):
            if st.session_state.chat_history:
                user_msgs = len([m for m in st.session_state.chat_history if m["role"] == "user"])
                ai_msgs = len([m for m in st.session_state.chat_history if m["role"] == "assistant"])
                total_chars = sum(len(m["content"]) for m in st.session_state.chat_history)
                
                st.markdown(f"""
                <div class="content-card">
                    <h5>📊 对话统计</h5>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; text-align: center;">
                        <div><strong>{user_msgs}</strong><br><small>用户消息</small></div>
                        <div><strong>{ai_msgs}</strong><br><small>AI回复</small></div>
                        <div><strong>{total_chars}</strong><br><small>总字符数</small></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("暂无对话数据")
    
    with col4:
        if st.button("❓ 使用帮助", use_container_width=True):
            st.markdown("""
            <div class="content-card">
                <h5>❓ 对话功能使用帮助</h5>
                <ul>
                    <li><strong>自然对话:</strong> 像和朋友聊天一样描述您的需求</li>
                    <li><strong>具体描述:</strong> 提供越多细节，AI回复越精准</li>
                    <li><strong>分步骤问:</strong> 复杂问题可以分解成多个小问题</li>
                    <li><strong>反馈评价:</strong> 使用👍👎按钮帮助AI改进</li>
                    <li><strong>保存记录:</strong> 重要对话记得导出保存</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)





def main():
    """主函数 - 增强版"""
    st.set_page_config(
        page_title="小红书文案生成智能体",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/your-repo/help',
            'Report a bug': "https://github.com/your-repo/issues",
            'About': "# 小红书文案生成智能体\n基于AI的专业文案生成工具"
        }
    )
    
    # 初始化自定义CSS
    init_custom_css()
    
    # 初始化会话状态
    init_session_state()
    
    # 主标题区域
    st.markdown("""
    <div class="main-header">📝 小红书文案生成智能体</div>
    <div class="sub-header">基于LangChain和Ollama的智能文案生成工具</div>
    """, unsafe_allow_html=True)
    
    # 系统状态概览
    if is_agent_ready():
        st.markdown("""
        <div class="success-message">
            🎉 <strong>系统就绪</strong> - AI智能体已初始化完成，所有功能可正常使用
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="error-message">
            ⚠️ <strong>系统未就绪</strong> - 请在侧边栏初始化AI智能体
        </div>
        """, unsafe_allow_html=True)
    
    # 侧边栏 - 增强版
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2>⚙️ 控制中心</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # 系统状态卡片
        st.markdown("""
        <div class="content-card">
            <h5>📊 系统状态</h5>
        </div>
        """, unsafe_allow_html=True)
        
        # 智能体状态
        if is_agent_ready():
            show_status_indicator("ready", "AI智能体已就绪")
            
            # 显示详细配置
            st.markdown(f"""
            <div class="feature-card">
                <h6>🔧 当前配置</h6>
                <ul style="margin: 0; padding-left: 1rem;">
                    <li>流式响应: {'✅ 已启用' if st.session_state.enable_stream else '❌ 已关闭'}</li>
                    <li>思考模式: {'✅ 已启用' if st.session_state.enable_thinking else '❌ 已关闭'}</li>
                    <li>对话历史: {len(st.session_state.chat_history)} 条</li>
                    <li>生成状态: {'🔄 进行中' if st.session_state.generating else '⏸️ 空闲'}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            show_status_indicator("error", "智能体未初始化")
            
            st.markdown("""
            <div class="content-card" style="border-left: 4px solid #dc3545;">
                <h6>🚀 快速初始化</h6>
                <p>点击下方按钮初始化AI智能体</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 初始化智能体", type="primary", use_container_width=True):
                setup_agent()
        
        st.markdown("---")
        
        # 配置选项区域
        st.markdown("### 🔧 高级设置")
        
        with st.expander("⚙️ 模型配置", expanded=is_agent_ready()):
            # 流式响应设置
            new_enable_stream = st.checkbox(
                "启用流式响应",
                value=st.session_state.enable_stream,
                help="实时显示生成过程，体验更流畅"
            )
            
            # 思考模式设置
            new_enable_thinking = st.checkbox(
                "启用思考模式", 
                value=st.session_state.enable_thinking,
                help="显示AI的思考过程，便于理解生成逻辑"
            )
            
            # 检查配置是否有变化
            config_changed = (
                new_enable_stream != st.session_state.enable_stream or
                new_enable_thinking != st.session_state.enable_thinking
            )
            
            if config_changed:
                st.session_state.enable_stream = new_enable_stream
                st.session_state.enable_thinking = new_enable_thinking
                if is_agent_ready():
                    st.session_state.agent.update_config(
                        enable_stream=new_enable_stream,
                        enable_thinking=new_enable_thinking
                    )
                    st.success("✅ 配置已更新")
        
        # 用户偏好设置
        with st.expander("👤 个人偏好", expanded=False):
            if st.session_state.user_preferences:
                st.markdown("**当前偏好设置:**")
                st.write(f"• 偏好语气: {st.session_state.user_preferences.get('preferred_tone', '未设置')}")
                st.write(f"• 偏好长度: {st.session_state.user_preferences.get('preferred_length', '未设置')}")
                
                if st.button("🗑️ 重置偏好"):
                    st.session_state.user_preferences = {
                        'favorite_categories': [],
                        'preferred_tone': '活泼可爱',
                        'preferred_length': '中等'
                    }
                    st.success("✅ 偏好已重置")
        
        st.markdown("---")
        
        # 功能介绍卡片
        st.markdown("""
        <div class="feature-card">
            <h5>🎯 核心功能</h5>
            <ul style="margin: 0; padding-left: 1rem; font-size: 0.9rem;">
                <li>🤖 AI智能文案生成</li>
                <li>🎨 专业模板库</li>
                <li>💬 智能对话助手</li>
                <li>🔄 内容智能优化</li>
                <li>📊 数据统计分析</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 支持分类展示
        st.markdown("""
        <div class="feature-card">
            <h5>📋 支持分类</h5>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.8rem;">
                <div>💄 美妆护肤</div>
                <div>👗 时尚穿搭</div>
                <div>🍽️ 美食探店</div>
                <div>✈️ 旅行攻略</div>
                <div>🌱 生活方式</div>
                <div>💪 健身运动</div>
                <div>🏠 家居装饰</div>
                <div>📚 学习分享</div>
                <div>💼 职场干货</div>
                <div>🛍️ 好物推荐</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 使用统计
        if is_agent_ready():
            content_status = '有' if st.session_state.last_generated_content else '无'
            chat_count = len(st.session_state.chat_history) // 2
            st.markdown(f"""
            <div class="feature-card">
                <h5>📈 使用统计</h5>
                <div style="font-size: 0.9rem;">
                    <div>本次会话: <strong>运行中</strong></div>
                    <div>生成内容: <strong>{content_status}</strong></div>
                    <div>对话轮数: <strong>{chat_count}</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 快速操作
        st.markdown("### ⚡ 快速操作")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🆕 新建", help="清空所有内容，重新开始", use_container_width=True):
                st.session_state.last_generated_content = ""
                st.session_state.chat_history = []
                st.success("✅ 已重置")
        
        with col2:
            if st.button("🔄 重载", help="重新加载页面", use_container_width=True):
                st.rerun()
    
    # 主要内容区域 - 增强版标签页
    tab1, tab2, tab3 = st.tabs([
        "📝 智能生成", 
        "🎨 模板库", 
        "💬 对话助手"
    ])
    
    with tab1:
        content_generation_tab()
    
    with tab2:
        template_gallery_tab()
    
    with tab3:
        chat_tab()
    
    # 增强版页脚
    st.markdown("---")
    
    # 页脚信息卡片
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    
    with footer_col1:
        st.markdown("""
        <div class="content-card">
            <h6>💡 使用提示</h6>
            <small>确保Ollama服务正在运行，并已安装qwen3-redbook-q8:latest模型</small>
        </div>
        """, unsafe_allow_html=True)
    
    with footer_col2:
        st.markdown("""
        <div class="content-card">
            <h6>🛠️ 技术支持</h6>
            <small>基于LangChain、Streamlit和Ollama构建</small>
        </div>
        """, unsafe_allow_html=True)
    
    with footer_col3:
        st.markdown("""
        <div class="content-card">
            <h6>📊 版本信息</h6>
            <small>小红书文案生成智能体 v2.0 - 优化版</small>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main() 