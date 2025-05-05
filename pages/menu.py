import streamlit as st
from utils.auth import change_page, logout_user
from utils.ui import page_header, display_user_level_info

def show():
    """메인 메뉴 페이지 표시"""
    page_header("서울 관광앱")
    st.markdown(f"### 👋 {st.session_state.username}님, 환영합니다!")
    
    # 사용자 레벨 및 경험치 정보 표시
    display_user_level_info()
    
    st.markdown("---")
    st.markdown("### 메뉴를 선택해주세요")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3>🗺️ 관광 장소 지도</h3>
            <p>서울의 주요 관광지를 지도에서 찾고 내비게이션으로 이동해보세요.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("관광 장소 지도 보기", key="map_button", use_container_width=True):
            change_page("map")
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>🗓️ 서울 관광 코스 짜주기</h3>
            <p>AI가 당신의 취향에 맞는 최적의 관광 코스를 추천해드립니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("관광 코스 짜기", key="course_button", use_container_width=True):
            change_page("course")
            st.rerun()
    
    st.markdown("")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3>📝 나의 관광 이력</h3>
            <p>방문한 장소들의 기록과 획득한 경험치를 확인하세요.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("관광 이력 보기", key="history_button", use_container_width=True):
            change_page("history")
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>⚙️ 설정</h3>
            <p>앱 설정 및 환경설정을 변경합니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("설정", key="settings_button", use_container_width=True):
            change_page("settings")
            st.rerun()
            
    # 로그아웃 버튼
    st.markdown("---")
    if st.button("🔓 로그아웃", key="logout_button"):
        logout_user()
        st.rerun()
