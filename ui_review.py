"""
学习路径 —— 从 app.py 迁出，作为「复习提醒」页的第三个 tab。

为什么搬：复习提醒和学习路径都在算记忆保留率、都在推荐下一步复习，
做成两个平级菜单属于重复入口。合并后导航少一项，功能一个不少。
"""

import html
import time

import streamlit as st

from scheduler import forgetting_curve as fc
from storage import metadata_store, vector_store
from storage.learning_path import get_learning_path, get_weak_notes
from ui_theme import notebook_line, page_header


def render_learning_path(user_id: str) -> None:
    page_header("🎯", "个性化学习路径", "根据遗忘曲线和标签掌握度，推荐下一步学习方向")
    notebook_line()

    _done = st.session_state.get("_review_done")
    if _done:
        st.success(_done)
        st.session_state["_review_done"] = None

    from storage.learning_path import get_learning_path, get_weak_notes

    path_data = get_learning_path(user_id=user_id)

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
                                    n["id"], user_id=user_id
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
                                    fc.record_access(n["id"], user_id=user_id)
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
    weak_notes = get_weak_notes(5, user_id=user_id)
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
