"""
第二大脑 —— 图形化界面 (Streamlit)
启动命令: streamlit run app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import streamlit.components.v1 as components
import json
import html
import time
from pathlib import Path

st.set_page_config(
    page_title="第二大脑",
    layout="wide",
    initial_sidebar_state="expanded",
)

import config

from storage.db import query_one, execute
from storage.passwords import hash_password, verify_password
from storage.rate_limit import check as rate_check, reset as rate_reset

# ═══════════════════════════════════════════
#  登录 / 注册 —— 品牌落地页（腾讯官网风格）
# ═══════════════════════════════════════════
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

if st.session_state.user_id is None:
    from ui_login import (
        render_scaffold, render_hero, render_features, render_footer,
    )

    render_scaffold()

    hero_col, form_col = st.columns(
        [1.08, 0.72], gap="large", vertical_alignment="center"
    )

    with hero_col:
        render_hero()

    with form_col:
        st.markdown('<span id="tv-login"></span>', unsafe_allow_html=True)

        with st.container(key="tLoginCard"):
            st.markdown(
                '<div class="tc-eyebrow">Welcome Back</div>'
                '<div class="tc-title">进入你的知识空间</div>'
                '<div class="tc-sub">登录后继续你的笔记、图谱与复习计划</div>',
                unsafe_allow_html=True,
            )

            with st.container(key="tSwitch"):
                _sw_l, _sw_r = st.columns(2, gap="small")
                with _sw_l:
                    if st.button(
                        "登录",
                        key="mode_login",
                        use_container_width=True,
                        type="primary" if st.session_state.get("auth_mode", "login") == "login" else "secondary",
                    ):
                        st.session_state.auth_mode = "login"
                        st.rerun()
                with _sw_r:
                    if st.button(
                        "注册",
                        key="mode_register",
                        use_container_width=True,
                        type="primary" if st.session_state.get("auth_mode") == "register" else "secondary",
                    ):
                        st.session_state.auth_mode = "register"
                        st.rerun()

            if st.session_state.get("auth_mode", "login") == "login":
                with st.form("login_form", clear_on_submit=False):
                    login_email = st.text_input(
                        "邮箱", key="login_email", placeholder="邮箱地址",
                        label_visibility="collapsed",
                    )
                    login_pwd = st.text_input(
                        "密码", type="password", key="login_pwd", placeholder="密码",
                        label_visibility="collapsed",
                    )
                    do_login = st.form_submit_button(
                        "登  录", type="primary", use_container_width=True
                    )
                if do_login:
                    _email_key = login_email.strip().lower()
                    if not _email_key or not login_pwd:
                        st.error("请输入邮箱和密码")
                    else:
                        # 限流：同一邮箱 5 分钟内最多 5 次
                        allowed, wait_s = rate_check(f"login:{_email_key}", limit=5, window=300)
                        if not allowed:
                            st.error(f"尝试次数过多，请 {wait_s} 秒后再试")
                        else:
                            user = query_one(
                                "SELECT id, email, password_hash FROM users "
                                "WHERE lower(email) = lower(%s)",
                                (_email_key,),
                            )
                            passed, needs_rehash = (False, False)
                            if user:
                                passed, needs_rehash = verify_password(
                                    login_pwd, user.get("password_hash")
                                )
                            if passed:
                                rate_reset(f"login:{_email_key}")
                                # 老账号是无盐 sha256，登录成功后静默升级为 bcrypt
                                if needs_rehash:
                                    try:
                                        execute(
                                            "UPDATE users SET password_hash = %s WHERE id = %s",
                                            (hash_password(login_pwd), user["id"]),
                                        )
                                    except Exception:
                                        pass  # 升级失败不影响本次登录
                                st.session_state.user_id = str(user["id"])
                                st.session_state.user_email = user["email"]
                                st.session_state["_enter_effect"] = "book"  # 登录进入：翻开笔记本
                                st.rerun()
                            else:
                                st.error("邮箱或密码错误")

            else:
                with st.form("register_form", clear_on_submit=False):
                    reg_email = st.text_input(
                        "邮箱", key="reg_email", placeholder="邮箱地址",
                        label_visibility="collapsed",
                    )
                    reg_pwd = st.text_input(
                        "密码", type="password", key="reg_pwd",
                        placeholder="设置密码（至少 6 位）",
                        label_visibility="collapsed",
                    )
                    reg_pwd2 = st.text_input(
                        "确认密码", type="password", key="reg_pwd2",
                        placeholder="再次输入密码",
                        label_visibility="collapsed",
                    )
                    do_register = st.form_submit_button(
                        "创建账号", type="primary", use_container_width=True
                    )
                if do_register:
                    _email = reg_email.strip()
                    if not _email or not reg_pwd:
                        st.error("请输入邮箱和密码")
                    elif "@" not in _email or "." not in _email.split("@")[-1]:
                        st.error("请输入有效的邮箱地址")
                    elif len(reg_pwd) < 6:
                        st.error("密码至少需要 6 位")
                    elif reg_pwd != reg_pwd2:
                        st.error("两次密码不一致")
                    else:
                        existing = query_one(
                            "SELECT id FROM users WHERE lower(email) = lower(%s)", (_email,)
                        )
                        if existing:
                            st.error("该邮箱已注册，请直接登录")
                        else:
                            execute(
                                "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
                                (_email, hash_password(reg_pwd)),
                            )
                            st.session_state.auth_mode = "login"
                            st.rerun()

            st.markdown(
                '<div class="tc-terms">登录即表示同意 '
                '<a href="#tv-login">服务条款</a> 与 <a href="#tv-login">隐私政策</a></div>',
                unsafe_allow_html=True,
            )

    render_features()
    render_footer()

    # 未登录：清理可能残留的侧边栏切换按钮（退出登录后）
    components.html(
        """
<script>
(function(){
  var d = window.parent.document;
  var e = d.getElementById('sbToggle'); if (e) e.remove();
})();
</script>
""",
        height=0,
    )

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

from storage import vector_store, metadata_store, notes_service
from scheduler import forgetting_curve as fc
from tools import add_knowledge, search_knowledge, manage_knowledge, reminder
from ui_theme import apply_main_theme, page_header, render_sticky, notebook_line, enter_effect

# ── 全局手帐皮肤（含侧边栏牛皮纸 + 全部控件）──
apply_main_theme()

# ── 侧边栏切换按钮：用 components.html 注入到父页面（固定左上角，点击原生 >>>/<<<）──
# 说明：st.markdown 的 unsafe_allow_html 会过滤掉 onclick，故必须走组件 iframe。
# 每次 rerun 都移除并重建，避免旧 iframe realm 销毁后处理器失效。
components.html(
    """
