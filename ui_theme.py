"""
手帐/笔记本风格 UI 主题
——
基于 ui_mockup_sketchbook.html 的设计稿，将手帐风格适配到 Streamlit 应用：
- 保留侧边栏结构与全部既有功能，仅替换皮肤
- 全局控件（按钮/输入/指标/tab/expander/对话气泡/进度条）全部手帐化
- 提供 page_header / paper-card / sticky 等页面级组件
"""

import streamlit as st

FONT_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?'
    'family=ZCOOL+KuaiLe&family=ZCOOL+XiaoWei&family=Ma+Shan+Zheng'
    '&family=Liu+Jian+Mao+Cao&family=Caveat:wght@500;700'
    '&family=Permanent+Marker&display=swap" rel="stylesheet">'
)

# ═══════════════════════════════════════════════════════════════
#  登录页皮肤（深色玻璃 → 便利贴签到纸）
# ═══════════════════════════════════════════════════════════════
LOGIN_CSS = r"""
<style>
:root{
  --paper:#fbf5e9; --paper-2:#f6eeda; --paper-edge:#e9dcc3;
  --ink:#3b3226; --ink-soft:#7a6f5e; --ink-faint:#b3a68e;
  --sticky-y:#ffe9a8; --sticky-p:#ffd6e7; --sticky-b:#d9efff; --sticky-g:#d9f5dc;
  --pen:#2f5d8f; --pen-dark:#224566; --pen-red:#c0504d; --pen-green:#4a7a4c; --pen-orange:#c07a3a;
  --tape:rgba(255,255,255,.55);
}
[data-testid="stApp"], .stApp{
  background:
    radial-gradient(circle at 15% 10%, rgba(200,180,140,.12), transparent 40%),
    radial-gradient(circle at 85% 90%, rgba(200,180,140,.10), transparent 45%),
    var(--paper) !important;
  font-family:'ZCOOL XiaoWei',serif !important;
  color:var(--ink) !important;
}
[data-testid="stApp"]::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.5;
  background-image:radial-gradient(rgba(150,130,100,.35) .6px, transparent .6px);background-size:3px 3px;}
.block-container{max-width:100% !important;padding-top:1.2rem !important;}
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"]{display:none;}
[data-testid="stSidebar"]{display:none!important}

/* 便利贴小卡 */
.sticky{position:relative;border-radius:4px 4px 10px 10px;padding:1rem 1.1rem;
  box-shadow:0 4px 8px rgba(80,60,20,.12);font-family:'Ma Shan Zheng',cursive;font-size:1.15rem;
  margin-bottom:.8rem;transform:rotate(var(--r,0deg));}
.sticky::before{content:'';position:absolute;top:-9px;left:14px;right:14px;height:16px;background:var(--tape);transform:rotate(-1deg);}
.sticky.y{background:var(--sticky-y)}
.sticky.p{background:var(--sticky-p)}
.sticky.b{background:var(--sticky-b)}
.sticky.g{background:var(--sticky-g)}

/* 手绘纸张卡 */
.paper-card{position:relative;background:var(--paper);border:2px solid var(--paper-edge);
  border-radius:16px;padding:1.2rem 1.3rem;margin-bottom:1rem;
  box-shadow:0 3px 0 rgba(90,70,40,.08),0 10px 22px rgba(90,70,40,.08);}
.tape{position:absolute;top:-9px;left:50%;transform:translateX(-50%) rotate(-2deg);
  width:80px;height:20px;background:var(--tape);box-shadow:0 1px 2px rgba(0,0,0,.08);}
.pp-title{font-family:'Ma Shan Zheng',cursive;color:var(--ink);}
.pp-sub{font-family:'ZCOOL XiaoWei',serif;color:var(--ink-soft);font-size:.9rem;margin-top:.1rem;}

/* 手绘按钮 */
button[kind="primary"], [data-testid="stBaseButton-primary"]{
  font-family:'Ma Shan Zheng',cursive !important;color:#fff !important;
  background:var(--pen) !important;border:2px solid var(--pen-dark) !important;
  border-radius:12px 10px 13px 9px !important;
  box-shadow:0 2px 0 rgba(0,0,0,.25) !important;
  transform:rotate(-.4deg) !important;letter-spacing:.05em;
}
button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover{filter:brightness(1.06) !important;}
button[kind="primary"]:active{transform:translateY(1px) rotate(-.4deg) !important;box-shadow:0 1px 0 rgba(0,0,0,.25)!important;}
[data-testid="stBaseButton-secondary"], button[kind="secondary"]{
  font-family:'Ma Shan Zheng',cursive !important;color:var(--ink) !important;
  background:var(--paper) !important;border:2px solid var(--ink-soft) !important;
  border-radius:12px 10px 13px 9px !important;box-shadow:0 2px 0 rgba(0,0,0,.12)!important;
}
[data-testid="stBaseButton-secondary"]:hover, button[kind="secondary"]:hover{
  border-color:var(--pen) !important;color:var(--pen) !important;filter:brightness(.98)!important;}
[data-testid="stBaseButton-secondary"]:active{transform:translateY(1px)!important;box-shadow:0 1px 0 rgba(0,0,0,.12)!important;}

/* 输入 = 圆珠笔虚线 */
[data-testid="stTextInput"] input{
  background:transparent !important;border:none !important;
  border-bottom:2px dashed var(--ink-faint) !important;border-radius:0 !important;
  font-family:'ZCOOL XiaoWei',serif !important;color:var(--ink) !important;
  box-shadow:none !important;
}
[data-testid="stTextInput"] input:focus{
  border-bottom-style:solid !important;border-bottom-color:var(--pen) !important;}
[data-testid="stTextInput"] input::placeholder{color:var(--ink-faint) !important;}
[data-testid="stTextInput"] label, [data-testid="stTextArea"] label, [data-testid="stFileUploader"] label{
  font-family:'Ma Shan Zheng',cursive !important;color:var(--ink-soft) !important;}
[data-testid="stTextArea"] textarea{
  background:repeating-linear-gradient(transparent,transparent 30px,var(--paper-edge) 30px,var(--paper-edge) 31px),#fffdf6 !important;
  border:2px solid var(--paper-edge) !important;border-radius:12px !important;
  font-family:'ZCOOL XiaoWei',serif !important;color:var(--ink) !important;
  box-shadow:0 3px 0 rgba(90,70,40,.06)!important;
}
[data-testid="stTextArea"] textarea:focus{border-color:var(--pen) !important;}

/* 选择框/多选 = 纸张 */
[data-testid="stSelectbox"] div[data-baseweb="select"]>div, [data-testid="stMultiSelect"] div[data-baseweb="select"]>div{
  background:var(--paper-2) !important;border:2px solid var(--paper-edge) !important;
  border-radius:12px !important;font-family:'ZCOOL XiaoWei',serif !important;}
[data-testid="stSelectbox"] div[data-baseweb="select"]>div:hover{border-color:var(--ink-faint)!important;}
[data-testid="stRadio"] label p, [data-testid="stCheckbox"] label p{font-family:'ZCOOL XiaoWei',serif !important;color:var(--ink)!important;}

/* 页签 = 手帐小签 */
[data-testid="stTabs"]{gap:.4rem}
[data-testid="stTabs"] button[data-baseweb="tab"]{
  font-family:'Ma Shan Zheng',cursive !important;font-size:1.05rem !important;
  color:var(--ink-soft) !important;background:var(--paper) !important;
  border:2px solid var(--paper-edge) !important;border-top:none !important;border-radius:0 0 10px 10px !important;
  padding:.35rem 1rem !important;margin:0 -2px !important;box-shadow:0 2px 0 rgba(90,70,40,.08)!important;
}
[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"]{
  color:var(--ink) !important;background:var(--sticky-y) !important;border-color:#e0c76f !important;}
[data-testid="stTabs"] div[data-baseweb="tab-highlight"]{display:none!important}

/* 折叠 = 纸张卡 */
[data-testid="stExpander"] details{
  background:var(--paper) !important;border:2px solid var(--paper-edge) !important;
  border-radius:14px !important;box-shadow:0 3px 0 rgba(90,70,40,.07)!important;}
[data-testid="stExpander"] summary{font-family:'Ma Shan Zheng',cursive !important;color:var(--ink)!important;border-radius:12px;padding:.5rem .8rem!important;}

/* 指标 = 便利贴 */
[data-testid="stMetric"]{
  background:var(--paper) !important;border:2px solid var(--paper-edge) !important;
  border-radius:14px !important;padding:.7rem 1rem !important;
  box-shadow:0 2px 0 rgba(90,70,40,.07)!important;
}
[data-testid="stMetric"] [data-testid="stMetricLabel"]{font-family:'Ma Shan Zheng',cursive !important;color:var(--ink-soft)!important;}
[data-testid="stMetric"] [data-testid="stMetricValue"]{font-family:'Caveat',cursive !important;font-weight:700;color:var(--ink)!important;}

/* 对话气泡 = 便利贴 */
[data-testid="stChatMessage"]{background:transparent!important;border:none!important;padding:0 .4rem!important;}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"]{
  position:relative;border-radius:6px;padding:.55rem .9rem;font-size:.95rem;
  box-shadow:0 2px 0 rgba(80,60,20,.08);}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdownContainer"]{
  background:var(--sticky-b) !important;border:1.5px solid #9cc6ec;}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stMarkdownContainer"]{
  background:var(--sticky-y) !important;border:1.5px solid #e6c87a;}
[data-testid="stChatInput"] textarea{
  background:var(--paper) !important;border:2px solid var(--paper-edge) !important;
  border-bottom:2px dashed var(--ink-faint) !important;border-radius:14px 14px 0 0 !important;
  font-family:'ZCOOL XiaoWei',serif !important;}
[data-testid="stChatInput"] textarea:focus{border-bottom-style:solid!important;border-bottom-color:var(--pen)!important;}

/* 进度条 = 手绘填充 */
[data-testid="stProgress"] div[role="progressbar"]{background:var(--paper-edge)!important;border-radius:6px!important;}
[data-testid="stProgress"] div[role="progressbar"]>div{background:var(--pen)!important;border-radius:6px!important;}

/* 提示条 = 便利贴 */
[data-testid="stAlert"], .stAlert{
  border-radius:12px !important;border-style:solid!important;border-width:2px!important;
  box-shadow:0 2px 0 rgba(80,60,20,.08)!important;
}
[data-testid="stAlert"] [data-testid="stAlertIcon"]{color:inherit!important;}
[data-testid="stAlert"] p, [data-testid="stAlert"] li{color:var(--ink)!important;font-family:'ZCOOL XiaoWei',serif!important;}

/* 标题/文本 */
h1,h2,h3,h4{font-family:'Ma Shan Zheng',cursive!important;color:var(--ink)!important;}
p, li, [data-testid="stCaptionContainer"]{font-family:'ZCOOL XiaoWei',serif!important;color:var(--ink)!important;}
hr{background:var(--paper-edge)!important;}
a{color:var(--pen)!important;text-decoration-style:dashed;}
[data-testid="stMarkdownContainer"] p{color:var(--ink)!important;font-family:'ZCOOL XiaoWei',serif!important;}

/* 上传区域 */
[data-testid="stFileUploader"] section{
  background:#fffdf6 !important;border:2px dashed var(--ink-faint) !important;
  border-radius:14px !important;}

/* 表格 */
[data-testid="stTable"] {border-radius:12px!important;overflow:hidden;border:2px solid var(--paper-edge)!important;}
[data-testid="stTable"] thead tr th{background:var(--paper-2)!important;font-family:'Ma Shan Zheng',cursive!important;}
[data-testid="stTable"] tbody tr td{background:var(--paper)!important;font-family:'ZCOOL XiaoWei',serif!important;}
[data-testid="stDataFrame"]{border-radius:12px!important;border:2px solid var(--paper-edge)!important;}
</style>
"""


