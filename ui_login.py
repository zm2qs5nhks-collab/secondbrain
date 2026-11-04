"""
登录 / 注册 —— 品牌落地页（腾讯官网风格）

设计基准（对齐 www.tencent.com/zh-cn）：
- 纯白底 + 腾讯品牌蓝 #0052D9，蓝色仅用于强调，不做大面积铺色
- 大字重对比：H1 54px/800，正文 15-16px/1.7，行高与字距收紧
- 圆角 8px（控件）/ 12px（卡片）/ 16px（登录卡），1px #e7e7e7 细边
- 克制的留白与细分割线；悬停只做 -3px 轻抬 + 极浅投影
- 系统字体栈（PingFang SC / 微软雅黑 / TencentSans），不依赖 Google Fonts

只负责「壳」和「文案」，登录表单本身由 app.py 用原生 Streamlit 控件渲染，
控件由 LOGIN_CSS 里的 .st-key-tLoginCard 作用域统一改写成腾讯风格。
"""

import streamlit as st

# ═══════════════════════════════════════════════════════════════
#  设计令牌 + 页面样式
# ═══════════════════════════════════════════════════════════════
LOGIN_CSS = r"""
<style>
:root{
  --tv-blue:#0052D9; --tv-blue-hover:#266FE8; --tv-blue-active:#0034B5;
  --tv-blue-1:#ECF2FE; --tv-ink:#181818; --tv-ink-2:#5c5c5c; --tv-ink-3:#8f8f8f;
  --tv-line:#e7e7e7; --tv-line-soft:#f0f0f0; --tv-bg-2:#f5f7fa;
  --tv-font:"TencentSans","PingFang SC","HarmonyOS Sans SC","Microsoft YaHei",
            -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  --tv-ease:cubic-bezier(.22,.61,.36,1);
}

/* ── 画布 ───────────────────────────────────────────── */
html, body, .stApp{background:#ffffff!important;}
.stApp{
  font-family:var(--tv-font)!important; color:var(--tv-ink);
  -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
}
/* 顶部极淡的品牌光晕，只做氛围，不影响阅读 */
.stApp::before{
  content:''; position:fixed; inset:0 0 auto; height:460px; pointer-events:none; z-index:0;
  background:
    radial-gradient(760px 340px at 86% -14%, rgba(0,82,217,.075), transparent 66%),
    radial-gradient(520px 260px at 6% -18%, rgba(0,82,217,.045), transparent 64%);
}
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"]{display:none!important;}
[data-testid="stSidebar"]{display:none!important;}
.block-container, [data-testid="stMainBlockContainer"]{
  max-width:1240px!important; padding:0 40px!important;
}
@media (max-width:640px){
  .block-container, [data-testid="stMainBlockContainer"]{padding:0 20px!important;}
  /* 窄屏下 Streamlit 会把 columns 竖排，把「登录/注册」强行拉回一行 */
  .st-key-tSwitch [data-testid="stHorizontalBlock"]{
    flex-direction:row!important; flex-wrap:nowrap!important;
  }
  .st-key-tSwitch [data-testid="stHorizontalBlock"] > div{
    flex:1 1 50%!important; width:50%!important; min-width:0!important;
  }
}
/* 让页面本身可滚动且不被 Streamlit 的默认 6rem 顶部内边距顶开 */
[data-testid="stMain"]{padding-top:0!important;}
.stApp [data-testid="stVerticalBlock"]{gap:0;}
.stApp [data-testid="stHorizontalBlock"]{gap:0;}

/* ── 顶部导航 ───────────────────────────────────────── */
.tv-topbar{
  position:relative; z-index:2;
  display:flex; align-items:center; justify-content:space-between; gap:24px;
  height:68px; border-bottom:1px solid var(--tv-line);
}
.tv-brand{display:flex; align-items:center; gap:10px; text-decoration:none;}
.tv-logo{
  width:34px; height:34px; border-radius:9px; display:grid; place-items:center; flex:0 0 auto;
  background:linear-gradient(135deg,#0a5fe0 0%,#0052D9 55%,#0046b8 100%);
  box-shadow:0 4px 12px rgba(0,82,217,.26);
}
.tv-name{font-size:17px; font-weight:700; letter-spacing:.01em; color:var(--tv-ink);}
.tv-badge{
  margin-left:2px; padding:2px 6px; border-radius:4px;
  font-size:10px; font-weight:700; letter-spacing:.1em;
  color:var(--tv-blue); background:var(--tv-blue-1);
}
.tv-nav{display:flex; align-items:center; gap:30px;}
.tv-nav a{
  font-size:14px; color:var(--tv-ink-2); text-decoration:none;
  transition:color .15s var(--tv-ease);
}
.tv-nav a:hover{color:var(--tv-blue);}
.tv-actions{display:flex; align-items:center; gap:10px;}
.tv-ghost{
  font-size:14px; color:var(--tv-ink-2); text-decoration:none;
  padding:8px 12px; border-radius:6px; transition:background .15s,color .15s;
}
.tv-ghost:hover{background:var(--tv-blue-1); color:var(--tv-blue);}
.tv-pill{
  display:inline-block; font-size:14px; font-weight:500; color:#fff!important;
  text-decoration:none; background:var(--tv-blue);
  padding:9px 18px; border-radius:6px;
  transition:background .15s, box-shadow .15s, transform .15s;
}
.tv-pill:hover{background:var(--tv-blue-hover); box-shadow:0 8px 18px rgba(0,82,217,.26);}
.tv-pill:active{background:var(--tv-blue-active); transform:translateY(1px);}
@media (max-width:900px){ .tv-nav{display:none;} .tv-ghost{display:none;} }

/* ── HERO ──────────────────────────────────────────── */
.tv-hero{position:relative; z-index:1; padding:60px 40px 44px 0;}
@media (max-width:900px){ .tv-hero{padding:32px 0 8px;} }

.tv-eyebrow{
  display:inline-flex; align-items:center; gap:9px; margin-bottom:20px;
  font-size:11.5px; font-weight:700; letter-spacing:.16em; text-transform:uppercase;
  color:var(--tv-blue);
}
.tv-dot{
  width:6px; height:6px; border-radius:50%; background:var(--tv-blue);
  box-shadow:0 0 0 4px var(--tv-blue-1);
}
.tv-h1{
  margin:0; font-size:54px; line-height:1.14; letter-spacing:-.028em;
  font-weight:800; color:var(--tv-ink);
}
.tv-h1 em{font-style:normal; color:var(--tv-blue);}
@media (max-width:1100px){ .tv-h1{font-size:44px;} }
@media (max-width:640px){ .tv-h1{font-size:34px; letter-spacing:-.02em;} }

.tv-lede{
  margin:22px 0 0; max-width:460px;
  font-size:16px; line-height:1.78; color:var(--tv-ink-2);
}
@media (max-width:640px){ .tv-lede{font-size:14.5px; line-height:1.7;} }

.tv-cta{display:flex; align-items:center; gap:12px; margin-top:32px; flex-wrap:wrap;}
.tv-cta-main{
  display:inline-flex; align-items:center; gap:8px;
  background:var(--tv-blue); color:#fff!important; text-decoration:none;
  font-size:15px; font-weight:600; padding:13px 26px; border-radius:8px;
  box-shadow:0 10px 24px rgba(0,82,217,.22);
  transition:background .15s, transform .15s, box-shadow .15s;
}
.tv-cta-main:hover{background:var(--tv-blue-hover); transform:translateY(-1px); box-shadow:0 14px 30px rgba(0,82,217,.28);}
.tv-cta-main:active{background:var(--tv-blue-active); transform:translateY(0);}
.tv-cta-sub{
  display:inline-flex; align-items:center; gap:6px;
  color:var(--tv-ink)!important; text-decoration:none;
  font-size:15px; font-weight:500; padding:12px 18px; border-radius:8px;
  border:1px solid var(--tv-line); background:#fff;
  transition:border-color .15s, background .15s, transform .15s;
}
.tv-cta-sub:hover{border-color:#c9d8f7; background:#fafcff; transform:translateY(-1px);}

.tv-points{
  display:flex; flex-wrap:wrap; gap:10px 26px;
  margin-top:38px; padding-top:22px; border-top:1px solid var(--tv-line);
}
.tv-point{display:flex; align-items:center; gap:7px; font-size:13px; color:var(--tv-ink-2);}
.tv-point svg{color:var(--tv-blue); flex:0 0 auto;}

/* ── 登录卡（作用域：st.container(key="tLoginCard")）───── */
.st-key-tLoginCard{
  background:#fff; border:1px solid var(--tv-line); border-radius:16px;
  padding:30px 28px 24px;
  box-shadow:0 20px 48px rgba(16,24,40,.09), 0 2px 6px rgba(16,24,40,.04);
}
@media (max-width:900px){ .st-key-tLoginCard{padding:22px 18px 16px; margin-top:12px;} }

.tc-eyebrow{font-size:11px; font-weight:700; letter-spacing:.16em; color:var(--tv-ink-3); text-transform:uppercase;}
.tc-title{font-size:23px; font-weight:700; letter-spacing:-.01em; color:var(--tv-ink); margin:8px 0 6px;}
.tc-sub{font-size:13px; line-height:1.6; color:var(--tv-ink-2); margin-bottom:18px;}
.tc-terms{font-size:11.5px; line-height:1.6; color:var(--tv-ink-3); margin-top:14px; text-align:center;}
.tc-terms a{color:var(--tv-blue); text-decoration:none;}
.tc-terms a:hover{text-decoration:underline;}

/* 卡片内控件排布：收紧 Streamlit 默认 1rem 间距 */
.st-key-tLoginCard [data-testid="stVerticalBlock"]{gap:.55rem;}
.st-key-tLoginCard [data-testid="stHorizontalBlock"]{gap:8px;}

/* 登录 / 注册 切换（作用域：st.container(key="tSwitch")） */
.st-key-tSwitch{background:var(--tv-bg-2); border-radius:8px; padding:4px; margin-bottom:6px;}
.st-key-tSwitch [data-testid="stHorizontalBlock"]{gap:4px;}
.st-key-tSwitch button{
  height:34px; min-height:34px; border:none!important; border-radius:6px!important;
  font-family:var(--tv-font)!important; font-size:13.5px!important;
  font-weight:500!important; letter-spacing:0!important;
  background:transparent!important; color:var(--tv-ink-2)!important;
  box-shadow:none!important; transform:none!important;
  transition:background .15s, color .15s!important;
}
.st-key-tSwitch button:hover{color:var(--tv-blue)!important; background:rgba(0,82,217,.06)!important;}
.st-key-tSwitch [data-testid="stBaseButton-primary"]{
  background:#fff!important; color:var(--tv-blue)!important; font-weight:600!important;
  box-shadow:0 1px 3px rgba(16,24,40,.10), 0 0 0 1px rgba(0,82,217,.12)!important;
}
.st-key-tSwitch [data-testid="stBaseButton-primary"]:hover{background:#fff!important;}

/* ── 输入框 ─────────────────────────────────────────────
   注意：Streamlit 1.5x 用 [data-testid="stTextInputRootElement"] 承载
   底色/边框（底色来自主题 secondaryBackgroundColor，会带出米黄），
   旧版则是 div[data-baseweb="input"]。两套选择器都写上，跨版本安全。 */
.st-key-tLoginCard [data-testid="stTextInput"]{margin:0;}
.st-key-tLoginCard [data-testid="stTextInputRootElement"],
.st-key-tLoginCard div[data-baseweb="input"]{
  height:46px!important;
  background:#fff!important;
  border:1px solid #dcdcdc!important;
  border-radius:8px!important;
  box-shadow:none!important;
  transition:border-color .15s, box-shadow .15s;
}
.st-key-tLoginCard [data-testid="stTextInputRootElement"]:hover,
.st-key-tLoginCard div[data-baseweb="input"]:hover{border-color:#bdbdbd!important;}
.st-key-tLoginCard [data-testid="stTextInputRootElement"]:focus-within,
.st-key-tLoginCard div[data-baseweb="input"]:focus-within{
  border-color:var(--tv-blue)!important;
  box-shadow:0 0 0 3px rgba(0,82,217,.12)!important;
}
.st-key-tLoginCard [data-testid="stTextInputRootElement"] input,
.st-key-tLoginCard div[data-baseweb="input"] input{
  height:44px!important; padding:0 14px!important;
  font-family:var(--tv-font)!important; font-size:14px!important;
  color:var(--tv-ink)!important; background:transparent!important;
  border:none!important; box-shadow:none!important; outline:none!important;
}
.st-key-tLoginCard [data-testid="stTextInputRootElement"] input::placeholder,
.st-key-tLoginCard div[data-baseweb="input"] input::placeholder{
  color:#a3a3a3!important; opacity:1!important;
}
.st-key-tLoginCard [data-testid="stTextInput"] label{display:none!important;}
/* 密码框的「眼睛」按钮：改成克制的灰色 */
.st-key-tLoginCard [data-testid="stTextInputRootElement"] button{
  background:transparent!important; color:#8f8f8f!important; box-shadow:none!important;
}

/* 提交按钮 */
.st-key-tLoginCard [data-testid="stFormSubmitButton"] button,
.st-key-tLoginCard [data-testid="stBaseButton-primaryFormSubmit"]{
  height:46px; min-height:46px; width:100%;
  border:none!important; border-radius:8px!important;
  background:var(--tv-blue)!important; color:#fff!important;
  font-family:var(--tv-font)!important; font-size:15px!important; font-weight:600!important;
  letter-spacing:.06em!important; box-shadow:none!important; transform:none!important;
  transition:background .15s, box-shadow .15s, transform .1s!important;
}
.st-key-tLoginCard [data-testid="stFormSubmitButton"] button:hover,
.st-key-tLoginCard [data-testid="stBaseButton-primaryFormSubmit"]:hover{
  background:var(--tv-blue-hover)!important;
  box-shadow:0 8px 20px rgba(0,82,217,.26)!important;
}
.st-key-tLoginCard [data-testid="stFormSubmitButton"] button:active,
.st-key-tLoginCard [data-testid="stBaseButton-primaryFormSubmit"]:active{
  background:var(--tv-blue-active)!important; transform:translateY(1px)!important;
}

/* 表单容器本身不要边框/内边距（Streamlit 的 stForm 默认带 border） */
.st-key-tLoginCard [data-testid="stForm"]{
  border:none!important; padding:0!important; background:transparent!important;
}
/* 提示条 */
.st-key-tLoginCard [data-testid="stAlert"]{
  border-radius:8px!important; padding:9px 12px!important;
  font-size:12.5px!important; margin:2px 0 0!important;
}
.st-key-tLoginCard [data-testid="stAlert"] p{font-size:12.5px!important; line-height:1.55!important;}

/* ── 能力区 ─────────────────────────────────────────── */
.tv-section{position:relative; z-index:1; padding:58px 0 6px;}
.tv-sec-head{max-width:620px; margin-bottom:30px;}
.tv-h2{
  margin:10px 0 0; font-size:32px; line-height:1.28; letter-spacing:-.02em;
  font-weight:700; color:var(--tv-ink);
}
@media (max-width:640px){ .tv-h2{font-size:24px;} }
.tv-sec-head p{margin:12px 0 0; font-size:15px; line-height:1.72; color:var(--tv-ink-2);}

.tv-cards{display:grid; grid-template-columns:repeat(4,1fr); gap:16px;}
@media (max-width:1080px){ .tv-cards{grid-template-columns:repeat(2,1fr);} }
@media (max-width:560px){ .tv-cards{grid-template-columns:1fr;} }

.tv-card{
  position:relative; background:#fff; border:1px solid var(--tv-line);
  border-radius:12px; padding:24px 20px 26px;
  transition:transform .22s var(--tv-ease), border-color .22s, box-shadow .22s;
}
.tv-card:hover{
  transform:translateY(-3px); border-color:#cfdffb;
  box-shadow:0 14px 30px rgba(16,24,40,.08);
}
.tv-ico{
  width:42px; height:42px; border-radius:10px; display:grid; place-items:center;
  background:var(--tv-blue-1); color:var(--tv-blue); margin-bottom:18px;
  transition:background .22s, color .22s;
}
.tv-card:hover .tv-ico{background:var(--tv-blue); color:#fff;}
.tv-card h3{margin:0 0 9px; font-size:15.5px; font-weight:600; color:var(--tv-ink);}
.tv-card p{margin:0; font-size:13.5px; line-height:1.72; color:var(--tv-ink-2);}

/* ── 页脚 ───────────────────────────────────────────── */
.tv-footer{
  display:flex; align-items:center; justify-content:space-between; gap:18px; flex-wrap:wrap;
  margin-top:64px; padding:26px 0 34px; border-top:1px solid var(--tv-line);
  font-size:13px; color:var(--tv-ink-3);
}
.tv-footer .tv-flinks{display:flex; gap:22px;}
.tv-footer a{color:var(--tv-ink-3); text-decoration:none; transition:color .15s;}
.tv-footer a:hover{color:var(--tv-blue);}
/* 备案号 / 联系方式 */
.tv-legal{
  margin:-16px 0 30px; font-size:12px; color:var(--tv-ink-3);
  display:flex; gap:14px; flex-wrap:wrap; align-items:center;
}
.tv-legal a{color:var(--tv-ink-3); text-decoration:none;}
.tv-legal a:hover{color:var(--tv-blue); text-decoration:underline;}

/* 关闭注册时的私有提示 */
.tc-private{
  margin:2px 0 10px; padding:9px 12px; border-radius:8px;
  background:var(--tv-bg-2); color:var(--tv-ink-2);
  font-size:12.5px; line-height:1.5;
}

/* 无障碍 */
@media (prefers-reduced-motion: reduce){
  .tv-card, .tv-cta-main, .tv-cta-sub, .tv-pill, .st-key-tLoginCard{transition:none!important;}
}
</style>
"""