<script>
(function(){
  var d = window.parent.document;
  var old = d.getElementById('sbToggle');
  if (old) old.remove();
  var el = d.createElement('div');
  el.id = 'sbToggle';
  el.className = 'sb-toggle';
  el.setAttribute('role','button');
  el.setAttribute('aria-label','展开或收起侧边栏');
  el.innerHTML = '<span class="sb-ico">\\u2630</span><span>菜单</span>';
  el.onclick = function(){
    var sb = d.querySelector('[data-testid=stSidebar]');
    var exp = sb && sb.getAttribute('aria-expanded') === 'true';
    var b = exp ? d.querySelector('[data-testid=stSidebarCollapseButton] button')
                : d.querySelector('button[data-testid=stExpandSidebarButton]');
    if (b) b.click();
  };
  d.body.appendChild(el);
})();
</script>
""",
    height=0,
)

# ── 主动推送①：登录后若有待复习笔记，右上角 toast 弹出提醒（每会话仅一次）──
if not st.session_state.get("_due_toast_shown"):
    _due = fc.get_notes_for_review(user_id=USER_ID)
    if _due:
        st.toast(f"⏰ 有 {len(_due)} 条旧笔记等你复习，去「复习提醒」看看吧！", icon="⏰")
        st.session_state["_last_review_push"] = time.time()
    st.session_state["_due_toast_shown"] = True


# ── 主动推送②：持续/定时复习推送（每 5 分钟检查一次，30 分钟内不重复打扰）──
@st.fragment(run_every="5m")
def _review_pusher():
    try:
        _due = fc.get_notes_for_review(user_id=USER_ID)
    except Exception:
        return
    if not _due:
        return
    _now = time.time()
    if _now - st.session_state.get("_last_review_push", 0) < 1800:
        return
    st.session_state["_last_review_push"] = _now
    _urgent = sum(1 for d in _due if d.get("urgency") == "紧急")
    _msg = f"⏰ 还有 {len(_due)} 条笔记等待复习"
    if _urgent:
        _msg += f"（其中 {_urgent} 条紧急）"
    st.toast(_msg, icon="⏰")


_review_pusher()


# ── 主动推送③：切换模块时的数据驱动智能提醒（每模块每会话只提示一次）──
def _page_tip(page: str):
    _shown = st.session_state.setdefault("_page_tips_shown", [])
    if page in _shown:
        return
    _shown.append(page)
    try:
        if page == "仪表盘":
            _due = fc.get_notes_for_review(user_id=USER_ID)
            if _due:
                st.toast(f"📌 有 {len(_due)} 条笔记到复习时间了，去「复习提醒」看看", icon="📌")
        elif page == "复习提醒":
            _due = fc.get_notes_for_review(user_id=USER_ID)
            if _due:
                _urgent = sum(1 for d in _due if d.get("urgency") == "紧急")
                _msg = f"⏰ 待复习 {len(_due)} 条"
                if _urgent:
                    _msg += f"，其中 {_urgent} 条很紧急"
                st.toast(_msg, icon="⏰")
        elif page == "笔记管理":
            _total = metadata_store.count(user_id=USER_ID)
            if _total == 0:
                st.toast("📝 还没有笔记，去「导入笔记」添加第一条吧", icon="📝")
            else:
                st.toast(f"📚 知识库共 {_total} 条笔记", icon="📚")
        elif page == "知识广场":
            st.toast("🌐 输入关键词即可内嵌浏览并一键收藏", icon="🌐")
        elif page == "知识问答":
            st.toast("💬 可以直接问我你记录过的知识", icon="💬")
        elif page == "知识图谱":
            st.toast("🕸️ 看看你的知识点之间有哪些隐藏联系", icon="🕸️")
        elif page == "学习路径":
            st.toast("🧭 这里会按复习曲线为你规划学习顺序", icon="🧭")
        elif page == "设置":
            st.toast("⚙️ 配置 API Key 后即可使用 AI 问答", icon="⚙️")
    except Exception:
        pass

# ─── 侧边栏导航 ───
st.sidebar.markdown("""
<div style="position:relative;text-align:center;padding:.6rem .4rem .2rem">
  <div style="font-size:2rem">🧠</div>
  <div style="font-family:'Ma Shan Zheng',cursive;font-size:1.4rem;color:var(--ink)">第二大脑</div>
  <div style="font-family:'Caveat',cursive;color:var(--ink-soft);font-size:.95rem">翻开你的知识笔记本 ✎</div>
