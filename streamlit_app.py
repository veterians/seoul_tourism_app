import streamlit as st
from pages import login, menu, map, course, history, settings
import config
from utils.ui import apply_custom_css

# 페이지 설정
st.set_page_config(
    page_title="서울 관광앱",
    page_icon="🗼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS 스타일 적용
apply_custom_css()

# 초기 세션 상태 설정
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "current_page" not in st.session_state:
    st.session_state.current_page = "login"

# 페이지 전환 함수
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
    elif st.session_state.current_page == "settings":
        settings.show()

if __name__ == "__main__":
    main()