# ═══════════════════════════════════════════════════════════════
#  登录后主皮肤（含侧边栏 + 全部模块控件）
# ═══════════════════════════════════════════════════════════════
MAIN_CSS = r"""
<style>
:root{
  --paper:#fbf5e9; --paper-2:#f6eeda; --paper-edge:#e9dcc3;
  --ink:#3b3226; --ink-soft:#7a6f5e; --ink-faint:#b3a68e;
  --sticky-y:#ffe9a8; --sticky-p:#ffd6e7; --sticky-b:#d9efff; --sticky-g:#d9f5dc;
  --pen:#2f5d8f; --pen-dark:#224566; --pen-red:#c0504d; --pen-green:#4a7a4c; --pen-orange:#c07a3a;
  --tape:rgba(255,255,255,.55);
}
[data-testid="stApp"], .stApp{
  background:
    radial-gradient(circle at 15% 10%, rgba(200,180,140,.12), transparent 40%),
    radial-gradient(circle at 85% 90%, rgba(200,180,140,.10), transparent 45%),
    var(--paper) !important;
  color:var(--ink) !important;
}
[data-testid="stApp"]::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.5;
  background-image:radial-gradient(rgba(150,130,100,.35) .6px, transparent .6px);background-size:3px 3px;}
/* 隐藏 Streamlit 原生顶栏，保持手帐干净。注意：DOM 仍保留，
   侧边栏切换按钮(stExpandSidebarButton/stSidebarCollapseButton)依旧可被程序化点击 */
[data-testid="stHeader"]{display:none!important}
[data-testid="stToolbar"]{display:none!important}
/* 自定义侧边栏切换按钮：固定在左上角，任何屏幕尺寸都清晰可见、可点 */
.sb-toggle{
  position:fixed;left:.6rem;top:.6rem;z-index:2147483000;
  display:inline-flex;align-items:center;gap:.35rem;
  padding:.42rem .8rem;border-radius:999px;
  background:var(--sticky-y);border:2px solid #e0c76f;
  box-shadow:0 3px 0 rgba(80,60,20,.2),0 8px 16px rgba(80,60,20,.18);
  font-family:'Ma Shan Zheng',cursive;font-size:1.05rem;color:#2b2b2b;
  cursor:pointer;user-select:none;-webkit-user-select:none;touch-action:manipulation;
  transition:transform .12s,background .12s;white-space:nowrap;
}
.sb-toggle:hover{background:#ffe29c;}
.sb-toggle:active{transform:scale(.94);}
.sb-toggle .sb-ico{font-size:1.1rem;line-height:1;}

/* toast 适配手帐浅色主题（默认深色在浅色背景下看不清） */
[data-testid="stToast"]{
  background:#fffdf4!important;color:#2b2b2b!important;
  border:2px solid #e0c76f!important;border-radius:14px!important;
  box-shadow:0 6px 18px rgba(80,60,20,.22)!important;
}
[data-testid="stToast"] [data-testid="stToastText"]{color:#2b2b2b!important;font-family:'Ma Shan Zheng',cursive!important;}
[data-testid="stToast"] [data-testid="stToastDynamicIcon"]{color:var(--pen)!important;}
[data-testid="stToast"] button{color:#2b2b2b!important;background:transparent!important;}

/* 笔记完整内容：只读纸张盒子（替代有 key/value 冲突的 disabled text_area） */
.note-full-content{
  white-space:pre-wrap;word-break:break-word;
  background:#fffdf6;border:2px solid var(--paper-edge);border-radius:12px;
  padding:.85rem 1rem;max-height:320px;overflow-y:auto;
  font-family:'ZCOOL XiaoWei',serif;color:var(--ink);line-height:1.75;font-size:1rem;
  box-shadow:inset 0 2px 6px rgba(90,70,40,.06);
}

/* ── 侧边栏 = 牛皮纸装订册 ── */
[data-testid="stSidebar"]{
  background:
    radial-gradient(circle at 20% 15%, rgba(210,190,150,.15), transparent 55%),
    var(--paper-2) !important;
  border-right:3px double var(--paper-edge) !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"]{padding-top:.5rem!important;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:var(--ink)!important;}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3{
  font-family:'Ma Shan Zheng',cursive!important;color:var(--ink)!important;}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"]{font-family:'Caveat',cursive!important;color:var(--ink-soft)!important;font-size:1rem!important;}

/* 侧边栏导航 = 手帐页签 */
[data-testid="stSidebar"] [data-testid="stRadio"]>div{flex-direction:column;gap:.35rem!important;}
[data-testid="stSidebar"] [data-testid="stRadio"] label{
  font-family:'Ma Shan Zheng',cursive!important;font-size:1.05rem!important;
  color:var(--ink-soft)!important;background:transparent!important;
  border:2px solid transparent!important;border-radius:10px!important;padding:.25rem .8rem!important;
  transition:.12s;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{border-color:var(--paper-edge)!important;color:var(--pen)!important;}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked){
  background:var(--sticky-y)!important;border-color:#e0c76f!important;color:var(--ink)!important;
  box-shadow:0 2px 0 rgba(80,60,20,.10)!important;
}
[data-testid="stSidebar"] [data-testid="stMetric"]{
  background:var(--sticky-g)!important;border:2px solid #b3d8b8!important;border-radius:12px!important;padding:.5rem .8rem!important;
  box-shadow:0 2px 0 rgba(80,60,20,.08)!important;transform:rotate(-.5deg);
}
[data-testid="stSidebar"] [data-testid="stMetric"] [data-testid="stMetricValue"]{font-family:'Caveat',cursive!important;font-weight:700;color:var(--pen-green)!important;}
[data-testid="stSidebar"] [data-testid="stMetric"] [data-testid="stMetricLabel"]{font-family:'Ma Shan Zheng',cursive!important;color:var(--ink-soft)!important;}
[data-testid="stSidebar"] [data-testid="stDivider"]{background:var(--paper-edge)!important;}

/* ── 手帐组件（页面内） ── */
.sticky{position:relative;border-radius:4px 4px 10px 10px;padding:1rem 1.1rem;
  box-shadow:0 4px 8px rgba(80,60,20,.12);font-family:'Ma Shan Zheng',cursive;font-size:1.15rem;
  margin-bottom:.8rem;transform:rotate(var(--r,0deg));}
.sticky::before{content:'';position:absolute;top:-9px;left:14px;right:14px;height:16px;background:var(--tape);transform:rotate(-1deg);}
.sticky.y{background:var(--sticky-y)}
.sticky.p{background:var(--sticky-p)}
.sticky.b{background:var(--sticky-b)}
.sticky.g{background:var(--sticky-g)}
.paper-card{position:relative;background:var(--paper);border:2px solid var(--paper-edge);
  border-radius:16px;padding:1.2rem 1.3rem;margin-bottom:1rem;
  box-shadow:0 3px 0 rgba(90,70,40,.08),0 10px 22px rgba(90,70,40,.08);}
.tape{position:absolute;top:-9px;left:50%;transform:translateX(-50%) rotate(-2deg);
  width:80px;height:20px;background:var(--tape);box-shadow:0 1px 2px rgba(0,0,0,.08);}
.pp-title{font-family:'Ma Shan Zheng',cursive;color:var(--ink);}
.pp-sub{font-family:'ZCOOL XiaoWei',serif;color:var(--ink-soft);font-size:.9rem;margin-top:.1rem;}
.pp-tape{display:inline-block;position:relative;background:var(--paper-2);border:2px solid var(--paper-edge);
  border-radius:10px;padding:.2rem .9rem;box-shadow:0 2px 0 rgba(90,70,40,.08);
  font-family:'Caveat',cursive;color:var(--ink-soft);transform:rotate(-.6deg);}

/* 手绘按钮 */
[data-testid="stBaseButton-primary"], button[kind="primary"]{
  font-family:'Ma Shan Zheng',cursive !important;color:#fff!important;
  background:var(--pen) !important;border:2px solid var(--pen-dark) !important;
  border-radius:12px 10px 13px 9px !important;
  box-shadow:0 2px 0 rgba(0,0,0,.25)!important;
  transform:rotate(-.4deg)!important;letter-spacing:.05em;
}
[data-testid="stBaseButton-primary"]:hover, button[kind="primary"]:hover{filter:brightness(1.06)!important;}
[data-testid="stBaseButton-primary"]:active{transform:translateY(1px) rotate(-.4deg)!important;}
[data-testid="stBaseButton-secondary"], button[kind="secondary"]{
  font-family:'Ma Shan Zheng',cursive !important;color:var(--ink)!important;
  background:var(--paper) !important;border:2px solid var(--ink-soft) !important;
  border-radius:12px 10px 13px 9px !important;box-shadow:0 2px 0 rgba(0,0,0,.12)!important;
}
[data-testid="stBaseButton-secondary"]:hover, button[kind="secondary"]:hover{border-color:var(--pen)!important;color:var(--pen)!important;}

/* 输入 = 米白纸卡 + 笔划线 */
[data-testid="stTextInput"] input{
  background:#fffdf6 !important;border:2px solid var(--paper-edge)!important;
  border-bottom:2px dashed var(--pen)!important;border-radius:10px!important;
  padding:.5rem .7rem!important;
  font-family:'ZCOOL XiaoWei',serif !important;font-size:1.05rem!important;
  color:var(--ink) !important;box-shadow:0 2px 0 rgba(90,70,40,.06)!important;
}
[data-testid="stTextInput"] input:focus{border-bottom-style:solid!important;border-bottom-color:var(--pen)!important;background:#fffef9!important;}
[data-testid="stTextInput"] input::placeholder{color:var(--ink-soft)!important;}
[data-testid="stTextInput"] label, [data-testid="stTextArea"] label, [data-testid="stFileUploader"] label,
[data-testid="stSelectbox"] label, [data-testid="stMultiSelect"] label, [data-testid="stSlider"] label{
  font-family:'Ma Shan Zheng',cursive !important;color:var(--ink-soft)!important;}
[data-testid="stTextArea"] textarea{
  background:repeating-linear-gradient(transparent,transparent 30px,var(--paper-edge) 30px,var(--paper-edge) 31px),#fffdf6 !important;
  border:2px solid var(--paper-edge) !important;border-radius:12px !important;
  font-family:'ZCOOL XiaoWei',serif !important;color:var(--ink) !important;
  box-shadow:0 3px 0 rgba(90,70,40,.06)!important;
}
[data-testid="stTextArea"] textarea:focus{border-color:var(--pen)!important;}

[data-testid="stSelectbox"] div[data-baseweb="select"]>div, [data-testid="stMultiSelect"] div[data-baseweb="select"]>div{
  background:var(--paper-2) !important;border:2px solid var(--paper-edge) !important;
  border-radius:12px !important;font-family:'ZCOOL XiaoWei',serif !important;}
[data-testid="stSelectbox"] div[data-baseweb="select"]>div:hover{border-color:var(--ink-faint)!important;}
[data-testid="stRadio"] label p, [data-testid="stCheckbox"] label p{font-family:'ZCOOL XiaoWei',serif!important;color:var(--ink)!important;}
[data-testid="stToggle"] label p{font-family:'ZCOOL XiaoWei',serif!important;color:var(--ink)!important;}
[data-testid="stSlider"] [role="slider"]{background:var(--pen)!important;border:2px solid var(--pen-dark)!important;}
[data-testid="stSlider"] [data-testid="stSliderThumbValue"]{font-family:'Caveat',cursive!important;}

/* 页签 */
[data-testid="stTabs"] button[data-baseweb="tab"]{
  font-family:'Ma Shan Zheng',cursive !important;color:var(--ink-soft)!important;
  background:var(--paper)!important;border:2px solid var(--paper-edge)!important;border-top:none!important;
  border-radius:0 0 10px 10px !important;padding:.35rem 1rem!important;margin:0 -2px!important;
  box-shadow:0 2px 0 rgba(90,70,40,.08)!important;
}
[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"]{color:var(--ink)!important;background:var(--sticky-y)!important;border-color:#e0c76f!important;}
[data-testid="stTabs"] div[data-baseweb="tab-highlight"]{display:none!important}

/* 折叠 = 纸张卡 */
[data-testid="stExpander"] details{background:var(--paper)!important;border:2px solid var(--paper-edge)!important;
  border-radius:14px!important;box-shadow:0 3px 0 rgba(90,70,40,.07)!important;}
[data-testid="stExpander"] summary{font-family:'Ma Shan Zheng',cursive!important;border-radius:12px;padding:.5rem .8rem!important;}

/* 手帐卡片容器：在 st.container() 内放 <span class="hb-card"></span> 即可给整块套上纸卡框 */
.hb-card,.hb-lines{display:none!important;}
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .hb-card){
  background:var(--paper)!important;
  border:2px solid var(--paper-edge)!important;
  border-radius:14px!important;
  padding:.85rem 1rem!important;
  box-shadow:0 3px 0 rgba(90,70,40,.07)!important;
}
/* 隐藏标记元素自身占位，让内容从容器顶部开始 */
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .hb-card) > [data-testid="stElementContainer"]:first-child{
  display:none!important;
}
/* 加 .hb-lines 标记 → 笔记本横格线；行高与线距一致，让文字坐在线上 */
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .hb-lines){
  background:repeating-linear-gradient(transparent 0,transparent 33px,var(--paper-edge) 33px,var(--paper-edge) 34px),var(--paper)!important;
  padding:0 1rem!important;
}
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .hb-lines) [data-testid="stMarkdownContainer"] p{
  line-height:34px!important;margin:0!important;
}
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .hb-lines) [data-testid="stCaptionContainer"]{
  line-height:34px!important;margin:0!important;
}

/* 指标 */
[data-testid="stMetric"]{background:var(--paper)!important;border:2px solid var(--paper-edge)!important;
  border-radius:14px!important;padding:.7rem 1rem!important;box-shadow:0 2px 0 rgba(90,70,40,.07)!important;}
[data-testid="stMetric"] [data-testid="stMetricLabel"]{font-family:'Ma Shan Zheng',cursive!important;color:var(--ink-soft)!important;}
[data-testid="stMetric"] [data-testid="stMetricValue"]{font-family:'Caveat',cursive!important;font-weight:700;color:var(--ink)!important;}

/* 对话 */
[data-testid="stChatMessage"]{background:transparent!important;border:none!important;padding:0 .4rem!important;}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"]{position:relative;border-radius:6px;padding:.55rem .9rem;
  box-shadow:0 2px 0 rgba(80,60,20,.08);}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdownContainer"]{background:var(--sticky-b)!important;border:1.5px solid #9cc6ec;}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stMarkdownContainer"]{background:var(--sticky-y)!important;border:1.5px solid #e6c87a;}
/* 聊天输入 = 手帐便签输入条（浅色底、整框圆角，去掉突兀的深色底栏） */
[data-testid="stBottom"], [data-testid="stBottomBlockContainer"]{
  background:var(--paper)!important;}
[data-testid="stChatInput"]{
  background:var(--paper)!important;
  border:2px solid var(--paper-edge)!important;
  border-radius:16px!important;
  box-shadow:0 3px 0 rgba(90,70,40,.08)!important;
  transition:border-color .18s cubic-bezier(.22,.61,.36,1),box-shadow .18s cubic-bezier(.22,.61,.36,1);}
[data-testid="stChatInput"]:focus-within{
  border-color:var(--pen)!important;
  box-shadow:0 3px 0 rgba(47,93,143,.20)!important;}
[data-testid="stChatInput"] textarea{
  background:transparent!important;border:none!important;border-radius:12px!important;
  font-family:'ZCOOL XiaoWei',serif!important;color:var(--ink)!important;box-shadow:none!important;}
[data-testid="stChatInput"] textarea::placeholder{color:var(--ink-soft)!important;}
[data-testid="stChatInputSubmitButton"] button, [data-testid="stChatInput"] button{
  background:var(--pen)!important;color:#fff!important;
  border:2px solid var(--pen-dark)!important;border-radius:12px!important;}
[data-testid="stChatInputSubmitButton"] button:hover{filter:brightness(1.08)!important;}

/* 进度条 */
[data-testid="stProgress"] div[role="progressbar"]{background:var(--paper-edge)!important;border-radius:6px!important;}
[data-testid="stProgress"] div[role="progressbar"]>div{background:var(--pen)!important;border-radius:6px!important;}

/* 提示条 */
[data-testid="stAlert"], .stAlert{border-radius:12px!important;border-style:solid!important;border-width:2px!important;
  box-shadow:0 2px 0 rgba(80,60,20,.08)!important;}
[data-testid="stAlert"] p, [data-testid="stAlert"] li{color:var(--ink)!important;font-family:'ZCOOL XiaoWei',serif!important;}

/* 标题/文本 */
h1,h2,h3,h4{font-family:'Ma Shan Zheng',cursive!important;color:var(--ink)!important;}
p, li, [data-testid="stCaptionContainer"]{font-family:'ZCOOL XiaoWei',serif!important;color:var(--ink)!important;}
hr{border-color:var(--paper-edge)!important;}
a{color:var(--pen)!important;text-decoration-style:dashed;}
[data-testid="stMarkdownContainer"] p{color:var(--ink)!important;font-family:'ZCOOL XiaoWei',serif!important;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:var(--ink)!important;}

/* 上传 / 表格 */
[data-testid="stFileUploader"] section{background:#fffdf6!important;border:2px dashed var(--ink-faint)!important;border-radius:14px!important;}
[data-testid="stTable"] {border-radius:12px!important;overflow:hidden;border:2px solid var(--paper-edge)!important;}
[data-testid="stTable"] thead tr th{background:var(--paper-2)!important;font-family:'Ma Shan Zheng',cursive!important;}
[data-testid="stTable"] tbody tr td{background:var(--paper)!important;font-family:'ZCOOL XiaoWei',serif!important;}
[data-testid="stDataFrame"]{border-radius:12px!important;border:2px solid var(--paper-edge)!important;}

/* 便利贴搜索卡（知识广场） */
.pz-search{display:flex;gap:.5rem;align-items:flex-end}
.pz-item{position:relative;background:#fffdf6;border:2px solid var(--paper-edge);border-radius:12px;
  padding:.7rem .9rem;margin-bottom:.6rem;box-shadow:0 2px 0 rgba(90,70,40,.05);}
.pz-item .no{font-family:'Permanent Marker',cursive;color:var(--ink-faint);}
.zoom-in{animation:pe .25s ease}
@keyframes pe{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@media(max-width:820px){[data-testid="stMetric"]{padding:.4rem .6rem!important}}
</style>
"""


