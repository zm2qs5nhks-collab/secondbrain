"""
第二大脑 —— 图形化界面 (Streamlit)
启动命令: streamlit run app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import json
import time
from pathlib import Path

st.set_page_config(
    page_title="第二大脑",
    layout="wide",
    initial_sidebar_state="expanded",
)

import config

from storage.db import query_one, execute

# ═══════════════════════════════════════════
#  登录/注册页面
# ═══════════════════════════════════════════
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

if st.session_state.user_id is None:
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #1a1025 0%, #2d1b69 40%, #1a1025 100%) !important;
        min-height: 100vh;
    }
    .block-container {
        max-width: 100% !important;
        padding-top: 2rem !important;
    }
    [data-testid="stHeader"], [data-testid="stToolbar"] { display: none; }
    [data-testid="stSidebar"] { display: none; }

    .glass-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.04) 100%);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3),
                    inset 0 1px 0 rgba(255, 255, 255, 0.2),
                    inset 0 -1px 0 rgba(255, 255, 255, 0.05);
        padding: 2.5rem 2rem;
        position: relative;
        overflow: hidden;
    }
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 50%;
        background: linear-gradient(180deg, rgba(255,255,255,0.08) 0%, transparent 100%);
        border-radius: 24px 24px 0 0;
        pointer-events: none;
    }
    .glass-card::after {
        content: '';
        position: absolute;
        top: -40%; left: -20%;
        width: 140%;
        height: 60%;
        background: radial-gradient(ellipse, rgba(255,255,255,0.06) 0%, transparent 70%);
        pointer-events: none;
        transform: rotate(-5deg);
    }

    .stTextInput > div > div > input {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
        background: rgba(255, 255, 255, 0.07) !important;
        color: #fff !important;
        transition: all 0.25s ease !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(167, 139, 250, 0.6) !important;
        box-shadow: 0 0 0 2px rgba(167, 139, 250, 0.15) !important;
        background: rgba(255, 255, 255, 0.1) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.35) !important;
    }
    .stTextInput label {
        font-weight: 600 !important;
        color: rgba(255, 255, 255, 0.75) !important;
        font-size: 0.85rem !important;
    }

    div[data-testid="stForm"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #7c5cbf 0%, #a78bfa 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 0.65rem 0 !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        width: 100% !important;
        box-shadow: 0 4px 20px rgba(124, 92, 191, 0.4) !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.08em;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(124, 92, 191, 0.55) !important;
    }

    .stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]) {
        background: rgba(255, 255, 255, 0.08) !important;
        color: rgba(255, 255, 255, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]):hover {
        background: rgba(255, 255, 255, 0.15) !important;
        color: #fff !important;
    }

    .auth-switch {
        text-align: center;
        font-size: 0.88rem;
        color: rgba(255, 255, 255, 0.45);
        margin-top: 1.2rem;
    }
    .auth-switch span.hl {
        color: #a78bfa;
        font-weight: 600;
        cursor: pointer;
    }

    .feature-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    .feature-title {
        font-size: 1rem;
        font-weight: 700;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 0.3rem;
    }
    .feature-desc {
        font-size: 0.82rem;
        color: rgba(255, 255, 255, 0.45);
        line-height: 1.5;
    }

    .decor-orb {
        position: fixed;
        border-radius: 50%;
        pointer-events: none;
        z-index: 0;
    }
    .decor-orb.o1 {
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(124,92,191,0.25) 0%, transparent 70%);
        top: -100px; right: -80px;
    }
    .decor-orb.o2 {
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(167,139,250,0.15) 0%, transparent 70%);
        bottom: -50px; left: -50px;
    }
    .decor-orb.o3 {
        width: 150px; height: 150px;
        background: radial-gradient(circle, rgba(124,92,191,0.12) 0%, transparent 70%);
        top: 40%; left: 8%;
    }

    .stAlert {
        border-radius: 12px !important;
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    .stAlert p, .stAlert li { color: rgba(255, 255, 255, 0.85) !important; }
    [data-testid="stFormSubmitButton"] button { width: 100% !important; }
    </style>
    <div class="decor-orb o1"></div>
    <div class="decor-orb o2"></div>
    <div class="decor-orb o3"></div>
    """, unsafe_allow_html=True)

    left_col, center_col, right_col = st.columns([1, 1.3, 1], gap="medium")

    with left_col:
        st.markdown("""
        <div style="padding-top: 1rem;">
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">智能问答</div>
                <div class="feature-desc">基于你的知识库，AI 实时检索并回答问题，每一条回答都有出处。</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📐</div>
                <div class="feature-title">语义搜索</div>
                <div class="feature-desc">不只是关键词匹配，深度理解你的笔记含义，精准找到相关内容。</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔄</div>
                <div class="feature-title">遗忘曲线</div>
                <div class="feature-desc">基于艾宾浩斯遗忘曲线，智能安排复习节点，让知识长期保留。</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        st.markdown("""
        <div style="padding-top: 1rem;">
            <div class="feature-card">
                <div class="feature-icon">🔒</div>
                <div class="feature-title">数据私有</div>
                <div class="feature-desc">所有数据存储在你自己的服务器上，完全掌控隐私，绝不上传第三方。</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <div class="feature-title">多源导入</div>
                <div class="feature-desc">支持文本、文件、网页 URL 一键导入，自动切片、向量化、入库。</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔌</div>
                <div class="feature-title">开放 API</div>
                <div class="feature-desc">提供标准 RESTful API 接口，轻松接入第三方工具与自动化流程。</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with center_col:
        st.markdown("""
        <div class="glass-card">
            <div style="position:relative; z-index:1; text-align:center;">
                <div style="font-size:2rem; margin-bottom:0.3rem;">🧠</div>
                <div class="auth-title">第二大脑</div>
                <div class="auth-subtitle">你的 AI 知识管理助手</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="height: 0.3rem;"></div>', unsafe_allow_html=True)

        if "auth_mode" not in st.session_state:
            st.session_state.auth_mode = "login"

        btn_cols = st.columns(2)
        with btn_cols[0]:
            login_active = st.session_state.auth_mode == "login"
            login_btn = st.button("🔑 登录", key="mode_login", use_container_width=True,
                                  type="primary" if login_active else "secondary")
        with btn_cols[1]:
            register_active = st.session_state.auth_mode == "register"
            register_btn = st.button("📝 注册", key="mode_register", use_container_width=True,
                                     type="primary" if register_active else "secondary")

        if login_btn:
            st.session_state.auth_mode = "login"
            st.rerun()
        if register_btn:
            st.session_state.auth_mode = "register"
            st.rerun()

        st.markdown('<div style="height: 0.3rem;"></div>', unsafe_allow_html=True)

        if st.session_state.auth_mode == "login":
            login_email = st.text_input("邮箱", key="login_email", placeholder="your@email.com")
            login_pwd = st.text_input("密码", type="password", key="login_pwd", placeholder="输入密码")
            if st.button("登  录", type="primary", key="btn_login", use_container_width=True):
                if not login_email or not login_pwd:
                    st.error("请输入邮箱和密码")
                else:
                    import hashlib
                    pwd_hash = hashlib.sha256(login_pwd.encode()).hexdigest()
                    user = query_one(
                        "SELECT id, email FROM users WHERE email = %s AND password_hash = %s",
                        (login_email, pwd_hash),
                    )
                    if user:
                        st.session_state.user_id = str(user["id"])
                        st.session_state.user_email = user["email"]
                        st.rerun()
                    else:
                        st.error("邮箱或密码错误")

        else:
            reg_email = st.text_input("邮箱", key="reg_email", placeholder="your@email.com")
            reg_pwd = st.text_input("密码", type="password", key="reg_pwd", placeholder="至少6位")
            reg_pwd2 = st.text_input("确认密码", type="password", key="reg_pwd2", placeholder="再次输入密码")
            if st.button("注  册", type="primary", key="btn_register", use_container_width=True):
                if not reg_email or not reg_pwd:
                    st.error("请输入邮箱和密码")
                elif len(reg_pwd) < 6:
                    st.error("密码至少需要6位")
                elif reg_pwd != reg_pwd2:
                    st.error("两次密码不一致")
                else:
                    existing = query_one("SELECT id FROM users WHERE email = %s", (reg_email,))
                    if existing:
                        st.error("该邮箱已注册")
                    else:
                        import hashlib
                        pwd_hash = hashlib.sha256(reg_pwd.encode()).hexdigest()
                        execute(
                            "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
                            (reg_email, pwd_hash),
                        )
                        st.success("注册成功！")
                        st.session_state.auth_mode = "login"
                        st.rerun()

    st.stop()

# ─── 登录成功 ───
USER_ID = st.session_state.user_id

from memory import long_term
from agent.llm import set_user_settings
set_user_settings(
    USER_ID,
    api_key=long_term.get_preference("api_key", config.OPENAI_API_KEY, user_id=USER_ID),
    base_url=long_term.get_preference("api_base_url", config.OPENAI_BASE_URL, user_id=USER_ID),
    model_name=long_term.get_preference("model_name", config.MODEL_NAME, user_id=USER_ID),
    embedding_model=long_term.get_preference("embedding_model", config.EMBEDDING_MODEL, user_id=USER_ID),
)

from storage import vector_store, metadata_store
from scheduler import forgetting_curve as fc
from tools import add_knowledge, search_knowledge, manage_knowledge, reminder

# ─── 侧边栏导航 ───
st.sidebar.title("🧠 第二大脑")
st.sidebar.caption(f"已登录: {st.session_state.user_email}")

page = st.sidebar.radio(
    "导航",
    ["仪表盘", "知识问答", "导入笔记", "笔记管理", "复习提醒", "知识图谱", "学习路径", "知识广场", "设置"],
    index=0,
)

st.sidebar.divider()
stats_count = metadata_store.count(user_id=USER_ID)
st.sidebar.metric("知识库笔记数", stats_count)

if st.sidebar.button("退出登录"):
    st.session_state.user_id = None
    st.session_state.user_email = None
    if "agent" in st.session_state:
        del st.session_state.agent
    if "chat_history" in st.session_state:
        del st.session_state.chat_history
    st.rerun()


def tts_button(text):
    import json as _j
    safe = _j.dumps(text[:200], ensure_ascii=False)
    html = f"""
    <button onclick="speak({safe})" style="background:none;border:1px solid #ccc;border-radius:8px;padding:2px 10px;cursor:pointer;font-size:13px;margin-top:4px">🔊 朗读</button>
    <script>
    function speak(t) {{ var u = new SpeechSynthesisUtterance(t); u.lang = 'zh-CN'; speechSynthesis.speak(u); }}
    </script>
    """
    st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════
#  页面一：仪表盘
# ═══════════════════════════════════════════
if page == "仪表盘":
    import datetime
    hour = datetime.datetime.now().hour
    if hour < 6:
        greeting = "🌙 夜深了，还在学习真棒"
    elif hour < 9:
        greeting = "🌅 早上好！今天也是学习的好日子"
    elif hour < 12:
        greeting = "☀️ 上午好，保持专注哦"
    elif hour < 14:
        greeting = "🌤️ 中午好，休息一下再继续"
    elif hour < 18:
        greeting = "🌇 下午好，一起加油吧"
    else:
        greeting = "🌆 晚上好，今天有什么收获吗"

    st.title("🧠 第二大脑")
    st.markdown(f"### {greeting}")

    due = fc.get_notes_for_review(user_id=USER_ID)
    if due:
        st.info(f"💡 你有 **{len(due)}** 条知识需要复习啦，去「复习提醒」看看吧")

    c1, c2, c3, c4 = st.columns(4)
    all_notes = metadata_store.list_notes(user_id=USER_ID)
    total = len(all_notes)
    tags_set = set()
    for n in all_notes:
        tags_set.update(n.get("tags", []))
    high_imp = sum(1 for n in all_notes if n.get("importance") == "high")
    reminders = fc.get_notes_for_review(user_id=USER_ID)

    c1.metric("总笔记数", total)
    c2.metric("标签种类", len(tags_set))
    c3.metric("高重要度", high_imp)
    c4.metric("待复习", len(reminders))

    st.markdown("---")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("最近笔记")
        if all_notes:
            for note in all_notes[:8]:
                tags_str = " ".join([f"`{t}`" for t in note.get("tags", [])])
                imp = "🔴" if note.get("importance") == "high" else "🔵"
                with st.container():
                    st.markdown(f"{imp} **{note['id']}** — {note['preview']}")
                    if tags_str:
                        st.caption(tags_str)
        else:
            st.info("知识库还是空的，去「导入笔记」添加第一条吧！")

    with col_right:
        st.subheader("标签分布")
        if tags_set:
            tag_counts = {}
            for n in all_notes:
                for t in n.get("tags", []):
                    tag_counts[t] = tag_counts.get(t, 0) + 1
            sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            for tag, cnt in sorted_tags[:10]:
                st.markdown(f"**{tag}** `×{cnt}`")
                st.progress(min(cnt / max(tag_counts.values()), 1.0))
        else:
            st.caption("暂无标签数据")

# ═══════════════════════════════════════════
#  页面二：知识问答（对话）
# ═══════════════════════════════════════════
elif page == "知识问答":
    st.title("💬 知识问答")
    st.caption("和你的第二大脑对话，它会自动调用工具完成任务")
    st.caption("💡 可以闲聊、问知识、让我记东西、帮你复习")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "agent" not in st.session_state:
        from agent.core import SecondBrainAgent
        st.session_state.agent = SecondBrainAgent(user_id=USER_ID)

    for msg in st.session_state.chat_history:
        role = msg["role"]
        avatar = "🧑" if role == "user" else "🧠"
        with st.chat_message(role, avatar=avatar):
            st.markdown(msg["content"])
            if role == "assistant" and msg.get("content"):
                tts_button(msg["content"])

    user_input = st.chat_input("输入你的问题...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🧠"):
            with st.spinner("思考中..."):
                try:
                    response = st.session_state.agent.chat(user_input)
                except Exception as e:
                    response = f"出错了: {e}"
            st.markdown(response)
            tts_button(response)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": response}
        )

    with st.sidebar:
        if st.button("清空对话历史"):
            st.session_state.chat_history = []
            if "agent" in st.session_state:
                st.session_state.agent.memory.clear()
            st.rerun()

# ═══════════════════════════════════════════
#  页面三：导入笔记
# ═══════════════════════════════════════════
elif page == "导入笔记":
    st.title("📥 导入笔记")
    st.markdown("支持从**本地文件**、**直接输入**、**网页URL**、**多媒体**四种方式导入知识。")
    st.markdown("---")

    tab_file, tab_text, tab_url, tab_media = st.tabs(["本地文件", "手动输入", "网页抓取", "多媒体"])

    with tab_file:
        st.subheader("上传文件")
        st.caption("支持 .txt, .md 格式")
        uploaded_files = st.file_uploader(
            "选择文件",
            type=["txt", "md"],
            accept_multiple_files=True,
        )

        file_tags = st.text_input("文件标签（逗号分隔）", key="file_tags",
                                   placeholder="如：Python, 笔记, 课程")
        file_importance = st.selectbox("重要程度", ["normal", "high", "low"],
                                        key="file_imp")

        if uploaded_files and st.button("开始导入文件", type="primary"):
            tags = [t.strip() for t in file_tags.split(",") if t.strip()]
            success_count = 0
            for f in uploaded_files:
                content = f.read().decode("utf-8", errors="ignore")
                if content.strip():
                    result = json.loads(add_knowledge.execute({
                        "content": content,
                        "tags": tags if tags else ["文件导入"],
                        "importance": file_importance,
                    }, user_id=USER_ID))
                    if result.get("status") == "success":
                        success_count += 1
            st.success(f"成功导入 {success_count}/{len(uploaded_files)} 个文件！")

    with tab_text:
        st.subheader("手动输入笔记")
        note_content = st.text_area(
            "笔记内容",
            height=200,
            placeholder="在这里输入你想保存的知识内容...\n\n例如：TCP三次握手：SYN → SYN+ACK → ACK",
        )
        note_tags = st.text_input("标签（逗号分隔）", key="note_tags",
                                   placeholder="如：TCP, 网络, 面试")
        note_importance = st.selectbox("重要程度", ["normal", "high", "low"],
                                        key="note_imp")

        if st.button("保存笔记", type="primary") and note_content.strip():
            tags = [t.strip() for t in note_tags.split(",") if t.strip()]
            result = json.loads(add_knowledge.execute({
                "content": note_content,
                "tags": tags if tags else ["手动输入"],
                "importance": note_importance,
            }, user_id=USER_ID))
            if result.get("status") == "success":
                st.success(f"笔记已保存！ID: {result['note_id']}")
                st.balloons()
            else:
                st.error(result.get("error", "保存失败"))

    with tab_url:
        st.subheader("从网页导入知识")
        st.caption("输入文章URL，自动提取正文内容并保存到知识库")

        url_input = st.text_input(
            "网页URL",
            placeholder="https://example.com/article",
        )
        url_tags = st.text_input("标签（逗号分隔）", key="url_tags",
                                  placeholder="如：技术博客, 架构设计")

        if st.button("抓取并保存", type="primary") and url_input.strip():
            with st.spinner("正在抓取网页内容..."):
                try:
                    from tools.fetch_web import fetch_url
                    fetched = fetch_url(url_input)
                    st.session_state["fetched"] = fetched
                except Exception as e:
                    st.error(f"抓取失败: {e}")
                    st.stop()

        fetched = st.session_state.get("fetched")
        if fetched and fetched.get("content"):
            st.success(f"抓取成功！标题: {fetched.get('title', '无标题')}")
            st.caption(f"内容长度: {fetched['length']} 字符")

            with st.expander("预览内容", expanded=False):
                st.text(fetched["content"][:2000])

            tags = [t.strip() for t in url_tags.split(",") if t.strip()]
            if st.button("确认保存到知识库", type="primary"):
                with st.spinner("正在保存..."):
                    save_result = json.loads(add_knowledge.execute({
                        "content": f"[来源: {fetched.get('title', fetched['url'])}]\n\n{fetched['content']}",
                        "tags": tags if tags else ["网页收藏"],
                        "importance": "normal",
                    }, user_id=USER_ID))
                if save_result.get("note_id"):
                    st.success(f"已保存！ID: {save_result['note_id']}")
                    st.balloons()
                else:
                    st.error(f"保存失败: {save_result.get('error', '未知错误')}")

    with tab_media:
        st.subheader("上传图片 / 音频 / 视频")
        st.caption("文件直接存储到知识库，可随时查看和管理")

        media_files = st.file_uploader(
            "选择文件",
            type=["jpg", "jpeg", "png", "gif", "bmp", "webp",
                  "mp3", "wav", "ogg", "flac", "aac", "m4a",
                  "mp4", "avi", "mov", "mkv", "flv", "wmv", "webm"],
            accept_multiple_files=True,
            key="media_upload",
        )
        media_tags = st.text_input("标签（逗号分隔）", key="media_tags",
                                    placeholder="如：课程截图, 讲义录音")
        media_desc = st.text_input("描述（可选）", key="media_desc",
                                    placeholder="简单描述这个文件的内容")

        if media_files and st.button("上传并入库", type="primary", key="media_upload_btn"):
            from storage.file_store import save_file
            tags = [t.strip() for t in media_tags.split(",") if t.strip()]
            ok = 0
            for f in media_files:
                try:
                    save_file(
                        user_id=USER_ID,
                        file_name=f.name,
                        file_bytes=f.read(),
                        tags=tags if tags else ["多媒体"],
                        description=media_desc,
                    )
                    ok += 1
                except Exception as e:
                    st.error(f"{f.name} 上传失败: {e}")
            if ok:
                st.success(f"成功上传 {ok}/{len(media_files)} 个文件")
                st.balloons()

        st.markdown("---")
        st.subheader("已上传的文件")
        from storage.file_store import list_files, delete_file, count
        media_count = count(user_id=USER_ID)
        st.caption(f"共 {media_count} 个文件")
        type_filter = st.radio("类型", ["全部", "图片", "音频", "视频"],
                                horizontal=True, key="media_type_filter")
        type_map = {"全部": None, "图片": "image", "音频": "audio", "视频": "video"}
        files = list_files(user_id=USER_ID, media_type=type_map[type_filter])
        if files:
            for f in files:
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        icon = {"image": "🖼️", "audio": "🎵", "video": "🎬"}.get(f["media_type"], "📄")
                        st.markdown(f"**{icon} {f['original_name']}**")
                        st.caption(f"{f['media_type']} | {f['file_size']//1024}KB | 标签: {f.get('tags', [])}")
                        if f.get("description"):
                            st.caption(f"描述: {f['description']}")
                        if f["media_type"] == "image" and os.path.exists(f["file_path"]):
                            st.image(f["file_path"], width=300)
                        elif f["media_type"] == "audio" and os.path.exists(f["file_path"]):
                            st.audio(f["file_path"])
                        elif f["media_type"] == "video" and os.path.exists(f["file_path"]):
                            st.video(f["file_path"])
                    with c2:
                        if st.button("删除", key=f"del_{f['file_id']}"):
                            delete_file(f["file_id"], user_id=USER_ID)
                            st.success("已删除")
                            st.rerun()
        else:
            st.info("暂无文件")

# ═══════════════════════════════════════════
#  页面四：笔记管理
# ═══════════════════════════════════════════
elif page == "笔记管理":
    st.title("📚 笔记管理")
    st.markdown("---")

    all_notes = metadata_store.list_notes(user_id=USER_ID)

    col1, col2 = st.columns([3, 1])
    with col2:
        st.subheader("筛选")
        filter_tag = st.text_input("按标签筛选", placeholder="输入标签")
        filter_imp = st.multiselect("按重要度", ["high", "normal", "low"])
        sort_by = st.selectbox("排序", ["最新创建", "最近访问", "访问次数"])

    if filter_tag:
        all_notes = [n for n in all_notes if filter_tag in n.get("tags", [])]
    if filter_imp:
        all_notes = [n for n in all_notes if n.get("importance") in filter_imp]
    if sort_by == "最近访问":
        all_notes.sort(key=lambda x: x.get("last_accessed", 0), reverse=True)
    elif sort_by == "访问次数":
        all_notes.sort(key=lambda x: x.get("access_count", 0), reverse=True)

    with col1:
        st.subheader(f"共 {len(all_notes)} 条笔记")
        for note in all_notes:
            tags_str = " ".join([f"`{t}`" for t in note.get("tags", [])])
            imp_icon = {"high": "🔴", "normal": "🔵", "low": "⚪"}.get(
                note.get("importance", "normal"), "🔵"
            )

            with st.expander(f"{imp_icon} {note['preview'][:60]}"):
                st.markdown(f"**ID:** `{note['id']}`")
                st.markdown(f"**标签:** {tags_str or '无'}")
                st.markdown(f"**重要度:** {note.get('importance', 'normal')}")
                st.markdown(f"**创建时间:** {time.strftime('%Y-%m-%d %H:%M', time.localtime(note['created_at']))}")
                st.markdown(f"**访问次数:** {note.get('access_count', 0)}")

                retention = fc.calculate_retention(note["id"], user_id=USER_ID)
                st.progress(retention)
                st.caption(f"记忆保留率: {retention*100:.0f}%")

                from storage.vector_store import get_note_full_content
                full_content = get_note_full_content(note["id"], user_id=USER_ID)
                if full_content:
                    st.markdown("---")
                    st.markdown("**完整内容：**")
                    st.text_area("笔记内容", value=full_content, height=200,
                                 disabled=True, key=f"content_{note['id']}")
                else:
                    st.info("完整内容未找到（可能是旧数据，重新添加笔记即可）")

                if st.button(f"删除", key=f"del_{note['id']}"):
                    metadata_store.delete_note(note["id"], user_id=USER_ID)
                    st.warning(f"已删除 {note['id']}")
                    st.rerun()

# ═══════════════════════════════════════════
#  页面五：复习提醒
# ═══════════════════════════════════════════
elif page == "复习提醒":
    st.title("⏰ 复习提醒")
    st.markdown("基于**遗忘曲线算法**，智能追踪你的知识记忆状态。")
    st.markdown("---")

    tab_review, tab_curves = st.tabs(["待复习列表", "遗忘曲线分析"])

    with tab_review:
        reminders = fc.get_notes_for_review(threshold=0.6, user_id=USER_ID)

        if not reminders:
            st.success("🎉 目前没有需要复习的内容，继续保持！")
        else:
            st.warning(f"有 **{len(reminders)}** 条知识需要复习")

            for r in reminders:
                note = metadata_store.get_note(r["note_id"], user_id=USER_ID)
                preview = note["preview"] if note else "未知内容"
                tags = note.get("tags", []) if note else []

                urgency_color = {"紧急": "🔴", "重要": "🟡", "一般": "🟢"}.get(
                    r["urgency"], "⚪"
                )

                with st.container():
                    st.markdown(f"### {urgency_color} {r['urgency']} — {preview}")
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("记忆保留率", f"{r['retention']*100:.0f}%")
                    col_b.metric("距上次复习", f"{r['days_since_review']}天")
                    col_c.metric("已复习次数", r["review_count"])

                    st.progress(r["retention"])

                    if tags:
                        st.caption(" ".join([f"`{t}`" for t in tags]))

                    if st.button(f"标记已复习", key=f"review_{r['note_id']}"):
                        fc.record_access(r["note_id"], user_id=USER_ID)
                        st.success("已记录复习！保留率已更新。")
                        st.rerun()

    with tab_curves:
        st.subheader("遗忘曲线可视化")
        st.caption("每条笔记的遗忘衰减曲线，展示记忆保留率随时间变化趋势")

        import pandas as pd
        curves = fc.get_all_curves_data(user_id=USER_ID)

        if not curves:
            st.info("暂无遗忘曲线数据，请先添加笔记并浏览后查看。")
        else:
            st.markdown("#### 全部笔记遗忘曲线对比")
            chart_data = []
            for curve in curves:
                preview = curve["note_id"][:12]
                for pt in curve["points"]:
                    chart_data.append({
                        "天数": pt["day"],
                        "保留率": pt["retention"],
                        "笔记": preview,
                    })

            if chart_data:
                df_all = pd.DataFrame(chart_data)
                st.line_chart(
                    df_all.pivot(index="天数", columns="笔记", values="保留率"),
                    use_container_width=True,
                )

            st.markdown("---")

            st.markdown("#### 单条笔记遗忘曲线")
            note_options = [c["note_id"] for c in curves]
            selected_note = st.selectbox("选择笔记", note_options, format_func=lambda x: x[:20])

            if selected_note:
                curve = next((c for c in curves if c["note_id"] == selected_note), None)
                if curve:
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("当前保留率", f"{curve['current_retention']*100:.0f}%")
                    col2.metric("距上次复习", f"{curve['days_since']}天")
                    col3.metric("已复习次数", curve["access_count"])
                    col4.metric("稳定系数", curve["stability"])

                    chart_points = [{"day": p["day"], "保留率": p["retention"]} for p in curve["points"]]
                    st.line_chart(
                        pd.DataFrame(chart_points).set_index("day"),
                        use_container_width=True,
                    )

                    from storage.db import query_one as q1
                    note_rec = q1("SELECT review_dates FROM forgetting WHERE note_id = %s AND user_id = %s", (selected_note, USER_ID))
                    if note_rec:
                        review_dates = note_rec.get("review_dates") or []
                        if review_dates:
                            st.markdown("**历史复习时间点:**")
                            for rd in review_dates:
                                st.caption(f"📅 {time.strftime('%Y-%m-%d %H:%M', time.localtime(rd))}")

                    retention = curve["current_retention"]
                    if retention < 0.3:
                        st.error("⚠️ 记忆保留率极低，强烈建议立即复习！")
                    elif retention < 0.6:
                        st.warning("📌 记忆正在衰退，建议尽快复习。")
                    else:
                        st.success("✅ 记忆状态良好，继续保持。")

# ═══════════════════════════════════════════
#  页面六：知识图谱
# ═══════════════════════════════════════════
elif page == "知识图谱":
    st.title("🕸️ 知识图谱")
    st.markdown("基于 **LLM 实体抽取 + NetworkX** 构建真正的知识图谱，支持多跳推理关联发现。")
    st.markdown("---")

    from storage.graph import KnowledgeGraph
    from storage.extractor import extract_from_text
    from storage.reasoning import discover_cross_domain_links, find_related_concepts, get_importance_scores

    if "kg" not in st.session_state:
        st.session_state.kg = KnowledgeGraph(user_id=USER_ID)
    kg = st.session_state.kg

    tab_add, tab_viz, tab_reason, tab_analysis = st.tabs(["添加笔记", "图谱总览", "多跳推理", "节点分析"])

    with tab_add:
        st.subheader("输入笔记，自动抽取实体关系")
        note_content = st.text_area(
            "笔记内容",
            height=150,
            placeholder="例如：Redis是一个开源的内存数据结构存储系统，广泛用于缓存策略。在电商秒杀场景中，Redis可以解决高并发下的库存扣减问题。",
        )

        if st.button("提取并加入图谱", type="primary") and note_content.strip():
            with st.spinner("LLM 正在抽取实体关系..."):
                result = extract_from_text(note_content)

            entities = result.get("entities", [])
            relations = result.get("relations", [])

            if entities:
                st.success(f"抽取完成：{len(entities)} 个实体，{len(relations)} 条关系")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**实体**")
                    for e in entities:
                        st.markdown(f"- {e['name']} ({e['type']})")
                with col2:
                    st.markdown("**关系**")
                    for r in relations:
                        st.markdown(f"- {r['source']} →{r['relation']}→ {r['target']}")

                kg.add_entities(entities)
                kg.add_relations(relations)
                kg.save()
                st.rerun()
            else:
                st.warning("未抽取到实体，请尝试更详细的内容。")

    with tab_viz:
        if len(kg.graph.nodes) == 0:
            st.info("图谱为空，请先在「添加笔记」页面输入内容。")
        else:
            dot_lines = ["digraph KG {", "  rankdir=LR;", "  bgcolor=transparent;"]
            dot_lines.append('  node [shape=box, style="rounded,filled", fontname="Microsoft YaHei", fontsize=10];')
            dot_lines.append('  edge [fontname="Microsoft YaHei", fontsize=8, color="#666666"];')

            type_colors = {
                "技术": "#4ECDC4", "概念": "#FFE66D", "场景": "#FF6B6B",
                "工具": "#95E1D3", "框架": "#A8D8EA", "方法": "#DCD6F7",
            }
            for node, data in kg.graph.nodes(data=True):
                ntype = data.get("type", "未知")
                color = type_colors.get(ntype, "#CCCCCC")
                safe = node.replace('"', '\\"')
                dot_lines.append(f'  "{safe}" [label="{safe}\\n({ntype})", fillcolor="{color}"];')
            for u, v, data in kg.graph.edges(data=True):
                rel = data.get("relation", "")
                safe_u = u.replace('"', '\\"')
                safe_v = v.replace('"', '\\"')
                dot_lines.append(f'  "{safe_u}" -> "{safe_v}" [label="{rel}"];')
            dot_lines.append("}")
            st.graphviz_chart("\n".join(dot_lines), use_container_width=True)

            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            col1.metric("实体节点", len(kg.graph.nodes))
            col2.metric("关系边", len(kg.graph.edges))
            pr = kg.pagerank()
            top = max(pr.items(), key=lambda x: x[1])[0] if pr else "-"
            col3.metric("核心节点", top)

    with tab_reason:
        if len(kg.graph.nodes) < 2:
            st.info("需要至少 2 个实体才能推理。")
        else:
            tab_cross, tab_query = st.tabs(["跨领域关联发现", "指定节点查询"])

            with tab_cross:
                st.subheader("跨领域关联")
                st.caption("发现不同领域实体之间的多跳连接路径")
                if st.button("发现跨领域关联", type="primary", key="cross_btn"):
                    with st.spinner("正在计算..."):
                        links = discover_cross_domain_links(kg)
                    if not links:
                        st.info("未发现跨领域关联")
                    else:
                        st.success(f"发现 {len(links)} 条跨领域关联")
                        for link in links[:10]:
                            path_str = " → ".join(link["path"])
                            st.markdown(f"**{link['source']}** ({link['source_type']}) ↔ **{link['target']}** ({link['target_type']})")
                            st.caption(f"路径 ({link['hops']}跳): {path_str}")
                            for edge in link["edges"]:
                                st.caption(f"  {edge['from']} —[{edge['relation']}]→ {edge['to']}")
                            st.divider()

            with tab_query:
                st.subheader("指定节点查询")
                node_list = [n["name"] for n in kg.get_all_nodes()]
                selected = st.selectbox("选择起始节点", node_list)
                hops = st.slider("最大跳数", 1, 4, 2, key="hop_slider")
                if st.button("查询关联", type="primary", key="query_btn"):
                    with st.spinner("正在推理..."):
                        related = find_related_concepts(kg, selected, max_hops=hops)
                    if not related:
                        st.info("未找到跨领域关联")
                    else:
                        for r in related:
                            path_str = " → ".join(r["path"])
                            st.markdown(f"**{r['concept']}** ({r['type']}) — {r['hops']}跳")
                            st.caption(f"路径: {path_str}")

    with tab_analysis:
        if len(kg.graph.nodes) == 0:
            st.info("图谱为空。")
        else:
            scores = get_importance_scores(kg)
            import pandas as pd
            df = pd.DataFrame(scores)
            st.dataframe(df, use_container_width=True)
            st.markdown("---")
            st.subheader("PageRank 分布")
            st.bar_chart(df.set_index("name")["pagerank"])

# ═══════════════════════════════════════════
#  页面七：学习路径
# ═══════════════════════════════════════════
elif page == "学习路径":
    st.title("🎯 个性化学习路径")
    st.markdown("根据遗忘曲线和标签掌握度，智能推荐下一步学习方向。")
    st.markdown("---")

    from storage.learning_path import get_learning_path, get_weak_notes

    path_data = get_learning_path(user_id=USER_ID)

    c1, c2, c3 = st.columns(3)
    c1.metric("总笔记数", path_data["total_notes"])
    c2.metric("标签维度", path_data["total_tags"])
    c3.metric("整体保留率", f"{path_data['overall_retention']*100:.0f}%")

    st.markdown("---")

    recommendations = path_data["recommendations"]
    if not recommendations:
        st.info("数据不足，添加更多笔记后即可生成个性化学习路径。")
    else:
        st.subheader("学习建议")

        for rec in recommendations:
            tag = rec["tag"]
            reason = rec["reason"]
            urgency = rec["urgency"]
            total = rec["total_notes"]

            icon = {"high": "🔴", "medium": "🟡", "explore": "🟢"}.get(urgency, "⚪")
            label = {"high": "紧急复习", "medium": "建议复习", "explore": "拓展深入"}.get(urgency, "一般")

            with st.container():
                st.markdown(f"### {icon} **{tag}** — {label}")
                st.markdown(f"💡 {reason}")
                st.caption(f"涉及 {total} 条笔记")

                for n in rec["notes"]:
                    ret = n["retention"]
                    color = "🟢" if ret > 0.7 else ("🟡" if ret > 0.4 else "🔴")
                    st.markdown(f"{color} {n['preview']}  — 保留率 {ret*100:.0f}%")

                if urgency in ("high", "medium") and st.button(
                    f"开始复习 {tag}", key=f"start_review_{tag}"
                ):
                    fc.record_access(rec["notes"][0]["id"], user_id=USER_ID)
                    st.success(f"已记录对「{tag}」的复习，保留率已更新！")
                    st.rerun()

    st.markdown("---")
    st.subheader("最急需复习的笔记")
    weak_notes = get_weak_notes(5, user_id=USER_ID)
    if weak_notes:
        for wn in weak_notes:
            ret = wn["retention"]
            tags_str = " ".join([f"`{t}`" for t in wn["tags"]])
            st.markdown(
                f"🔴 **{wn['preview']}** — 保留率 {ret*100:.0f}%"
            )
            if tags_str:
                st.caption(tags_str)
    else:
        st.success("没有需要紧急复习的笔记，表现优秀！")

# ═══════════════════════════════════════════
#  页面八：知识广场
# ═══════════════════════════════════════════
elif page == "知识广场":
    st.title("🌐 知识广场")
    st.markdown("搜索网页，一键收藏到知识库")

    tab_search, tab收藏 = st.tabs(["在线搜索", "收藏网页"])

    with tab_search:
        search_query = st.text_input(
            "搜索",
            placeholder="输入关键词，回车在新窗口打开百度搜索...",
            key="kg_search",
            label_visibility="collapsed",
        )
        if search_query.strip():
            import urllib.parse
            baidu_url = f"https://www.baidu.com/s?wd={urllib.parse.quote(search_query)}"
            st.markdown(f"👉 [点击在新窗口打开百度搜索: {search_query}]({baidu_url})")

        st.markdown("---")
        st.markdown("**搜到好文章？粘贴链接一键入库：**")
        save_url = st.text_input("网页链接", placeholder="https://...", key="kg_save_url")
        save_tags = st.text_input("标签", value="网页收藏", key="kg_save_tags", placeholder="标签，逗号分隔")

        if st.button("收藏到知识库", type="primary", key="kg_save_btn"):
            if save_url.strip():
                tags = [t.strip() for t in save_tags.split(",") if t.strip()]
                with st.spinner("正在抓取网页并入库..."):
                    from tools.web_search import fetch_url_content
                    from tools.add_knowledge import execute as add_exec
                    try:
                        page_data = fetch_url_content(save_url)
                        full_content = f"[来源: {page_data['title'] or page_data['url']}]\n\n{page_data['content']}"
                        add_result = json.loads(add_exec({
                            "content": full_content,
                            "tags": tags,
                            "importance": "normal",
                        }, user_id=USER_ID))
                        if add_result.get("note_id"):
                            st.success(f"已收藏！{page_data['title']}（{add_result.get('chunks_stored', 0)} 个分块）")
                        else:
                            st.error(f"入库失败: {add_result.get('error', '未知错误')}")
                    except Exception as e:
                        st.error(f"抓取失败: {e}")
            else:
                st.warning("请输入网页链接")

    with tab收藏:
        st.markdown("直接输入网页地址，抓取正文保存到知识库")
        url2 = st.text_input("网页地址", placeholder="https://example.com/article", key="kg_tab2_url")
        tags2 = st.text_input("标签", value="网页收藏", key="kg_tab2_tags")
        imp2 = st.selectbox("重要度", ["normal", "high", "low"], key="kg_tab2_imp")
        if st.button("抓取并入库", type="primary", key="kg_tab2_btn"):
            if url2.strip():
                tags_list = [t.strip() for t in tags2.split(",") if t.strip()]
                with st.spinner("正在抓取..."):
                    from tools.web_search import fetch_url_content
                    from tools.add_knowledge import execute as add_exec
                    try:
                        data = fetch_url_content(url2)
                        full = f"[来源: {data['title'] or data['url']}]\n\n{data['content']}"
                        result = json.loads(add_exec({
                            "content": full,
                            "tags": tags_list,
                            "importance": imp2,
                        }, user_id=USER_ID))
                        if result.get("note_id"):
                            st.success(f"已入库！{data['title']}（{result.get('chunks_stored', 0)} 个分块）")
                        else:
                            st.error(f"入库失败: {result.get('error', '未知错误')}")
                    except Exception as e:
                        st.error(f"抓取失败: {e}")
            else:
                st.warning("请输入网页地址")

# ═══════════════════════════════════════════
#  页面九：设置
# ═══════════════════════════════════════════
elif page == "设置":
    st.title("⚙️ 设置")
    st.markdown("---")

    st.subheader("API 配置")
    from memory import long_term

    current_url = long_term.get_preference("api_base_url", config.OPENAI_BASE_URL, user_id=USER_ID)
    current_key = long_term.get_preference("api_key", config.OPENAI_API_KEY, user_id=USER_ID)
    current_model = long_term.get_preference("model_name", config.MODEL_NAME, user_id=USER_ID)
    current_embedding = long_term.get_preference("embedding_model", config.EMBEDDING_MODEL, user_id=USER_ID)

    new_url = st.text_input("API Base URL", value=current_url, key="api_url")
    if current_key and current_key != config.OPENAI_API_KEY:
        st.info("API Key 已配置（留空则保持不变）")
    else:
        st.warning("API Key 未配置，请输入")
    new_key = st.text_input("API Key", value="", type="password", key="api_key_input",
                            placeholder="输入新 Key 以更新，留空不修改")
    new_model = st.text_input("模型名称", value=current_model, key="model_name_input")
    new_embedding = st.text_input("Embedding 模型", value=current_embedding, key="embedding_input")

    if st.button("保存 API 配置", type="primary"):
        long_term.update_preference("api_base_url", new_url, user_id=USER_ID)
        if new_key:
            long_term.update_preference("api_key", new_key, user_id=USER_ID)
            current_key = new_key
        long_term.update_preference("model_name", new_model, user_id=USER_ID)
        long_term.update_preference("embedding_model", new_embedding, user_id=USER_ID)
        set_user_settings(USER_ID, api_key=current_key, base_url=new_url,
                          model_name=new_model, embedding_model=new_embedding)
        st.success("配置已保存并生效！")

    if st.button("重置为 .env 默认值"):
        for k in ["api_key", "api_base_url", "model_name", "embedding_model"]:
            long_term.delete_preference(k, user_id=USER_ID)
        _clients = __import__("agent.llm", fromlist=["_clients"])._clients
        _clients.pop(USER_ID, None)
        st.success("已重置，页面刷新后将使用 .env 中的配置")
        st.rerun()

    st.markdown("---")
    st.subheader("数据管理")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("清空知识库", type="primary"):
            st.warning("此操作不可恢复！")
            if st.button("确认清空", type="primary"):
                vector_store.delete_all(user_id=USER_ID)
                st.success("知识库已清空")
                st.rerun()

    with col2:
        if st.button("导出笔记为JSON"):
            notes = metadata_store.list_notes(user_id=USER_ID)
            st.download_button(
                "下载 JSON",
                data=json.dumps(notes, ensure_ascii=False, indent=2),
                file_name="knowledge_base_export.json",
                mime="application/json",
            )

    with col3:
        st.metric("向量库文档数", vector_store.count(user_id=USER_ID))
        st.metric("元数据笔记数", metadata_store.count(user_id=USER_ID))