# ═══════════════════════════════════════════════════════════════
#  HTML 片段（图标均为内联 SVG，不依赖图标字体）
# ═══════════════════════════════════════════════════════════════
_LOGO = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="6" cy="6.5" r="2.4"/><circle cx="18" cy="9" r="2.4"/>'
    '<circle cx="10" cy="18" r="2.4"/><path d="M8.2 7.3 15.8 8.5M7.6 8.8l1.7 6.7"/></svg>'
)

_CHECK = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="m4 12.5 5 5L20 6.5"/></svg>'
)

_ICON_SEARCH = (
    '<svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.7" stroke-linecap="round"><circle cx="11" cy="11" r="6.6"/>'
    '<path d="m16 16 4.6 4.6"/></svg>'
)
_ICON_GRAPH = (
    '<svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.7" stroke-linecap="round"><circle cx="6" cy="7" r="2.5"/>'
    '<circle cx="18" cy="10" r="2.5"/><circle cx="10" cy="18" r="2.5"/>'
    '<path d="M8.3 8.1 15.7 9.3M7.3 9.3l1.9 6.3"/></svg>'
)
_ICON_CLOCK = (
    '<svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="12" r="8.6"/>'
    '<path d="M12 7.4V12l3 2"/></svg>'
)
_ICON_PLUG = (
    '<svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="3.5" y="3.5" width="7" height="7" rx="1.8"/>'
    '<rect x="13.5" y="3.5" width="7" height="7" rx="1.8"/>'
    '<rect x="3.5" y="13.5" width="7" height="7" rx="1.8"/>'
    '<path d="M14 17h6M17 14v6"/></svg>'
)