# ═══════════════════════════════════════════════════════════════
#  手帐风微动效层（纯 CSS，无 JS）
#  —— 在 LOGIN_CSS / MAIN_CSS 之后注入，靠后覆盖以叠加动效
# ═══════════════════════════════════════════════════════════════
ANIM_CSS = r"""
<style>
:root{ --ease-soft:cubic-bezier(.22,.61,.36,1); }

/* 1) 淡入上浮：纸张卡 / 搜索条目 / 只读内容盒
      用独立的 translate 属性承载上浮，避免与 hover 的 transform 抢占 */
@keyframes hbFadeUp{from{opacity:0;translate:0 8px}to{opacity:1;translate:0 0}}
.paper-card,.pz-item,.note-full-content{animation:hbFadeUp .4s var(--ease-soft) both;}

/* 1b) 主卡片容器（页面里 <span class="hb-card"> 的父容器）也淡入 + 悬停轻抬
       —— 这是 app 里真正用到的卡片，务必覆盖 */
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .hb-card){
  animation:hbFadeUp .45s var(--ease-soft) both;
  transition:box-shadow .25s var(--ease-soft),transform .25s var(--ease-soft);}
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .hb-card):hover{
  transform:translateY(-2px);box-shadow:0 8px 18px rgba(90,70,40,.16)!important;}
/* 横格线卡片：内容区整体淡入（避免滚动条跳动，不加 hover 位移） */
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .hb-lines){
  animation:hbFadeUp .45s var(--ease-soft) both;}

/* 2) 便签飘动：用独立的 translate 属性，避免覆盖 .sticky 自身的 rotate 倾斜 */
@keyframes hbFloat{0%,100%{translate:0 0}50%{translate:0 -4px}}
.sticky{animation:hbFloat 4.6s ease-in-out infinite;}
.sticky:nth-of-type(2n){animation-duration:6.2s;animation-delay:-1.4s;}
.sticky:nth-of-type(3n){animation-duration:5.6s;animation-delay:-2.3s;}

/* 3) 卡片 hover 抬起 + 投影；便签 hover 停住并扶正 */
.paper-card,.pz-item,.sticky,.note-full-content{
  transition:box-shadow .25s var(--ease-soft),transform .25s var(--ease-soft);}
.paper-card:hover{transform:translateY(-3px);box-shadow:0 6px 0 rgba(90,70,40,.08),0 12px 24px rgba(90,70,40,.16);}
.pz-item:hover{transform:translateY(-2px);box-shadow:0 10px 20px rgba(90,70,40,.16);}
.sticky:hover{animation-play-state:paused;transform:rotate(0deg) translateY(-3px);
  box-shadow:0 12px 20px rgba(80,60,20,.22);}
.note-full-content:hover{box-shadow:inset 0 2px 6px rgba(90,70,40,.06),0 8px 18px rgba(90,70,40,.14);}

/* 4) 按钮：主按钮渐变 + 悬停发光 + 按压回弹；次按钮轻抬 */
[data-testid="stBaseButton-primary"],button[kind="primary"]{
  background:linear-gradient(180deg,#3a6da3 0%,var(--pen) 55%,var(--pen-dark) 100%)!important;
  transition:transform .12s var(--ease-soft),box-shadow .12s var(--ease-soft),filter .15s!important;}
[data-testid="stBaseButton-primary"]:hover,button[kind="primary"]:hover{
  filter:brightness(1.08) saturate(1.05)!important;
  box-shadow:0 5px 12px rgba(34,69,102,.38)!important;}
[data-testid="stBaseButton-primary"]:active,button[kind="primary"]:active{
  transform:translateY(2px) rotate(-.4deg) scale(.985)!important;
  box-shadow:0 0 0 rgba(0,0,0,.2)!important;}
[data-testid="stBaseButton-secondary"],button[kind="secondary"]{
  transition:transform .12s var(--ease-soft),box-shadow .15s,border-color .15s,color .15s!important;}
[data-testid="stBaseButton-secondary"]:hover,button[kind="secondary"]:hover{
  transform:translateY(-1px)!important;box-shadow:0 4px 9px rgba(90,70,40,.16)!important;}
[data-testid="stBaseButton-secondary"]:active{
  transform:translateY(1px) scale(.99)!important;box-shadow:0 1px 0 rgba(0,0,0,.12)!important;}

/* 5) 指标卡 hover 轻抬 */
[data-testid="stMetric"]{transition:transform .2s var(--ease-soft),box-shadow .2s var(--ease-soft);}
[data-testid="stMetric"]:hover{transform:translateY(-2px);box-shadow:0 6px 14px rgba(90,70,40,.16)!important;}

/* 6) 进度条：三色渐变 + 光泽流动 + 宽度平滑增长 */
@keyframes hbFlow{from{background-position:0 0}to{background-position:200% 0}}
[data-testid="stProgress"] div[role="progressbar"]>div{
  background:linear-gradient(90deg,var(--pen),var(--pen-green),var(--pen))!important;
  background-size:200% 100%!important;animation:hbFlow 2.4s linear infinite;
  transition:width .5s var(--ease-soft)!important;}

/* 7) 加载骨架：<span class="hb-skeleton [w60|w80]">
      —— 供页面在等待时铺设占位条；同时美化原生 spinner */
@keyframes hbShimmer{from{background-position:100% 0}to{background-position:0 0}}
.hb-skeleton{display:block;height:14px;border-radius:7px;margin:.35rem 0;
  background:linear-gradient(90deg,var(--paper-edge) 25%,#fff8e8 37%,var(--paper-edge) 63%);
  background-size:400% 100%;animation:hbShimmer 1.3s ease-in-out infinite;}
.hb-skeleton.w40{width:40%}.hb-skeleton.w60{width:60%}.hb-skeleton.w80{width:80%}
[data-testid="stSpinner"] p{font-family:'Ma Shan Zheng',cursive!important;color:var(--ink-soft)!important;}
[data-testid="stSpinner"] > div{border-top-color:var(--pen)!important;}

/* 8) 侧边栏导航：悬停右移、选中项柔和过渡 */
[data-testid="stSidebar"] [data-testid="stRadio"] label{
  transition:transform .15s var(--ease-soft),background .15s,border-color .15s,color .15s;}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{transform:translateX(3px);}

/* 9) 页签悬停轻抬 */
[data-testid="stTabs"] button[data-baseweb="tab"]{transition:transform .15s var(--ease-soft),background .15s,color .15s;}
[data-testid="stTabs"] button[data-baseweb="tab"]:hover{transform:translateY(-1px);}

/* 10) 输入聚焦：下划线阴影渐显 */
[data-testid="stTextInput"] input{transition:border-color .18s,box-shadow .18s,background .18s!important;}
[data-testid="stTextInput"] input:focus{box-shadow:0 3px 0 rgba(47,93,143,.22)!important;}

/* 11) 复习「翻开笔记」：点开始复习后，内容像翻页一样掀开浮现
      只命中内层容器（它把 .hb-flip 作为第一个标记），避免外层卡片一起翻 */
.hb-flip{display:none!important;}
@keyframes hbFlipOpen{
  from{opacity:0;transform-origin:left center;
       transform:perspective(1600px) rotateY(-30deg) translateX(-8px);}
  to{opacity:1;transform:none;}
}
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"]:first-child .hb-flip){
  animation:hbFlipOpen .55s cubic-bezier(.22,.61,.36,1) both;
  background:#fffdf6!important;
  border:2px solid var(--paper-edge)!important;
  border-left:6px solid #d8c7a4!important;
  border-radius:10px!important;
  padding:.9rem 1rem .9rem 1.1rem!important;
  margin-top:.5rem!important;
  box-shadow:-16px 10px 30px rgba(90,70,40,.20)!important;
}

/* 无障碍：尊重系统「减少动态效果」 */
@media (prefers-reduced-motion: reduce){
  .paper-card,.pz-item,.note-full-content,.sticky,.hb-skeleton,.block-container,
  [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"]:first-child .hb-flip),
  [data-testid="stProgress"] div[role="progressbar"]>div{animation:none!important;}
}
</style>
"""