</div>
""", unsafe_allow_html=True)
st.sidebar.caption(f"已登录: {st.session_state.user_email}")

# 侧边栏：按「记录 → 整理 → 使用」排序，显示名与内部 key 解耦
# （key 保持原样，页面分支不用动；只改 label 就换了个说法）
PAGE_LABELS = {
    "仪表盘": "📊 仪表盘",
    "导入笔记": "➕ 添加内容",
    "笔记管理": "📚 我的笔记",
    "知识问答": "💬 智能问答",
    "复习提醒": "🔁 复习提醒",
    "学习路径": "🧭 学习路径",
    "知识图谱": "🕸️ 知识图谱",
    "知识广场": "🌐 发现",
    "设置": "⚙️ 设置",
}

page = st.sidebar.radio(
    "导航",
    list(PAGE_LABELS),
    index=0,
    format_func=lambda p: PAGE_LABELS.get(p, p),
)

# 检测模块切换 → 触发数据驱动提醒（首次进入不弹，避免与登录提醒重复）
_prev_page = st.session_state.get("_prev_page")
if _prev_page != page:
    st.session_state["_prev_page"] = page
    if _prev_page is not None:
        st.session_state["_enter_effect"] = "page"  # 切换模块：主内容淡入上浮
        st.session_state["_review_open"] = None     # 离开页面时收起复习面板
        st.session_state["_reminder_open"] = None
        _page_tip(page)

# 执行「进入」动效（登录=翻开笔记本 / 切页=淡入上浮），一次性消费
_enter = st.session_state.get("_enter_effect")
if _enter:
    del st.session_state["_enter_effect"]
    enter_effect(_enter)

st.sidebar.divider()
stats_count = metadata_store.count(user_id=USER_ID)
st.sidebar.metric("知识库笔记数", stats_count)

if st.sidebar.button("退出登录", use_container_width=True):
    st.session_state.user_id = None
    st.session_state.user_email = None
    if "agent" in st.session_state:
        del st.session_state.agent
    if "chat_history" in st.session_state:
        del st.session_state.chat_history
    st.session_state["_due_toast_shown"] = False
    st.session_state["_last_review_push"] = 0
    st.session_state["_page_tips_shown"] = []
    st.session_state["_prev_page"] = None
    st.rerun()


def tts_button(text):
    """语音朗读按钮。

    st.markdown 会过滤掉 onclick / <script> 并把源码当纯文本显示，
    因此必须用 components.html（iframe 内允许执行脚本）承载 Web Speech API。
    """
    safe = json.dumps((text or "").strip(), ensure_ascii=False)
    html = f"""
    <style>html,body{{margin:0;padding:0;background:transparent}}</style>
    <button id="tts-btn" onclick="ttsToggle()"
      style="background:#fbf5e9;border:1px solid #e9dcc3;border-radius:8px;
             padding:3px 12px;cursor:pointer;font-size:13px;color:#7a6f5e;
             font-family:'ZCOOL XiaoWei',serif;">🔊 朗读</button>
    <script>
    var TTS_TEXT = {safe};
    var btn = document.getElementById('tts-btn');
    function ttsToggle() {{
      var synth = window.speechSynthesis;
      if (!synth) {{ btn.textContent = '当前浏览器不支持朗读'; return; }}
      if (synth.speaking || synth.pending) {{
        synth.cancel(); btn.textContent = '🔊 朗读'; return;
      }}
      var u = new SpeechSynthesisUtterance(TTS_TEXT);
      u.lang = 'zh-CN';
      u.rate = 1.0;
      u.onend = function() {{ btn.textContent = '🔊 朗读'; }};
      u.onerror = function() {{ btn.textContent = '🔊 朗读'; }};
      btn.textContent = '⏹ 停止';
      synth.speak(u);
    }}
    </script>
    """
    components.html(html, height=42, scrolling=False)


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

    st.markdown("""
    <div style="display:flex;align-items:baseline;gap:.8rem;flex-wrap:wrap;margin:.2rem 0 .2rem">
      <span style="font-size:1.9rem">🧠</span>
      <span class="pp-title" style="font-size:1.9rem">第二大脑</span>
      <span style="font-family:'Caveat',cursive;color:var(--ink-soft);font-size:1.05rem">%s</span>
    </div>
    """ % greeting, unsafe_allow_html=True)

    due = fc.get_notes_for_review(user_id=USER_ID)
    if due:
        render_sticky(f"⏰ 有 {len(due)} 条旧笔记在等你复习，去「复习提醒」看看吧！", color="y", angle=-0.5)

    c1, c2, c3, c4 = st.columns(4)
    all_notes = metadata_store.list_notes(user_id=USER_ID)
    total = len(all_notes)
    tags_set = set()
    for n in all_notes:
        tags_set.update(n.get("tags", []))
    high_imp = sum(1 for n in all_notes if n.get("importance") == "high")
    reminders = fc.get_notes_for_review(user_id=USER_ID)
    _today0 = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    _notes_today = sum(1 for n in all_notes if (n.get("created_at") or 0) >= _today0)
    _tags_today = set()
    for _n in all_notes:
        if (_n.get("created_at") or 0) >= _today0:
            _tags_today.update(_n.get("tags", []))

    c1.metric("📝 总笔记数", total,
              delta=f"+{_notes_today} 今天", delta_color="normal" if _notes_today else "off")
    c2.metric("🏷️ 标签种类", len(tags_set),
              delta=f"+{len(_tags_today)} 今天", delta_color="normal" if _tags_today else "off")
    c3.metric("⭐ 高重要度", high_imp,
              delta=f"占比 {round(high_imp / total * 100)}%" if total else "暂无", delta_color="off")
    c4.metric("📖 待复习", len(reminders),
              delta="需要处理" if reminders else "已清空", delta_color="off")

    notebook_line()

    def _rel_time(ts):
        if not ts:
            return ""
        d = time.time() - ts
        if d < 60:
            return "刚刚"
        if d < 3600:
            return f"{int(d // 60)} 分钟前"
        if d < 86400:
            return f"{int(d // 3600)} 小时前"
        if d < 172800:
            return "昨天"
        return f"{int(d // 86400)} 天前"

    def _note_icon(note):
        src = (note.get("source") or "").lower()
        tags = [str(t).lower() for t in (note.get("tags") or [])]
        if src == "web":
            return "🌐"
        if src == "api":
            return "🔌"
        if any("python" in t for t in tags):
            return "🐍"
        if any(("数据" in t) or ("sql" in t) or ("mysql" in t) for t in tags):
            return "🗄️"
        return "📄"

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:baseline;margin:.3rem 0 .4rem">
          <h3 style="font-family:'Ma Shan Zheng',cursive;color:var(--ink);margin:0">📄 最近记的</h3>
          <span style="font-family:'Caveat',cursive;color:var(--pen)">翻到「笔记管理」→</span>
        </div>
        """, unsafe_allow_html=True)
        if all_notes:
            for note in all_notes[:8]:
                tags_str = " ".join([f"`{t}`" for t in note.get("tags", [])])
                imp = "🔴" if note.get("importance") == "high" else "🔵"
                icon = _note_icon(note)
                when = _rel_time(note.get("created_at"))
                with st.container():
                    st.markdown('<span class="hb-card hb-lines"></span>', unsafe_allow_html=True)
                    _t = (note.get("title") or note.get("preview") or "未命名笔记").strip()
                    st.markdown(f"{imp} {icon} **{_t[:50]}**")
                    _meta = "　".join(x for x in [tags_str, when] if x)
                    if _meta:
                        st.caption(_meta)
        else:
            st.info("知识库还是空的，去「导入笔记」添加第一条吧！")

    with col_right:
        st.markdown("""
        <h3 style="font-family:'Ma Shan Zheng',cursive;color:var(--ink);margin:0 0 .5rem">🎨 标签热度</h3>
        """, unsafe_allow_html=True)
        with st.container():
            st.markdown('<span class="hb-card"></span>', unsafe_allow_html=True)
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
    page_header("💬", "和你的笔记聊天", "AI 会翻开你的笔记本帮你找答案")
    render_sticky("可以闲聊、问知识、让我记东西、帮你复习～", color="g", angle=0.5)

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
#  页面三：添加内容（标题 + 正文 + 附件）
# ═══════════════════════════════════════════
elif page == "导入笔记":
    from ui_add_note import render_add_note

    render_add_note(USER_ID)

