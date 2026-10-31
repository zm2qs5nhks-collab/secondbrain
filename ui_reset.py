"""
登录卡里的「找回密码」流程。

两步：
1) 输入邮箱 → 发送验证码
2) 输入验证码 + 新密码 → 重置

所有安全判断都在 storage.password_reset 里，这里只管交互。
"""

import streamlit as st

from storage.password_reset import request_code, reset_password


def render_reset_forms() -> None:
    st.markdown(
        '<div class="tc-eyebrow">Reset Password</div>'
        '<div class="tc-title">找回密码</div>'
        '<div class="tc-sub">验证码会发到你注册时用的邮箱，10 分钟内有效</div>',
        unsafe_allow_html=True,
    )

    step = st.session_state.get("reset_step", 0)

    if step == 0:
        with st.form("reset_request_form", clear_on_submit=False):
            email = st.text_input(
                "邮箱", key="reset_email", placeholder="注册时用的邮箱",
                label_visibility="collapsed",
            )
            sent = st.form_submit_button(
                "发送验证码", type="primary", use_container_width=True
            )
        if sent:
            res = request_code(email)
            if res["ok"]:
                st.session_state["reset_email_value"] = email.strip().lower()
                st.session_state["reset_step"] = 1
                st.rerun()
            else:
                st.error(res["message"])

    else:
        target = st.session_state.get("reset_email_value", "")
        if target:
            st.caption(f"验证码已发送到 `{target}`")

        with st.form("reset_confirm_form", clear_on_submit=False):
            code = st.text_input(
                "验证码", key="reset_code", placeholder="6 位验证码",
                max_chars=6, label_visibility="collapsed",
            )
            pwd1 = st.text_input(
                "新密码", type="password", key="reset_pwd1",
                placeholder="新密码（至少 6 位）", label_visibility="collapsed",
            )
            pwd2 = st.text_input(
                "确认新密码", type="password", key="reset_pwd2",
                placeholder="再次输入新密码", label_visibility="collapsed",
            )
            done = st.form_submit_button(
                "重置密码", type="primary", use_container_width=True
            )

        if done:
            if pwd1 != pwd2:
                st.error("两次输入的密码不一致")
            else:
                res = reset_password(target, code, pwd1)
                if res["ok"]:
                    st.session_state.auth_mode = "login"
                    st.session_state["reset_step"] = 0
                    st.session_state["_login_notice"] = res["message"]
                    st.rerun()
                else:
                    st.error(res["message"])

        if st.button("返回登录", key="reset_back", use_container_width=True):
            st.session_state["reset_step"] = 0
            st.session_state.auth_mode = "login"
            st.rerun()