def inject_fonts():
    st.markdown(FONT_LINK, unsafe_allow_html=True)


def apply_login_theme():
    """登录页皮肤（替换原深色玻璃）"""
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)
    st.markdown(ANIM_CSS, unsafe_allow_html=True)


def apply_main_theme():
    """登录后全局皮肤（含侧边栏 + 全部模块）"""
    inject_fonts()
    st.markdown(MAIN_CSS, unsafe_allow_html=True)
    st.markdown(ANIM_CSS, unsafe_allow_html=True)


def enter_effect(kind: str = "page"):
    """页面/登录「进入」动效 —— 只在调用它的那一次 rerun 生效。

    kind="page" —— 切换模块：主内容淡入上浮
    kind="book" —— 登录成功：主内容如翻开笔记本般从左侧掀开
    只作用于 .block-container（主内容区）；固定元素（菜单按钮/toast）挂在
    body 上，不在该容器内，故不受位移影响。
    """
    if kind == "book":
        css = (
            "@keyframes hbBookOpen{"
            "from{opacity:0;transform-origin:left center;"
            "transform:perspective(1400px) rotateY(-16deg) translateX(-16px);}"
            "to{opacity:1;transform:none;}}"
            ".block-container{animation:hbBookOpen .62s cubic-bezier(.22,.61,.36,1) both;}"
        )
    else:
        css = (
            "@keyframes hbPageIn{from{opacity:0;translate:0 14px}to{opacity:1;translate:0 0}}"
            ".block-container{animation:hbPageIn .42s cubic-bezier(.22,.61,.36,1) both;}"
        )
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str = None):
    """页面顶部手帐标题栏：图标 + 手写大标题 + 便利贴副标题"""
    sub = ""
    if subtitle:
        sub = f'<div class="pp-sub" style="font-family:\'Caveat\',cursive;font-size:1.05rem;margin-top:.15rem">{subtitle}</div>'
    html = (
        '<div style="display:flex;align-items:baseline;gap:.8rem;'
        'margin:.2rem 0 .4rem;flex-wrap:wrap">'
        f'<span style="font-size:1.9rem">{icon}</span>'
        f'<span class="pp-title" style="font-size:1.9rem">{title}</span>'
        f'{sub}</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def paper_card(inner: str, with_tape: bool = True):
    tape = '<div class="tape"></div>' if with_tape else ""
    return f'<div class="paper-card">{tape}{inner}</div>'


def render_paper_card(inner: str, with_tape: bool = True):
    st.markdown(paper_card(inner, with_tape), unsafe_allow_html=True)


def sticky(text: str, color: str = "y", angle: float = 0, size: str = ""):
    s = f'font-size:{size}' if size else ""
    return f'<div class="sticky {color}" style="--r:{angle}deg;{s}">{text}</div>'


def render_sticky(text: str, color: str = "y", angle: float = 0):
    st.markdown(sticky(text, color, angle), unsafe_allow_html=True)


def notebook_line():
    """页内手绘分隔线"""
    st.markdown(
        '<div style="position:relative;height:14px;margin:.4rem 0;'
        'background:repeating-linear-gradient(0deg, transparent 0 6px, '
        'var(--paper-edge) 6px 7px);"></div>',
        unsafe_allow_html=True,
    )