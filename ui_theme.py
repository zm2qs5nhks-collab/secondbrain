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
[data-testid="stToolbar"]{display:none}

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
[data-testid="stChatInput"] textarea{background:var(--paper)!important;border:2px solid var(--paper-edge)!important;
  border-bottom:2px dashed var(--ink-faint)!important;border-radius:14px 14px 0 0!important;
  font-family:'ZCOOL XiaoWei',serif!important;}
[data-testid="stChatInput"] textarea:focus{border-bottom-style:solid!important;border-bottom-color:var(--pen)!important;}

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


def inject_fonts():
    st.markdown(FONT_LINK, unsafe_allow_html=True)


def apply_login_theme():
    """登录页皮肤（替换原深色玻璃）"""
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)


def apply_main_theme():
    """登录后全局皮肤（含侧边栏 + 全部模块）"""
    inject_fonts()
    st.markdown(MAIN_CSS, unsafe_allow_html=True)


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