TOPBAR_HTML = f"""
<div class="tv-topbar">
  <a class="tv-brand" href="#tv-top">
    <span class="tv-logo">{_LOGO}</span>
    <span class="tv-name">第二大脑</span>
    <span class="tv-badge">BETA</span>
  </a>
  <nav class="tv-nav">
    <a href="#tv-features">产品能力</a>
    <a href="#tv-features">知识图谱</a>
    <a href="#tv-features">遗忘曲线</a>
    <a href="#tv-login">开放接口</a>
  </nav>
  <div class="tv-actions">
    <a class="tv-ghost" href="#tv-login">登录</a>
    <a class="tv-pill" href="#tv-login">免费开始</a>
  </div>
</div>
"""

HERO_HTML = f"""
<div class="tv-hero" id="tv-top">
  <div class="tv-eyebrow"><span class="tv-dot"></span>Personal Knowledge Agent</div>
  <h1 class="tv-h1">让每一个想法<br>都被<em>记住</em></h1>
  <p class="tv-lede">
    笔记、网页与灵光一现，统一收进一张会关联、会检索、
    也会在你快要忘掉的时候提醒你的知识网络。
  </p>
  <div class="tv-cta">
    <a class="tv-cta-main" href="#tv-login">立即开始<span aria-hidden="true">→</span></a>
    <a class="tv-cta-sub" href="#tv-features">看看能做什么</a>
  </div>
  <div class="tv-points">
    <span class="tv-point">{_CHECK}语义检索，按意思找</span>
    <span class="tv-point">{_CHECK}实体关系，多跳推理</span>
    <span class="tv-point">{_CHECK}遗忘曲线，主动复习</span>
  </div>
</div>
"""

