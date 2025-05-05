import streamlit as st
from utils.auth import change_page
from utils.ui import page_header

def show():
    """설정 페이지 표시"""
    page_header("앱 설정")
    
    # 뒤로가기 버튼
    if st.button("← 메뉴로 돌아가기"):
        change_page("menu")
        st.rerun()
    
    st.subheader("일반 설정")
    
    # 언어 설정
    st.markdown("### 언어 설정")
    selected_language = st.selectbox(
        "기본 언어 선택", 
        ["🇰🇷 한국어", "🇺🇸 English", "🇨🇳 中文"],
        index=0 if st.session_state.language == "한국어" else 1 if st.session_state.language == "영어" else 2
    )
    language_map = {
        "🇰🇷 한국어": "한국어",
        "🇺🇸 English": "영어",
        "🇨🇳 中文": "중국어"
    }
    st.session_state.language = language_map[selected_language]
    
    # API 키 설정
    st.markdown("### API 키 설정")
    st.markdown("Google Maps API 키를 입력해주세요. API 키가 없으면 지도 기능을 사용할 수 없습니다.")
    
    current_api_key = st.session_state.google_maps_api_key if "google_maps_api_key" in st.session_state else ""
    api_key = st.text_input("Google Maps API 키", value=current_api_key, type="password")
    
    if api_key and api_key != current_api_key:
        st.session_state.google_maps_api_key = api_key
        st.success("API 키가 저장되었습니다.")
    
    # 알림 설정
    st.markdown("### 알림 설정")
    
    if "notifications_enabled" not in st.session_state:
        st.session_state.notifications_enabled = True
    
    notifications_enabled = st.toggle("알림 활성화", value=st.session_state.notifications_enabled)
    st.session_state.notifications_enabled = notifications_enabled
    
    # 앱 정보
    st.markdown("---")
    st.markdown("### 앱 정보")
    st.markdown("**서울 관광앱** v1.0.0")
    st.markdown("개발자: 서울관광프론티어팀")
    st.markdown("문의: frontier@example.com")
    
    # 캐시 초기화 버튼
    st.markdown("---")
    if st.button("캐시 초기화", use_container_width=True):
        st.cache_data.clear()
        st.success("캐시가 초기화되었습니다.")