# ═══════════════════════════════════════════
#  页面四：笔记管理
# ═══════════════════════════════════════════
elif page == "笔记管理":
    page_header("📚", "笔记整理簿", "每一页都是你的积累，翻看、复习、整理")
    notebook_line()

    all_notes = metadata_store.list_notes(user_id=USER_ID)

    col1, col2 = st.columns([3, 1])
    with col2:
        with st.container():
            st.markdown('<span class="hb-filter"></span>', unsafe_allow_html=True)
            st.markdown(
                "<h3 style=\"font-family:'Ma Shan Zheng',cursive;color:var(--ink);"
                "margin:0 0 .4rem\">🔍 筛选</h3>",
                unsafe_allow_html=True,
            )
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
        if not all_notes:
            st.info("还没有笔记。去左侧「➕ 添加内容」记第一条吧。")

        try:
            from storage import file_store as _fs
            _att_counts = _fs.count_files_for_notes([n["id"] for n in all_notes], USER_ID)
        except Exception:
            _att_counts = {}

        for note in all_notes:
            tags_str = " ".join([f"`{t}`" for t in note.get("tags", [])])
            imp_icon = {"high": "🔴", "normal": "🔵", "low": "⚪"}.get(
                note.get("importance", "normal"), "🔵"
            )
            _title = (note.get("title") or note.get("preview") or "未命名笔记").strip()
            _n_att = _att_counts.get(note["id"], 0)
            _badge = f" · 📎{_n_att}" if _n_att else ""

            with st.expander(f"{imp_icon} {_title[:60]}{_badge}"):
                st.markdown(f"**ID:** `{note['id']}`")
                st.markdown(f"**标签:** {tags_str or '无'}")
                st.markdown(f"**重要度:** {note.get('importance', 'normal')}")
                st.markdown(f"**创建时间:** {time.strftime('%Y-%m-%d %H:%M', time.localtime(note['created_at']))}")

                retention = fc.calculate_retention(note["id"], user_id=USER_ID)
                st.progress(retention)
                st.caption(f"记忆保留率: {retention*100:.0f}%")

                detail = notes_service.get_note_detail(note["id"], USER_ID) or {}
                body = (detail.get("body") or "").strip()
                if body:
                    st.markdown("---")
                    st.markdown("**正文：**")
                    st.markdown(
                        f'<div class="note-full-content">{html.escape(body)}</div>',
                        unsafe_allow_html=True,
                    )
                elif not _n_att:
                    st.info("这条笔记没有正文（可能是旧数据，重新添加即可）")

                files = detail.get("files") or []
                if files:
                    st.markdown("**附件：**")
                    _cols = st.columns(min(3, len(files)))
                    for _i, _f in enumerate(files):
                        _path = _f.get("file_path") or ""
                        with _cols[_i % len(_cols)]:
                            if _f.get("media_type") == "image" and os.path.exists(_path):
                                st.image(_path, use_container_width=True)
                            elif _f.get("media_type") == "audio" and os.path.exists(_path):
                                st.audio(_path)
                            elif _f.get("media_type") == "video" and os.path.exists(_path):
                                st.video(_path)
                            else:
                                st.markdown(f"📄 `{_f.get('original_name', '文件')}`")
                            st.caption(_f.get("original_name", ""))

                if st.button("删除", key=f"del_{note['id']}"):
                    notes_service.delete_note(note["id"], USER_ID)
                    st.rerun()