FEATURES_HTML = f"""
<div class="tv-section" id="tv-features">
  <div class="tv-sec-head">
    <div class="tv-eyebrow"><span class="tv-dot"></span>Capabilities</div>
    <h2 class="tv-h2">把知识管理，做成顺手的事</h2>
    <p>四件核心能力，撑起从「记下来」到「想起来」的完整闭环。</p>
  </div>
  <div class="tv-cards">
    <div class="tv-card">
      <div class="tv-ico">{_ICON_SEARCH}</div>
      <h3>语义检索</h3>
      <p>不靠关键词硬匹配。你的问题会被向量化，直接命中真正相关的那一段原文。</p>
    </div>
    <div class="tv-card">
      <div class="tv-ico">{_ICON_GRAPH}</div>
      <h3>知识图谱</h3>
      <p>自动抽取实体与关系，支持多跳推理发现跨领域连接，可导出 GraphML 与交互式 HTML。</p>
    </div>
    <div class="tv-card">
      <div class="tv-ico">{_ICON_CLOCK}</div>
      <h3>遗忘曲线</h3>
      <p>每条笔记都有独立的记忆曲线，快忘的时候主动提醒，并按紧急程度排好顺序。</p>
    </div>
    <div class="tv-card">
      <div class="tv-ico">{_ICON_PLUG}</div>
      <h3>智能体接入</h3>
      <p>同一套知识库，通过 REST 与 MCP 接给 Claude、Cursor、Coze 等助手调用。</p>
    </div>
  </div>
</div>
"""

