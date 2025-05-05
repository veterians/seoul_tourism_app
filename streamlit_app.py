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

# 개별 모듈 직접 import (folders 대신 individual files)
import utils
import pages_login
import pages_menu
import pages_map
import pages_course
import pages_history

# CSS 스타일 적용
utils.apply_custom_css()

# 세션 상태 초기화
utils.init_session_state()

# 페이지 라우팅
def main():
    # 로그인 상태에 따른 페이지 제어
    if not st.session_state.logged_in and st.session_state.current_page != "login":
        st.session_state.current_page = "login"
    
    # 현재 페이지에 따라 해당 모듈의 함수 호출
    if st.session_state.current_page == "login":
        pages_login.show()
    elif st.session_state.current_page == "menu":
        pages_menu.show()
    elif st.session_state.current_page == "map":
        pages_map.show()
    elif st.session_state.current_page == "course":
        pages_course.show()
    elif st.session_state.current_page == "history":
        pages_history.show()
    else:
        pages_menu.show()  # 기본값

if __name__ == "__main__":
    main()
