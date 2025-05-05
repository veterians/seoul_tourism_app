import streamlit as st
import time
from geopy.distance import geodesic

from utils.auth import change_page
from utils.ui import page_header
from utils.data_processing import get_location_position, add_visit
from utils.data_loader import load_excel_files
from utils.google_maps import show_google_map

def show():
    """지도 페이지 표시"""
    page_header("서울 관광 장소 지도")
    
    # 뒤로가기 버튼
    if st.button("← 메뉴로 돌아가기"):
        change_page("menu")
        st.rerun()
    
    # API 키 확인
    api_key = st.session_state.google_maps_api_key
    if not api_key:
        st.error("Google Maps API 키가 설정되지 않았습니다.")
        api_key = st.text_input("Google Maps API 키를 입력하세요", type="password")
        if api_key:
            st.session_state.google_maps_api_key = api_key
            st.success("API 키가 설정되었습니다. 지도를 로드합니다.")
            st.rerun()
        else:
            st.info("Google Maps를 사용하려면 API 키가 필요합니다.")
            return
    
    # 언어 선택
    col1, col2 = st.columns([4, 1])
    with col2:
        selected_language = st.selectbox(
            "🌏 Language", 
            ["🇰🇷 한국어", "🇺🇸 English", "🇨🇳 中文"],
            index=0 if st.session_state.language == "한국어" else 1 if st.session_state.language == "영어" else 2
        )
        language_map = {
            "🇰🇷 한국어": "한국어",
            "🇺🇸 English": "영어",
            "🇨🇳 中文": "중국어"
        }
        st.session_state.language = language_map[selected_language]
    
    # 사용자 위치 가져오기
    user_location = get_location_position()
    
    # 데이터 로드 컨트롤
    with st.sidebar:
        st.header("데이터 관리")
        
        # 데이터 로드 버튼
        if st.button("서울 관광 데이터 로드", use_container_width=True):
            with st.spinner("데이터를 로드하는 중..."):
                all_markers = load_excel_files(st.session_state.language)
                if all_markers:
                    st.session_state.all_markers = all_markers
                    st.session_state.markers_loaded = True
                    st.success(f"총 {len(all_markers)}개의 관광지 로드 완료!")
                else:
                    st.warning("데이터를 로드할 수 없습니다.")
        
        # 파일 업로드
        uploaded_files = st.file_uploader(
            "Excel 파일 업로드 (.xlsx)",
            type=["xlsx"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button("업로드한 파일 처리", use_container_width=True):
                with st.spinner("파일을 처리하는 중..."):
                    # 파일 처리 로직 (실제 구현 필요)
                    st.success("파일 업로드 완료!")
    
    # 내비게이션 모드가 아닌 경우 기본 지도 표시
    if not st.session_state.navigation_active:
        map_col, info_col = st.columns([2, 1])
        
        with map_col:
            # 마커 데이터 준비
            markers = []
            
            # 사용자 현재 위치 마커
            markers.append({
                'lat': user_location[0],
                'lng': user_location[1],
                'title': '내 위치',
                'color': 'blue',
                'info': '현재 위치',
                'category': '현재 위치'
            })
            
            # 로드된 데이터 마커 추가
            if hasattr(st.session_state, 'all_markers') and st.session_state.all_markers:
                markers.extend(st.session_state.all_markers)
                st.success(f"지도에 {len(st.session_state.all_markers)}개의 장소를 표시했습니다.")
            
            # Google Maps 표시
            show_google_map(
                api_key=api_key,
                center_lat=user_location[0],
                center_lng=user_location[1],
                markers=markers,
                zoom=12,
                height=600,
                language=st.session_state.language
            )
        
        with info_col:
            st.subheader("장소 정보")
            
            # 검색 기능
            search_term = st.text_input("장소 검색")
            if search_term and hasattr(st.session_state, 'all_markers') and st.session_state.all_markers:
                search_results = [m for m in st.session_state.all_markers 
                                 if search_term.lower() in m['title'].lower()]
                
                if search_results:
                    st.markdown(f"### 🔍 검색 결과 ({len(search_results)}개)")
                    for i, marker in enumerate(search_results[:5]):  # 상위 5개만
                        with st.container():
                            st.markdown(f"**{marker['title']}**")
                            st.caption(f"분류: {marker.get('category', '기타')}")
                            
                            col1, col2 = st.columns([1,1])
                            with col1:
                                if st.button(f"길찾기", key=f"nav_{i}"):
                                    st.session_state.navigation_active = True
                                    st.session_state.navigation_destination = {
                                        "name": marker['title'],
                                        "lat": marker['lat'],
                                        "lng": marker['lng']
                                    }
                                    st.rerun()
                            
                            with col2:
                                if st.button(f"방문기록", key=f"visit_{i}"):
                                    success, xp = add_visit(
                                        st.session_state.username,
                                        marker['title'],
                                        marker['lat'],
                                        marker['lng']
                                    )
                                    if success:
                                        st.success(f"'{marker['title']}' 방문! +{xp} XP 획득!")
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.info("이미 오늘 방문한 장소입니다.")
                else:
                    st.info(f"'{search_term}'에 대한 검색 결과가 없습니다.")
            
            # 카테고리별 통계
            if hasattr(st.session_state, 'all_markers') and st.session_state.all_markers:
                st.subheader("카테고리별 장소")
                categories = {}
                for m in st.session_state.all_markers:
                    cat = m.get('category', '기타')
                    if cat not in categories:
                        categories[cat] = 0
                    categories[cat] += 1
                
                for cat, count in categories.items():
                    st.markdown(f"- **{cat}**: {count}개")
    else:
        # 내비게이션 모드 UI
        destination = st.session_state.navigation_destination
        if not destination:
            st.error("목적지 정보가 없습니다.")
            if st.button("지도로 돌아가기"):
                st.session_state.navigation_active = False
                st.rerun()
        else:
            st.subheader(f"🧭 {destination['name']}까지 내비게이션")
            
            # 목적지 정보 표시
            dest_lat, dest_lng = destination["lat"], destination["lng"]
            user_lat, user_lng = user_location
            
            # 직선 거리 계산
            distance = geodesic((user_lat, user_lng), (dest_lat, dest_lng)).meters
            
            if not st.session_state.transport_mode:
                st.markdown("### 이동 수단 선택")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    walk_time = distance / 67  # 도보 속도 약 4km/h (67m/분)
                    st.markdown("""
                    <div class="card">
                        <h3>🚶 도보</h3>
                        <p>예상 소요 시간: {:.0f}분</p>
                    </div>
                    """.format(walk_time), unsafe_allow_html=True)
                    
                    if st.button("도보 선택", use_container_width=True):
                        st.session_state.transport_mode = "walk"
                        st.rerun()
                
                with col2:
                    transit_time = distance / 200  # 대중교통 속도 약 12km/h (200m/분)
                    st.markdown("""
                    <div class="card">
                        <h3>🚍 대중교통</h3>
                        <p>예상 소요 시간: {:.0f}분</p>
                    </div>
                    """.format(transit_time), unsafe_allow_html=True)
                    
                    if st.button("대중교통 선택", use_container_width=True):
                        st.session_state.transport_mode = "transit"
                        st.rerun()
                
                with col3:
                    car_time = distance / 500  # 자동차 속도 약 30km/h (500m/분)
                    st.markdown("""
                    <div class="card">
                        <h3>🚗 자동차</h3>
                        <p>예상 소요 시간: {:.0f}분</p>
                    </div>
                    """.format(car_time), unsafe_allow_html=True)
                    
                    if st.button("자동차 선택", use_container_width=True):
                        st.session_state.transport_mode = "car"
                        st.rerun()
                
                if st.button("← 지도로 돌아가기", use_container_width=True):
                    st.session_state.navigation_active = False
                    st.rerun()
            
            else:
                # 선택된 교통수단에 따른 내비게이션 표시
                transport_mode = st.session_state.transport_mode
                transport_icons = {
                    "walk": "🚶",
                    "transit": "🚍",
                    "car": "🚗"
                }
                transport_names = {
                    "walk": "도보",
                    "transit": "대중교통",
                    "car": "자동차"
                }
                
                st.markdown(f"### {transport_icons[transport_mode]} {transport_names[transport_mode]} 경로")
                
                # 경로 데이터 준비 (두 지점 연결)
                route = [
                    {"lat": user_lat, "lng": user_lng},  # 출발지
                    {"lat": dest_lat, "lng": dest_lng}   # 목적지
                ]
                
                # 마커 데이터 준비
                markers = [
                    {
                        'lat': user_lat, 
                        'lng': user_lng, 
                        'title': '내 위치', 
                        'color': 'blue', 
                        'info': '출발 지점',
                        'category': '내 위치'
                    },
                    {
                        'lat': dest_lat, 
                        'lng': dest_lng, 
                        'title': destination["name"], 
                        'color': 'red', 
                        'info': f'목적지: {destination["name"]}',
                        'category': '목적지'
                    }
                ]
                
                # 내비게이션 UI
                nav_col, info_col = st.columns([2, 1])
                
                with nav_col:
                    # 지도에 출발지-목적지 경로 표시
                    show_google_map(
                        api_key=api_key,
                        center_lat=(user_lat + dest_lat) / 2,  # 중간 지점
                        center_lng=(user_lng + dest_lng) / 2,
                        markers=markers,
                        zoom=14,
                        height=600,
                        language=st.session_state.language
                    )
                
                with info_col:
                    # 경로 정보 표시
                    st.markdown("### 경로 정보")
                    st.markdown(f"**{destination['name']}까지**")
                    st.markdown(f"- 거리: {distance:.0f}m")
                    
                    # 교통수단별 예상 시간
                    if transport_mode == "walk":
                        speed = 67  # m/min
                        transport_desc = "도보"
                    elif transport_mode == "transit":
                        speed = 200  # m/min
                        transport_desc = "대중교통"
                    else:  # car
                        speed = 500  # m/min
                        transport_desc = "자동차"
                    
                    time_min = distance / speed
                    st.markdown(f"- 예상 소요 시간: {time_min:.0f}분")
                    st.markdown(f"- 이동 수단: {transport_desc}")
                    
                    # 턴바이턴 내비게이션 지시사항 (예시)
                    st.markdown("### 경로 안내")
                    directions = [
                        "현재 위치에서 출발합니다",
                        f"{distance*0.3:.0f}m 직진 후 오른쪽으로 턴",
                        f"{distance*0.2:.0f}m 직진 후 왼쪽으로 턴",
                        f"{distance*0.5:.0f}m 직진 후 목적지 도착"
                    ]
                    
                    for i, direction in enumerate(directions):
                        st.markdown(f"{i+1}. {direction}")
                    
                    # 다른 교통수단 선택 버튼
                    st.markdown("### 다른 이동 수단")
                    other_modes = {"walk": "도보", "transit": "대중교통", "car": "자동차"}
                    other_modes.pop(transport_mode)  # 현재 모드 제거
                    
                    cols = st.columns(len(other_modes))
                    for i, (mode, name) in enumerate(other_modes.items()):
                        with cols[i]:
                            if st.button(name):
                                st.session_state.transport_mode = mode
                                st.rerun()
                    
                    if st.button("내비게이션 종료", use_container_width=True):