FOOTER_HTML = """
<div class="tv-footer">
  <span>© 2026 第二大脑 · 个人知识管理 Agent</span>
  <span class="tv-flinks">
    <a href="#tv-features">产品能力</a>
    <a href="#tv-login">隐私说明</a>
    <a href="#tv-login">服务条款</a>
  </span>
</div>
"""


# ═══════════════════════════════════════════════════════════════
#  渲染入口
# ═══════════════════════════════════════════════════════════════
def render_scaffold():
    """注入样式 + 顶部导航。必须在登录页最开始调用一次。"""
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)
    st.markdown(TOPBAR_HTML, unsafe_allow_html=True)


def render_hero():
    st.markdown(HERO_HTML, unsafe_allow_html=True)


def render_features():
    st.markdown(FEATURES_HTML, unsafe_allow_html=True)


def render_footer():
    st.markdown(FOOTER_HTML, unsafe_allow_html=True)

    # 备案号与联系方式：备案审核会看，配置了才渲染
    import html as _html

    import config

    bits = []
    if getattr(config, "SITE_ICP", ""):
        bits.append(
            f'<a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">'
            f'{_html.escape(config.SITE_ICP)}</a>'
        )
    if getattr(config, "SITE_CONTACT", ""):
        bits.append(f"<span>联系方式：{_html.escape(config.SITE_CONTACT)}</span>")
    bits.append("<span>本站为个人知识库，内容不对外公开</span>")

    st.markdown('<div class="tv-legal">' + " · ".join(bits) + "</div>", unsafe_allow_html=True)
