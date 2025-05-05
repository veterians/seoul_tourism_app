import streamlit as st
from utils.data_loader import save_session_data

def change_page(page):
    """페이지 전환 함수"""
    st.session_state.current_page = page
    
    # 페이지 전환 시 일부 상태 초기화
    if page != "map":
        st.session_state.clicked_location = None
        st.session_state.navigation_active = False
        st.session_state.navigation_destination = None
        st.session_state.transport_mode = None

def authenticate_user(username, password):
    """사용자 인증 함수"""
    if "users" not in st.session_state:
        return False
    
    return username in st.session_state.users and st.session_state.users[username] == password

def register_user(username, password):
    """사용자 등록 함수"""
    if "users" not in st.session_state:
        st.session_state.users = {"admin": "admin"}
    
    if username in st.session_state.users:
        return False
    
    st.session_state.users[username] = password
    
    # 신규 사용자 데이터 초기화
    if "user_xp" not in st.session_state:
        st.session_state.user_xp = {}
    st.session_state.user_xp[username] = 0
    
    if "user_visits" not in st.session_state:
        st.session_state.user_visits = {}
    st.session_state.user_visits[username] = []
    
    save_session_data()
    return True

def logout_user():
    """로그아웃 함수"""
    st.session_state.logged_in = False
    st.session_state.username = ""
    change_page("login")
