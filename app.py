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
        background: linear-gradient(135deg, #f5f0ff 0%, #e8e0ff 50%, #f0e8ff 100%);
    }
    .block-container {
        max-width: 100% !important;
        padding: 0 !important;
    }
    [data-testid="stHeader"], [data-testid="stToolbar"] { display: none; }
    [data-testid="stSidebar"] { display: none; }
    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 2rem;
    }
    .login-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 3rem 2.5rem;
        width: 100%;
        max-width: 460px;
        box-shadow: 0 20px 60px rgba(120, 80, 200, 0.15),
                    0 4px 16px rgba(120, 80, 200, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.6);
        position: relative;
        overflow: hidden;
    }
    .login-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #7c5cbf, #a78bfa, #7c5cbf);
    }
    .login-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    .login-subtitle {
        font-size: 0.95rem;
        color: #8888a0;
        text-align: center;
        margin-bottom: 2rem;
    }
    .mode-toggle {
        display: flex;
        background: #f4f0ff;
        border-radius: 14px;
        padding: 4px;
        margin-bottom: 2rem;
    }
    .mode-toggle button {
        flex: 1;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 0 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        background: transparent !important;
        color: #7c7c9a !important;
        transition: all 0.3s ease !important;
    }
    .mode-toggle button[kind="primary"],
    .mode-toggle button[data-testid="stBaseButton-primary"] {
        background: white !important;
        color: #7c5cbf !important;
        box-shadow: 0 2px 8px rgba(120, 80, 200, 0.15) !important;
    }
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        border: 1.5px solid #e8e4f0 !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
        background: #fafafe !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #a78bfa !important;
        box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.15) !important;
        background: white !important;
    }
    .stTextInput label {
        font-weight: 600 !important;
        color: #3a3a5c !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.02em;
    }
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #7c5cbf 0%, #9b7de8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 0.7rem 0 !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        width: 100% !important;
        letter-spacing: 0.04em;
        box-shadow: 0 4px 16px rgba(120, 92, 191, 0.35) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 24px rgba(120, 92, 191, 0.45) !important;
    }
    .auth-divider {
        text-align: center;
        color: #b0b0c8;
        font-size: 0.85rem;
        margin: 1.2rem 0;
    }
    .auth-switch {
        text-align: center;
        font-size: 0.9rem;
        color: #7c7c9a;
        margin-top: 1.5rem;
    }
    .auth-switch a, .auth-switch span.clickable {
        color: #7c5cbf;
        font-weight: 600;
        cursor: pointer;
        text-decoration: none;
    }
    .auth-switch a:hover, .auth-switch span.clickable:hover {
        color: #9b7de8;
        text-decoration: underline;
    }
    .decor-blob1 {
        position: fixed;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(167,139,250,0.2) 0%, transparent 70%);
        border-radius: 50%;
        top: -80px; left: -60px;
        z-index: 0;
        pointer-events: none;
    }
    .decor-blob2 {
        position: fixed;
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(120,92,191,0.12) 0%, transparent 70%);
        border-radius: 50%;
        bottom: -120px; right: -100px;
        z-index: 0;
        pointer-events: none;
    }
    .decor-ring {
        position: fixed;
        width: 180px; height: 180px;
        border: 3px solid rgba(167,139,250,0.15);
        border-radius: 50%;
        top: 15%; right: 8%;
        z-index: 0;
        pointer-events: none;
    }
    .decor-dot {
        position: fixed;
        width: 12px; height: 12px;
        background: rgba(167,139,250,0.3);
        border-radius: 50%;
        z-index: 0;
        pointer-events: none;
    }
    .decor-dot.d1 { top: 20%; left: 5%; }
    .decor-dot.d2 { top: 70%; right: 12%; width: 8px; height: 8px; }
    .decor-dot.d3 { bottom: 25%; left: 15%; width: 10px; height: 10px; }
    .stAlert { border-radius: 12px !important; }
    </style>
    <div class="decor-blob1"></div>
    <div class="decor-blob2"></div>
    <div class="decor-ring"></div>
    <div class="decor-dot d1"></div>
    <div class="decor-dot d2"></div>
    <div class="decor-dot d3"></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🧠 第二大脑</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">你的 AI 知识管理助手</div>', unsafe_allow_html=True)

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    col_l, col_toggle, col_r = st.columns([1, 2, 1])
    with col_toggle:
        c1, c2 = st.columns(2)
        with c1:
            login_btn = st.button("登录", key="mode_login", use_container_width=True,
                                  type="primary" if st.session_state.auth_mode == "login" else "secondary")
        with c2:
            register_btn = st.button("注册", key="mode_register", use_container_width=True,
                                     type="primary" if st.session_state.auth_mode == "register" else "secondary")

    if login_btn:
        st.session_state.auth_mode = "login"
        st.rerun()
    if register_btn:
        st.session_state.auth_mode = "register"
        st.rerun()

    st.markdown('<div style="height: 1.2rem;"></div>', unsafe_allow_html=True)

    if st.session_state.auth_mode == "login":
        login_email = st.text_input("邮箱", key="login_email", placeholder="请输入邮箱")
        login_pwd = st.text_input("密码", type="password", key="login_pwd", placeholder="请输入密码")
        st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
        if st.button("登 录", type="primary", key="btn_login", use_container_width=True):
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

        st.markdown("""
        <div class="auth-switch">
            还没有账号？
            <span class="clickable" onclick="
                window.parent.document.querySelectorAll('button')[1].click();
            ">立即注册</span>
        </div>
        """, unsafe_allow_html=True)

    else:
        reg_email = st.text_input("邮箱", key="reg_email", placeholder="请输入邮箱")
        reg_pwd = st.text_input("密码", type="password", key="reg_pwd", placeholder="请设置密码（至少6位）")
        reg_pwd2 = st.text_input("确认密码", type="password", key="reg_pwd2", placeholder="请再次输入密码")
        st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
        if st.button("注 册", type="primary", key="btn_register", use_container_width=True):
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

        st.markdown("""
        <div class="auth-switch">
            已有账号？
            <span class="clickable" onclick="
                window.parent.document.querySelectorAll('button')[0].click();
            ">返回登录</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)
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
    ["仪表盘", "知识问答", "导入笔记", "笔记管理", "复习提醒", "知识图谱", "学习路径", "设置"],
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
    st.markdown("支持从**本地文件**、**直接输入**、**网页URL**三种方式导入知识。")
    st.markdown("---")

    tab_file, tab_text, tab_url = st.tabs(["本地文件", "手动输入", "网页抓取"])

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
        st.session_state.kg = KnowledgeGraph()
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
#  页面八：设置
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