# ═══════════════════════════════════════════
#  页面五：复习提醒
# ═══════════════════════════════════════════
elif page == "复习提醒":
    page_header("⏰", "复习提醒", "基于遗忘曲线算法，智能追踪你的知识记忆状态")
    notebook_line()

    _done = st.session_state.get("_reminder_done")
    if _done:
        st.success(_done)
        st.session_state["_reminder_done"] = None

    tab_review, tab_curves = st.tabs(["待复习列表", "遗忘曲线分析"])

    with tab_review:
        reminders = fc.get_notes_for_review(threshold=0.6, user_id=USER_ID)

        if not reminders:
            st.success("🎉 目前没有需要复习的内容，继续保持！")
        else:
            st.warning(f"有 **{len(reminders)}** 条知识需要复习")

            for r in reminders:
                note = metadata_store.get_note(r["note_id"], user_id=USER_ID)
                preview = (
                    (note.get("title") or note.get("preview") or "").strip() if note else ""
                ) or "未知内容"
                tags = note.get("tags", []) if note else []

                urgency_color = {"紧急": "🔴", "重要": "🟡", "一般": "🟢"}.get(
                    r["urgency"], "⚪"
                )

                with st.container():
                    st.markdown('<span class="hb-card"></span>', unsafe_allow_html=True)
                    st.markdown(f"### {urgency_color} {r['urgency']} — {preview}")
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("记忆保留率", f"{r['retention']*100:.0f}%")
                    col_b.metric("距上次复习", f"{r['days_since_review']}天")
                    col_c.metric("已复习次数", r["review_count"])

                    st.progress(r["retention"])

                    if tags:
                        st.caption(" ".join([f"`{t}`" for t in tags]))

                    _open = st.session_state.get("_reminder_open") == r["note_id"]
                    if not _open and st.button("开始复习", key=f"review_{r['note_id']}"):
                        st.session_state["_reminder_open"] = r["note_id"]
                        _open = True  # 同一次运行内直接展开，避免额外 rerun 造成滚动跳位
                    if _open:
                        with st.container():
                            st.markdown('<span class="hb-flip"></span>', unsafe_allow_html=True)
                            st.markdown("#### 📖 复习中")
                            _full = vector_store.get_note_full_content(
                                r["note_id"], user_id=USER_ID
                            ) or preview
                            st.markdown(
                                f'<div class="note-full-content">{html.escape(_full)}</div>',
                                unsafe_allow_html=True,
                            )
                            _done_col, _cancel_col = st.columns(2)
                            if _done_col.button(
                                "✅ 复习完成", key=f"done_{r['note_id']}",
                                type="primary", use_container_width=True,
                            ):
                                fc.record_access(r["note_id"], user_id=USER_ID)
                                st.session_state["_reminder_open"] = None
                                st.session_state["_reminder_done"] = "✅ 已完成复习，保留率已更新！"
                                st.rerun()
                            if _cancel_col.button(
                                "取消", key=f"cancel_{r['note_id']}", use_container_width=True
                            ):
                                st.session_state["_reminder_open"] = None
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
    page_header("🕸️", "知识图谱", "LLM 实体抽取 + NetworkX，支持多跳推理关联发现")
    notebook_line()

    from storage.graph import KnowledgeGraph
    from storage.extractor import extract_from_text
    from storage.reasoning import discover_cross_domain_links, find_related_concepts, get_importance_scores
    import storage.graph_views as gv

    if "kg" not in st.session_state:
        st.session_state.kg = KnowledgeGraph(user_id=USER_ID)
    kg = st.session_state.kg
    # 关键：每次进入/重跑本页都从磁盘重载图谱，
    # 否则「导入笔记」页新增的实体无法在图谱中看到（缓存对象陈旧）
    kg.load()

    if "kg_selected_notes" not in st.session_state:
        st.session_state.kg_selected_notes = []
    if "kg_include_legacy" not in st.session_state:
        st.session_state.kg_include_legacy = False

    all_notes = metadata_store.list_notes(user_id=USER_ID)
    note_tags = {n["id"]: (n.get("tags") or []) for n in all_notes}

    def current_kg():
        """返回当前生效的图谱视图：勾选了笔记 → 子图；未勾选 → 全图"""
        selected = st.session_state.get("kg_selected_notes", [])
        include_legacy = st.session_state.get("kg_include_legacy", False)
        if selected:
            return kg.build_subgraph(selected, include_unattributed=include_legacy)
        return kg

    # ── 图谱架构选择（单选：一次只看一种结构）──
    _archs = gv.list_architectures()
    _arch_ids = [a["id"] for a in _archs]
    _arch_name = {a["id"]: a["name"] for a in _archs}
    _arch_desc = {a["id"]: a["desc"] for a in _archs}
    _kg_view = current_kg()

    _c1, _c2, _c3 = st.columns([2, 1, 1])
    with _c1:
        _sel_arch = st.selectbox(
            "🧩 图谱架构（选择你实际需要的结构）",
            _arch_ids, format_func=lambda x: _arch_name[x], key="kg_arch",
        )
    with _c2:
        _center = None
        if _sel_arch == "radial":
            _names = [n["name"] for n in _kg_view.get_all_nodes()]
            if _names:
                _center = st.selectbox("中心节点", _names, key="kg_radial_center")
    with _c3:
        st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
        _hide_iso = st.checkbox("隐藏无连线的孤立节点", key="kg_hide_isolated",
                                help="只显示彼此有关系的节点，隐藏没有连线的孤立实体。")
    st.caption(f"📐 {_arch_desc[_sel_arch]}")
    view = gv.build_view(_kg_view, _sel_arch, center=_center, note_tags=note_tags,
                         hide_isolated=_hide_iso)

    tab_add, tab_pick, tab_viz, tab_reason, tab_analysis = st.tabs(["添加笔记", "选择笔记", "图谱总览", "多跳推理", "节点分析"])

    with tab_add:
        st.subheader("输入笔记，自动抽取实体关系")
        note_content = st.text_area(
            "笔记内容",
            height=150,
            placeholder="例如：Redis是一个开源的内存数据结构存储系统，广泛用于缓存策略。在电商秒杀场景中，Redis可以解决高并发下的库存扣减问题。",
        )

        link_options = {
            n["id"]: (n["preview"][:30] + "…" if len(n["preview"]) > 30 else n["preview"])
            for n in all_notes
        }
        link_note = st.selectbox(
            "关联到已有笔记（可选，标注图谱数据来源）",
            ["（不关联）"] + list(link_options.keys()),
            format_func=lambda x: x if x == "（不关联）" else f"{x} · {link_options[x]}",
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

                linked_id = None if link_note == "（不关联）" else link_note
                kg.add_entities(entities, note_id=linked_id)
                kg.add_relations(relations, note_id=linked_id)
                kg.save()
                st.rerun()
            else:
                st.warning("未抽取到实体，请尝试更详细的内容。")

        # ── 补抽缺失的笔记实体 ──
        st.markdown("---")
        st.subheader("🩹 补抽缺失的笔记实体")
        st.caption("有些笔记可能因模型输出异常而没抽到实体。这里可以找出这些笔记并重新抽取。")
        _graph_note_ids = set()
        for _nd in kg.get_all_nodes():
            _graph_note_ids.update(_nd.get("notes") or [])
        _missing = [n for n in all_notes if n["id"] not in _graph_note_ids]

        if st.session_state.get("kg_reextract_summary"):
            st.success(st.session_state["kg_reextract_summary"])
            with st.expander("上次补抽明细", expanded=False):
                for _l in st.session_state.get("kg_reextract_log", []):
                    st.caption(_l)

        if not all_notes:
            st.caption("暂无笔记。")
        elif not _missing:
            st.success("所有笔记都已在图谱中，无缺失。")
        else:
            st.info(f"发现 **{len(_missing)}** 条笔记在图谱中没有实体。")
            if st.button(f"🔁 为这 {len(_missing)} 条笔记补抽实体", type="primary", key="kg_reextract"):
                from storage.vector_store import get_note_full_content
                kg.load()  # 写前重载最新图谱，避免覆盖其它进程写入
                _ok, _empty, _fail = 0, 0, 0
                _logs = []
                _prog = st.progress(0.0)
                for _i, _n in enumerate(_missing, 1):
                    _full = (get_note_full_content(_n["id"], user_id=USER_ID) or "").strip()
                    _content = _full or (_n.get("preview", "") or "").strip()
                    _src = "全文" if _full else "摘要"
                    if len(_content) < 5:
                        _empty += 1
                        _logs.append(f"⚠️ {_n['id']}：内容过短（{len(_content)} 字），跳过")
                        _prog.progress(_i / len(_missing))
                        continue
                    if _i > 1:
                        time.sleep(1.2)  # 逐条限速，降低触发 429 的概率
                    try:
                        _r = extract_from_text(_content, user_id=USER_ID)
                        _ents = _r.get("entities", [])
                        _rels = _r.get("relations", [])
                        kg.add_entities(_ents, note_id=_n["id"])
                        kg.add_relations(_rels, note_id=_n["id"])
                        if _ents:
                            _ok += 1
                            _logs.append(f"✅ {_n['id']}（{_src} {len(_content)} 字）：{len(_ents)} 实体 / {len(_rels)} 关系")
                        else:
                            _empty += 1
                            _logs.append(f"⚠️ {_n['id']}（{_src} {len(_content)} 字）：模型未抽到实体")
                    except Exception as _e:
                        _fail += 1
                        _logs.append(f"❌ {_n['id']}（{_src} {len(_content)} 字）：{type(_e).__name__}: {_e}")
                    _prog.progress(_i / len(_missing))
                kg.save()
                st.session_state["kg_reextract_summary"] = (
                    f"补抽完成：成功 {_ok} 条 ｜ 未抽到实体 {_empty} 条 ｜ 失败 {_fail} 条"
                )
                st.session_state["kg_reextract_log"] = _logs
                st.rerun()

    with tab_pick:
        st.subheader("🗂️ 选择参与构建图谱的笔记")
        st.caption("勾选笔记后，「图谱总览 / 多跳推理 / 节点分析 / 导出」将只基于所选笔记的知识点构建，不再混淆在一起。")
        st.caption("不勾选任何笔记 = 查看全部图谱。")

        if not all_notes:
            st.info("还没有任何笔记，请先到「导入笔记」添加知识。")
        else:
            # 统计每篇笔记在图谱中贡献的实体数，方便用户判断该笔记是否已入图
            note_entity_cnt = {}
            for nd in kg.get_all_nodes():
                for nid in (nd.get("notes") or []):
                    note_entity_cnt[nid] = note_entity_cnt.get(nid, 0) + 1

            # 初始化每个笔记的选择键（仅首次），避免 value= 与 key= 冲突导致的回弹
            _sel_now = st.session_state.get("kg_selected_notes", [])
            for n in all_notes:
                st.session_state.setdefault(f"kgsel_{n['id']}", n["id"] in _sel_now)

            def _sync_selection():
                current = [n["id"] for n in all_notes
                           if st.session_state.get(f"kgsel_{n['id']}", False)]
                st.session_state["kg_selected_notes"] = current

            c_all, c_none = st.columns(2)
            with c_all:
                if st.button("✅ 全选所有笔记", use_container_width=True):
                    for n in all_notes:
                        st.session_state[f"kgsel_{n['id']}"] = True
                    _sync_selection()
                    st.rerun()
            with c_none:
                if st.button("⬜ 清空选择", use_container_width=True):
                    for n in all_notes:
                        st.session_state[f"kgsel_{n['id']}"] = False
                    _sync_selection()
                    st.rerun()

            st.markdown("---")
            for n in all_notes:
                label = n["preview"][:40] + ("…" if len(n["preview"]) > 40 else "")
                tags = " ".join(f"`{t}`" for t in (n.get("tags") or []))
                cnt = note_entity_cnt.get(n["id"], 0)
                help_text = n["id"] + (f" | {tags}" if tags else "") + f" | 图谱实体 {cnt} 个"
                label_full = f"{label}  `（图谱实体 {cnt}）`"
                st.checkbox(label_full, key=f"kgsel_{n['id']}", help=help_text, on_change=_sync_selection)

            st.markdown("---")
            st.checkbox(
                "包含未标注来源的实体（历史旧数据 / 手动添加）",
                key="kg_include_legacy",
                help="旧版数据中的实体没有记录来源笔记。开启后，选择特定笔记时仍会显示这些通用实体；关闭则只显示所选笔记真正包含的知识点。",
            )

            sel_now = st.session_state.get("kg_selected_notes", [])
            st.info(f"✅ 当前已选 **{len(sel_now)}** 篇笔记" if sel_now else "ℹ️ 当前未勾选任何笔记 → 图谱总览显示**全部**。")
            if st.button("🔄 刷新图谱视图", type="primary"):
                st.rerun()

    with tab_viz:
        if len(view["nodes"]) == 0:
            st.info(view.get("note") or "当前选择范围内图谱为空，请先在「添加笔记」或「导入笔记」添加内容。")
        else:
            selected_cnt = len(st.session_state.get("kg_selected_notes", []))
            scope_str = f"已选 {selected_cnt} 篇笔记（子图）" if selected_cnt else "全部笔记（未勾选）"
            st.markdown(f"**当前架构：** {view['name']} ｜ **范围：** {scope_str}")
            if view.get("note"):
                st.warning(view["note"])
            if view["architecture"] == "classic":
                st.graphviz_chart(gv.view_to_dot(view), use_container_width=True)
            elif view["architecture"] == "list":
                import pandas as _pd
                st.markdown("**实体**")
                st.dataframe(
                    _pd.DataFrame([{"实体": n["id"], "类型": n["type"], "连接数": n["degree"],
                                    "分组": n.get("group_label")} for n in view["nodes"]]),
                    use_container_width=True, hide_index=True,
                )
                st.markdown("**关系**")
                st.dataframe(
                    _pd.DataFrame([{"源": e["source"], "关系": e["relation"],
                                    "目标": e["target"], "类别": e["category"]} for e in view["edges"]]),
                    use_container_width=True, hide_index=True,
                )
            else:
                components.html(gv.view_to_html(view, title="知识图谱"), height=780, scrolling=True)

            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            col1.metric("实体节点", view["stats"]["nodes"])
            col2.metric("关系边", view["stats"]["edges"])
            col3.metric("分组", view["stats"]["groups"])
            if view["groups"]:
                st.caption("分组：" + "　".join(f"{g['label']}({g['size']})" for g in view["groups"][:20]))

            st.markdown("---")
            st.subheader("📤 导出当前架构图谱")
            st.caption("导出为独立文件：HTML 浏览器直接打开、GraphML 导入 Gephi/Neo4j、JSON/CSV 供程序或表格使用、PNG 图片。")
            vkg = gv.view_to_kg(view)
            exp_fmt = st.selectbox("导出格式", ["交互式 HTML", "GraphML", "JSON", "CSV 压缩包", "PNG 图片"], key="kg_exp_fmt")
            exp_key = f"kg_export_{view['architecture']}_{exp_fmt}"
            fname = f"kg_{view['architecture']}"

            if exp_fmt == "交互式 HTML":
                data = gv.view_to_html(view, title="知识图谱").encode("utf-8")
                st.download_button("⬇️ 下载 HTML", data=data, file_name=f"{fname}.html",
                                   mime="text/html", key=exp_key, use_container_width=True)
            elif exp_fmt == "GraphML":
                data = vkg.to_graphml_bytes()
                st.download_button("⬇️ 下载 GraphML", data=data, file_name=f"{fname}.graphml",
                                   mime="application/xml", key=exp_key, use_container_width=True)
            elif exp_fmt == "JSON":
                data = vkg.to_json_bytes()
                st.download_button("⬇️ 下载 JSON", data=data, file_name=f"{fname}.json",
                                   mime="application/json", key=exp_key, use_container_width=True)
            elif exp_fmt == "CSV 压缩包":
                data = vkg.to_csv_zip()
                st.download_button("⬇️ 下载 CSV 压缩包", data=data, file_name=f"{fname}_csv.zip",
                                   mime="application/zip", key=exp_key, use_container_width=True)
            else:
                try:
                    data = vkg.to_png_bytes()
                    st.download_button("⬇️ 下载 PNG", data=data, file_name=f"{fname}.png",
                                       mime="image/png", key=exp_key, use_container_width=True)
                except Exception as e:
                    st.warning(f"PNG 导出需要服务器安装 Graphviz（dot 命令），当前不可用：{e}\n\n请改用其他格式。")

    with tab_reason:
        kg_view = gv.view_to_kg(view)
        st.caption(f"当前架构：{view['name']}（推理基于该架构的子图）")
        if len(kg_view.graph.nodes) < 2:
            st.info("当前架构下需要至少 2 个实体才能推理。（可换架构或调整「选择笔记」扩大范围）")
        else:
            tab_cross, tab_query = st.tabs(["跨领域关联发现", "指定节点查询"])

            with tab_cross:
                st.subheader("跨领域关联")
                st.caption("发现不同领域实体之间的多跳连接路径")
                if st.button("发现跨领域关联", type="primary", key="cross_btn"):
                    with st.spinner("正在计算..."):
                        links = discover_cross_domain_links(kg_view)
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
                node_list = [n["name"] for n in kg_view.get_all_nodes()]
                selected = st.selectbox("选择起始节点", node_list)
                hops = st.slider("最大跳数", 1, 4, 2, key="hop_slider")
                if st.button("查询关联", type="primary", key="query_btn"):
                    with st.spinner("正在推理..."):
                        related = find_related_concepts(kg_view, selected, max_hops=hops)
                    if not related:
                        st.info("未找到跨领域关联")
                    else:
                        for r in related:
                            path_str = " → ".join(r["path"])
                            st.markdown(f"**{r['concept']}** ({r['type']}) — {r['hops']}跳")
                            st.caption(f"路径: {path_str}")

    with tab_analysis:
        kg_view = gv.view_to_kg(view)
        if len(kg_view.graph.nodes) == 0:
            st.info("当前架构范围内为空。")
        else:
            scores = get_importance_scores(kg_view)
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
    page_header("🎯", "个性化学习路径", "根据遗忘曲线和标签掌握度，推荐下一步学习方向")
    notebook_line()

    _done = st.session_state.get("_review_done")
    if _done:
        st.success(_done)
        st.session_state["_review_done"] = None

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
                st.markdown('<span class="hb-card"></span>', unsafe_allow_html=True)
                st.markdown(f"### {icon} **{tag}** — {label}")
                st.markdown(f"💡 {reason}")
                st.caption(f"涉及 {total} 条笔记")

                for n in rec["notes"]:
                    ret = n["retention"]
                    color = "🟢" if ret > 0.7 else ("🟡" if ret > 0.4 else "🔴")
                    st.markdown(f"{color} {n['preview']}  — 保留率 {ret*100:.0f}%")

                if urgency in ("high", "medium"):
                    _open = st.session_state.get("_review_open") == tag
                    if not _open and st.button(f"开始复习 {tag}", key=f"start_review_{tag}"):
                        st.session_state["_review_open"] = tag
                        _open = True  # 同一次运行内直接展开，避免额外 rerun 造成滚动跳位
                    if _open:
                        with st.container():
                            st.markdown('<span class="hb-flip"></span>', unsafe_allow_html=True)
                            st.markdown(f"#### 📖 复习中 · {tag}")
                            for n in rec["notes"]:
                                _full = vector_store.get_note_full_content(
                                    n["id"], user_id=USER_ID
                                ) or n["preview"]
                                st.markdown(
                                    f'<div class="note-full-content">{html.escape(_full)}</div>',
                                    unsafe_allow_html=True,
                                )
                            _done_col, _cancel_col = st.columns(2)
                            if _done_col.button(
                                "✅ 复习完成", key=f"done_review_{tag}",
                                type="primary", use_container_width=True,
                            ):
                                for n in rec["notes"]:
                                    fc.record_access(n["id"], user_id=USER_ID)
                                st.session_state["_review_open"] = None
                                st.session_state["_review_done"] = (
                                    f"✅ 已完成「{tag}」的复习（{len(rec['notes'])} 条），保留率已更新！"
                                )
                                st.rerun()
                            if _cancel_col.button(
                                "取消", key=f"cancel_review_{tag}", use_container_width=True
                            ):
                                st.session_state["_review_open"] = None
                                st.rerun()

    st.markdown("---")
    st.subheader("最急需复习的笔记")
    weak_notes = get_weak_notes(5, user_id=USER_ID)
    if weak_notes:
        for wn in weak_notes:
            ret = wn["retention"]
            tags_str = " ".join([f"`{t}`" for t in wn["tags"]])
            with st.container():
                st.markdown('<span class="hb-card"></span>', unsafe_allow_html=True)
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
    page_header("🌐", "知识广场", "去外面搜集知识，剪下来贴进你的笔记本")
    notebook_line()

    tab_search, tab收藏 = st.tabs(["在线搜索", "收藏网页"])

    with tab_search:
        from tools.web_search import search_web, fetch_url_content, bing_search_iframe_url
        from tools.add_knowledge import execute as add_exec

        c_q, c_b = st.columns([4, 1])
        with c_q:
            search_query = st.text_input(
                "搜索",
                placeholder="输入关键词，回车搜索真实网页...",
                key="kg_search",
                label_visibility="collapsed",
            )
        with c_b:
            do_search = st.button("🔍 搜索", type="primary", use_container_width=True)

        # 内嵌浏览器开关：始终可点（不再因无关键词而禁用，避免看起来"无法访问"）
        iframe_toggle = st.toggle(
            "🖥️ 内嵌浏览器直接浏览搜索结果页",
            key="kg_embed_on",
            help="在页面内嵌 Bing 的真实搜索结果页面，可直接在应用里点击浏览原文。",
        )
        if iframe_toggle:
            if search_query.strip():
                st.components.v1.iframe(bing_search_iframe_url(search_query), height=720, scrolling=True)
            else:
                st.info("👆 请先在上方输入关键词并回车，内嵌浏览器会自动加载搜索结果页。")

        if search_query.strip() and do_search:
            with st.spinner("正在检索（Bing）..."):
                try:
                    results = search_web(search_query, count=10)
                    st.session_state["kg_search_results"] = results
                    st.session_state["kg_search_query"] = search_query
                except Exception as e:
                    st.error(f"搜索失败: {e}")
                    st.session_state.pop("kg_search_results", None)

        results = st.session_state.get("kg_search_results")

        if results is None:
            st.caption("👆 输入关键词开始搜索，或到右侧「收藏网页」直接粘贴链接入库。")
        elif not results:
            st.warning("没有搜到结果，换个关键词试试。")
        else:
            st.success(f"共找到 {len(results)} 条结果（来自 Bing）")
            st.markdown("每条可 **一键收藏入库**，或点标题在新窗口打开原文。")

            save_tags_default = st.session_state.get("kg_search_query", "网页收藏")
            st.caption(f"收藏标签将自动带上关键词：`{save_tags_default}`")

            for i, r in enumerate(results):
                st.markdown(
                    f'<div class="pz-item zoom-in"><span class="no">{i+1}</span>',
                    unsafe_allow_html=True,
                )
                col_l, col_r = st.columns([5, 1])
                with col_l:
                    st.markdown(f"**[{r['title']}]({r['url']})**")
                    if r.get("cite"):
                        st.caption(r["cite"])
                    if r.get("snippet"):
                        st.markdown(r["snippet"])
                with col_r:
                    if st.button("📥 收藏", key=f"kg_save_res_{i}", use_container_width=True):
                        tags = list({save_tags_default, "网页收藏"})
                        with st.spinner("抓取网页并入库..."):
                            try:
                                page_data = fetch_url_content(r["url"])
                                full_content = f"[来源: {page_data['title'] or r['url']}]({r['url']})\n\n{page_data['content']}"
                                from tools.add_knowledge import execute as add_exec
                                add_result = json.loads(add_exec({
                                    "content": full_content,
                                    "tags": tags,
                                    "importance": "normal",
                                }, user_id=USER_ID))
                                if add_result.get("note_id"):
                                    st.success(f"已收藏！{page_data['title']}")
                                else:
                                    st.error(f"入库失败: {add_result.get('error', '未知错误')}")
                            except Exception as e:
                                st.error(f"抓取失败: {e}")
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**或者手动粘贴链接一键入库：**")
        save_url = st.text_input("网页链接", placeholder="https://...", key="kg_save_url")
        save_tags = st.text_input("标签", value="网页收藏", key="kg_save_tags", placeholder="标签，逗号分隔")

        if st.button("收藏到知识库", type="primary", key="kg_save_btn"):
            if save_url.strip():
                tags = [t.strip() for t in save_tags.split(",") if t.strip()]
                with st.spinner("正在抓取网页并入库..."):
                    try:
                        page_data = fetch_url_content(save_url)
                        full_content = f"[来源: {page_data['title'] or save_url}]({save_url})\n\n{page_data['content']}"
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
else:  # 页面九：设置
    page_header("⚙️", "笔记本偏好", "配置你的第二大脑 API 与数据")
    notebook_line()

    st.markdown("""
    <div class="setpanel" style="position:relative;background:var(--paper);border:2px solid var(--paper-edge);
      border-radius:14px;padding:1.1rem 1.2rem;margin-bottom:1rem;box-shadow:0 2px 0 rgba(90,70,40,.06)">
      <div class="tape"></div>
      <h3 style="font-family:'Ma Shan Zheng',cursive;color:var(--ink);margin:0 0 .5rem">🔧 API 配置</h3>
    """, unsafe_allow_html=True)
    from memory import long_term

    current_url = long_term.get_preference("api_base_url", config.OPENAI_BASE_URL, user_id=USER_ID)
    current_key = long_term.get_preference("api_key", config.OPENAI_API_KEY, user_id=USER_ID)
    current_model = long_term.get_preference("model_name", config.MODEL_NAME, user_id=USER_ID)
    current_embedding = long_term.get_preference("embedding_model", config.EMBEDDING_MODEL, user_id=USER_ID)
    st.markdown("</div>", unsafe_allow_html=True)

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

    # ── API Token：接入智能体 ──
    _base = config.PUBLIC_BASE_URL or "http://<你的服务器>:8000"
    st.markdown(f"""
    <div class="setpanel" style="position:relative;background:var(--paper);border:2px solid var(--paper-edge);
      border-radius:14px;padding:1.1rem 1.2rem;margin-bottom:1rem;box-shadow:0 2px 0 rgba(90,70,40,.06)">
      <div class="tape"></div>
      <h3 style="font-family:'Ma Shan Zheng',cursive;color:var(--ink);margin:0 0 .4rem">🔑 接入智能体（API Token）</h3>
      <p style="font-family:'ZCOOL XiaoWei',serif;color:var(--ink-soft);margin:0">
        把知识库接入 Claude / Cursor / Coze / Dify 等助手，需要一把钥匙（Token）。<br>
        MCP 地址：<code>{_base}/mcp</code><br>
        REST 地址：<code>{_base}/api</code>
      </p>
    </div>
    """, unsafe_allow_html=True)

    from storage import api_tokens as _tok
    try:
        if st.button("➕ 生成新 Token", type="primary"):
            st.session_state["_new_token"] = _tok.create_token(USER_ID, name="web")
        if st.session_state.get("_new_token"):
            st.success("Token 已生成，请立即复制保存（只显示这一次）：")
            st.code(st.session_state["_new_token"], language=None)
            if st.button("我已保存，隐藏"):
                st.session_state.pop("_new_token", None)
                st.rerun()
        _tokens = _tok.list_tokens(USER_ID)
        if _tokens:
            st.caption("已有 Token：")
            for _t in _tokens:
                _c1, _c2 = st.columns([4, 1])
                with _c1:
                    _state = "已撤销" if _t.get("revoked") else "有效"
                    st.markdown(f"`{_t['token_prefix']}...` · {_t.get('name') or 'default'} · {_state}")
                with _c2:
                    if not _t.get("revoked"):
                        if st.button("撤销", key=f"revoke_{_t['id']}"):
                            _tok.revoke_token(USER_ID, str(_t["id"]))
                            st.rerun()
        else:
            st.caption("还没有 Token，点上面按钮生成一个。")
    except Exception as _e:
        st.warning(f"Token 功能不可用（可能还没建表）：{_e}")
        st.caption("请在服务器执行：psql -U secondbrain -d secondbrain -f migrations/add_api_tokens.sql")

    st.markdown("""
    <div class="setpanel" style="position:relative;background:var(--paper);border:2px solid var(--paper-edge);
      border-radius:14px;padding:1.1rem 1.2rem;margin-bottom:1rem;box-shadow:0 2px 0 rgba(90,70,40,.06)">
      <h3 style="font-family:'Ma Shan Zheng',cursive;color:var(--ink);margin:0 0 .5rem">🗂️ 数据管理</h3>
    """, unsafe_allow_html=True)

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

    st.markdown("</div>", unsafe_allow_html=True)
