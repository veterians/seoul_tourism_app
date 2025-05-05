import streamlit as st
import os
from pathlib import Path

# 데이터 폴더 생성
data_folder = Path("data")
if not data_folder.exists():
    data_folder.mkdir(parents=True, exist_ok=True)

# 페이지 설정
st.set_page_config(
    page_title="서울 관광앱",
    page_icon="🗼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 필요한 유틸리티 및 페이지 모듈 임포트
from utils.ui import apply_custom_css
from utils.data_loader import init_session_state
from pages import login, menu, map, course, history

# CSS 스타일 적용
apply_custom_css()

# 세션 상태 초기화
init_session_state()

# 페이지 라우팅
def main():
    # 로그인 상태에 따른 페이지 제어
    if not st.session_state.logged_in and st.session_state.current_page != "login":
        st.session_state.current_page = "login"
    
    # 현재 페이지에 따라 해당 모듈의 함수 호출
    if st.session_state.current_page == "login":
        login.show()
    elif st.session_state.current_page == "menu":
        menu.show()
    elif st.session_state.current_page == "map":
        map.show()
    elif st.session_state.current_page == "course":
        course.show()
    elif st.session_state.current_page == "history":
        history.show()
    else:
        menu.show()  # 기본값

if __name__ == "__main__":
    main()
