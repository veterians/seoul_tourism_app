import streamlit as st
import pandas as pd
from datetime import datetime
import utils

def display_visits(visits):
    """방문 기록 표시 함수"""
    if not visits:
        st.info("방문 기록이 없습니다.")
        return
    
    for i, visit in enumerate(visits):
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{visit['place_name']}**")
                st.caption(f"방문일: {visit['date']}")
            
            with col2:
                st.markdown(f"+{visit.get('xp_gained', 0)} XP")
            
            with col3:
                # 리뷰 또는 평점이 있는 경우 표시
                if 'rating' in visit and visit['rating']:
                    st.markdown("⭐" * int(visit['rating']))
                else:
                    if st.button("평가", key=f"rate_{i}"):
                        # 평가 기능 구현 (실제로는 팝업이나 별도 UI가 필요)
                        st.session_state.rating_place = visit['place_name']
                        st.session_state.rating_index = i

def show():
    """관광 이력 페이지 표시"""
    utils.page_header("나의 관광 이력")
    
    # 뒤로가기 버튼
    if st.button("← 메뉴로 돌아가기"):
        utils.change_page("menu")
        st.rerun()
    
    username = st.session_state.username
    
    # 사용자 레벨과 경험치 표시
    user_xp = st.session_state.user_xp.get(username, 0)
    user_level = utils.calculate_level(user_xp)
    xp_percentage = utils.calculate_xp_percentage(user_xp)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        st.image("https://i.imgur.com/W3UVTgZ.png", width=100)  # 사용자 아이콘
    
    with col2:
        st.markdown(f"## 레벨 {user_level}")
        st.progress(xp_percentage / 100)
        st.markdown(f"**총 경험치: {user_xp} XP** (다음 레벨까지 {utils.XP_PER_LEVEL - (user_xp % utils.XP_PER_LEVEL)} XP)")
    
    with col3:
        st.write("")  # 빈 공간
    
    # 방문 통계
    if username in st.session_state.user_visits and st.session_state.user_visits[username]:
        visits = st.session_state.user_visits[username]
        
        total_visits = len(visits)
        unique_places = len(set([v['place_name'] for v in visits]))
        total_xp = sum([v.get('xp_gained', 0) for v in visits])
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("총 방문 횟수", f"{total_visits}회")
        
        with col2:
            st.metric("방문한 장소 수", f"{unique_places}곳")
        
        with col3:
            st.metric("획득한 경험치", f"{total_xp} XP")
        
        # 방문 기록 목록 표시
        st.markdown("---")
        st.subheader("📝 방문 기록")
        
        # 정렬 옵션
        tab1, tab2, tab3 = st.tabs(["전체", "최근순", "경험치순"])
        
        with tab1:
            display_visits(visits)
        
        with tab2:
            recent_visits = sorted(visits, key=lambda x: x['timestamp'], reverse=True)
            display_visits(recent_visits)
        
        with tab3:
            xp_visits = sorted(visits, key=lambda x: x.get('xp_gained', 0), reverse=True)
            display_visits(xp_visits)
        
        # 방문한 장소를 지도에 표시
        st.markdown("---")
        st.subheader("🗺️ 방문 지도")
        
        # 필요한 경우 API 키 확인
        api_key = st.session_state.google_maps_api_key
        if not api_key:
            st.error("Google Maps API 키가 설정되지 않았습니다.")
            api_key = st.text_input("Google Maps API 키를 입력하세요", type="password")
            if api_key:
                st.session_state.google_maps_api_key = api_key
        
        # 방문 장소 마커 생성
        visit_markers = []
        for visit in visits:
            marker = {
                'lat': visit["latitude"],
                'lng': visit["longitude"],
                'title': visit["place_name"],
                'color': 'purple',  # 방문한 장소는 보라색으로 표시
                'info': f"방문일: {visit['date']}<br>획득 XP: +{visit.get('xp_gained', 0)}",
                'category': '방문한 장소'
            }
            visit_markers.append(marker)
        
        if visit_markers:
            # 지도 중심 좌표 계산 (마커들의 평균)
            center_lat = sum(m['lat'] for m in visit_markers) / len(visit_markers)
            center_lng = sum(m['lng'] for m in visit_markers) / len(visit_markers)
            
            # Google Maps 표시
            utils.show_google_map(
                api_key=api_key,
                center_lat=center_lat,
                center_lng=center_lng,
                markers=visit_markers,
                zoom=12,
                height=500,
                language=st.session_state.language
            )
        else:
            st.info("지도에 표시할 방문 기록이 없습니다.")
    else:
        st.info("아직 방문 기록이 없습니다. 지도에서 장소를 방문하면 여기에 기록됩니다.")
        
        # 예시 데이터 생성 버튼
        if st.button("예시 데이터 생성"):
            # 샘플 방문 데이터
            sample_visits = [
                {
                    "place_name": "경복궁",
                    "latitude": 37.5796,
                    "longitude": 126.9770,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "xp_gained": 80
                },
                {
                    "place_name": "남산서울타워",
                    "latitude": 37.5511,
                    "longitude": 126.9882,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "xp_gained": 65
                },
                {
                    "place_name": "명동",
                    "latitude": 37.5635,
                    "longitude": 126.9877,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "xp_gained": 25
                }
            ]
            
            if username not in st.session_state.user_visits:
                st.session_state.user_visits[username] = []
            
            st.session_state.user_visits[username] = sample_visits
            
            # XP 부여
            total_xp = sum([v['xp_gained'] for v in sample_visits])
            if username not in st.session_state.user_xp:
                st.session_state.user_xp[username] = 0
            st.session_state.user_xp[username] += total_xp
            
            st.success(f"예시 데이터가 생성되었습니다! +{total_xp} XP 획득!")
            st.rerun()
