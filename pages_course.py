import streamlit as st
import random
import time
import utils

def show():
    """관광 코스 추천 페이지 표시"""
    utils.page_header("서울 관광 코스 짜주기")
    
    # 뒤로가기 버튼
    if st.button("← 메뉴로 돌아가기"):
        utils.change_page("menu")
        st.rerun()
    
    # AI 추천 아이콘 및 소개
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("https://i.imgur.com/8JfVh5H.png", width=80)
    with col2:
        st.markdown("### AI가 추천하는 맞춤 코스")
        st.markdown("여행 일정과 취향을 입력하시면 최적의 관광 코스를 추천해 드립니다.")
    
    # 여행 정보 입력 섹션
    st.markdown("---")
    st.subheader("여행 정보 입력")
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("여행 시작일")
    
    with col2:
        end_date = st.date_input("여행 종료일", value=start_date)
    
    # 일수 계산
    delta = (end_date - start_date).days + 1
    st.caption(f"총 {delta}일 일정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_people = st.number_input("여행 인원", min_value=1, max_value=10, value=2)
    
    with col2:
        include_children = st.checkbox("아이 동반")
    
    # 여행 스타일 선택
    st.markdown("### 여행 스타일")
    travel_styles = ["활동적인", "휴양", "맛집", "쇼핑", "역사/문화", "자연"]
    
    # 3열로 버튼식 선택
    cols = st.columns(3)
    selected_styles = []
    
    for i, style in enumerate(travel_styles):
        with cols[i % 3]:
            if st.checkbox(style, key=f"style_{style}"):
                selected_styles.append(style)
    
    # 코스 생성 버튼
    st.markdown("---")
    generate_course = st.button("코스 생성하기", type="primary", use_container_width=True)
    
    if generate_course:
        if not selected_styles:
            st.warning("최소 하나 이상의 여행 스타일을 선택해주세요.")
        else:
            with st.spinner("최적의 관광 코스를 생성 중입니다..."):
                # 로딩 효과를 위한 딜레이
                time.sleep(2)
                
                # 스타일에 따른 코스 추천
                if "역사/문화" in selected_styles:
                    course_type = "문화 코스"
                elif "쇼핑" in selected_styles or "맛집" in selected_styles:
                    course_type = "쇼핑 코스"
                elif "휴양" in selected_styles or "자연" in selected_styles:
                    course_type = "자연 코스"
                else:
                    course_type = "대중적 코스"
                
                # 현재 데이터 확인
                if not hasattr(st.session_state, 'all_markers') or not st.session_state.all_markers:
                    with st.spinner("관광지 데이터를 로드하는 중..."):
                        all_markers = utils.load_excel_files(st.session_state.language)
                        if all_markers:
                            st.session_state.all_markers = all_markers
                        else:
                            # 데이터가 없을 경우 기본 코스 사용
                            all_markers = []
                else:
                    all_markers = st.session_state.all_markers
                
                # 기본 코스에서 추천
                recommended_course = utils.RECOMMENDATION_COURSES.get(course_type, [])
                
                # 충분한 데이터가 있으면 실제 마커 데이터 사용
                if all_markers and len(all_markers) > 10:
                    # 카테고리별 장소 필터링
                    filtered_markers = []
                    if "역사/문화" in selected_styles:
                        filtered_markers.extend([m for m in all_markers if "역사" in m.get('category', '').lower() or "문화" in m.get('category', '').lower() or "미술관" in m.get('category', '').lower()])
                    if "쇼핑" in selected_styles:
                        filtered_markers.extend([m for m in all_markers if "쇼핑" in m.get('category', '').lower() or "기념품" in m.get('category', '').lower()])
                    if "맛집" in selected_styles:
                        filtered_markers.extend([m for m in all_markers if "음식" in m.get('category', '').lower() or "맛집" in m.get('category', '').lower()])
                    if "자연" in selected_styles:
                        filtered_markers.extend([m for m in all_markers if "자연" in m.get('category', '').lower() or "공원" in m.get('category', '').lower()])
                    
                    # 중복 제거
                    seen = set()
                    filtered_markers = [m for m in filtered_markers if not (m['title'] in seen or seen.add(m['title']))]
                    
                    # 장소가 충분하면 사용, 그렇지 않으면 기본 코스에 추가
                    if filtered_markers and len(filtered_markers) >= delta * 3:
                        random.shuffle(filtered_markers)
                        recommended_course = []
                        for i in range(min(delta * 3, len(filtered_markers))):
                            recommended_course.append(filtered_markers[i]['title'])
                    elif filtered_markers:
                        # 기본 코스에 필터링된 장소 추가
                        for m in filtered_markers[:5]:
                            if m['title'] not in recommended_course:
                                recommended_course.append(m['title'])
                
                st.success("코스 생성 완료!")
                
                # 코스 표시
                st.markdown("## 추천 코스")
                st.markdown(f"**{course_type}** - {delta}일 일정")
                
                # 코스 마커 및 정보 준비
                course_markers = []
                
                # 일별 코스 표시
                for day in range(1, min(delta+1, 4)):  # 최대 3일까지
                    st.markdown(f"### Day {day}")
                    
                    # 일별 방문 장소 선택
                    day_spots = []
                    if day == 1:
                        day_spots = recommended_course[:3]  # 첫날 3곳
                    elif day == 2:
                        day_spots = recommended_course[3:6] if len(recommended_course) > 3 else recommended_course[:3]
                    else:  # 3일차 이상
                        day_spots = recommended_course[6:9] if len(recommended_course) > 6 else recommended_course[:3]
                    
                    # 표시할 장소가 없으면 기본 추천
                    if not day_spots:
                        day_spots = ["경복궁", "남산서울타워", "명동"]
                    
                    timeline = st.columns(len(day_spots))
                    
                    for i, spot_name in enumerate(day_spots):
                        # 장소 정보 찾기 (마커 데이터에서 또는 기본값 사용)
                        spot_info = None
                        if all_markers:
                            spot_info = next((m for m in all_markers if m['title'] == spot_name), None)
                        
                        # 방문 시간대 설정
                        time_slots = ["09:00-12:00", "13:00-16:00", "16:00-19:00"]
                        time_slot = time_slots[i % 3]
                        
                        with timeline[i]:
                            st.markdown(f"**{time_slot}**")
                            st.markdown(f"**{spot_name}**")
                            
                            if spot_info:
                                st.caption(f"분류: {spot_info.get('category', '관광지')}")
                                
                                # 경로에 추가
                                course_markers.append(spot_info)
                            else:
                                st.caption("관광지")
                
                # 지도에 코스 표시
                st.markdown("### 🗺️ 코스 지도")
                
                # 필요한 경우 API 키 확인
                api_key = st.session_state.google_maps_api_key
                if not api_key:
                    st.error("Google Maps API 키가 설정되지 않았습니다.")
                    api_key = st.text_input("Google Maps API 키를 입력하세요", type="password")
                    if api_key:
                        st.session_state.google_maps_api_key = api_key
                
                # 코스 마커 표시
                if course_markers:
                    # 지도 중심 좌표 계산 (마커들의 평균)
                    center_lat = sum(m['lat'] for m in course_markers) / len(course_markers)
                    center_lng = sum(m['lng'] for m in course_markers) / len(course_markers)
                    
                    # 지도 표시
                    utils.show_google_map(
                        api_key=api_key,
                        center_lat=center_lat,
                        center_lng=center_lng,
                        markers=course_markers,
                        zoom=12,
                        height=500,
                        language=st.session_state.language
                    )
                else:
                    # 실제 좌표 데이터가 없는 경우
                    st.warning("코스 장소의 좌표 정보가 없어 지도에 표시할 수 없습니다.")
                
                # 일정 저장 버튼
                if st.button("이 코스 저장하기", use_container_width=True):
                    if 'saved_courses' not in st.session_state:
                        st.session_state.saved_courses = []
                    
                    st.session_state.saved_courses.append({
                        "type": course_type,
                        "days": delta,
                        "places": recommended_course,
                        "date": start_date.strftime("%Y-%m-%d")
                    })
                    
                    st.success("코스가 저장되었습니다!")
