import streamlit as st
from utils.auth import authenticate_user, register_user, change_page
from utils.ui import page_header

def show():
    """로그인 페이지 표시"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        page_header("서울 관광앱")
        st.image("https://i.imgur.com/0aMYJHa.png", width=300)
        
        tab1, tab2 = st.tabs(["로그인", "회원가입"])

        with tab1:
            st.markdown("### 로그인")
            username = st.text_input("아이디", key="login_username")
            password = st.text_input("비밀번호", type="password", key="login_password")
            col1, col2 = st.columns([1,1])
            with col1:
                remember = st.checkbox("아이디 저장")
            with col2:
                st.markdown("")  # 빈 공간
            
            if st.button("로그인", use_container_width=True):
                if authenticate_user(username, password):
                    st.success("🎉 로그인 성공!")
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    change_page("menu")
                    st.rerun()
                else:
                    st.error("❌ 아이디 또는 비밀번호가 올바르지 않습니다.")

        with tab2:
            st.markdown("### 회원가입")
            new_user = st.text_input("새 아이디", key="register_username")
            new_pw = st.text_input("새 비밀번호", type="password", key="register_password")
            new_pw_confirm = st.text_input("비밀번호 확인", type="password", key="register_password_confirm")
            
            if st.button("회원가입", use_container_width=True):
                if not new_user or not new_pw:
                    st.error("아이디와 비밀번호를 입력해주세요.")
                elif new_pw != new_pw_confirm:
                    st.error("비밀번호와 비밀번호 확인이 일치하지 않습니다.")
                elif register_user(new_user, new_pw):
                    st.success("✅ 회원가입 완료!")
                    st.session_state.logged_in = True
                    st.session_state.username = new_user
                    change_page("menu")
                    st.rerun()
                else:
                    st.warning("⚠️ 이미 존재하는 아이디입니다.")
