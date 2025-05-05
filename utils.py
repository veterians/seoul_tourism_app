# 모든 유틸리티 함수를 하나의 파일로 통합
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path
from geopy.distance import geodesic

# Google Maps 기본 중심 위치 (서울시청)
DEFAULT_LOCATION = [37.5665, 126.9780]

# 카테고리별 마커 색상
CATEGORY_COLORS = {
    "체육시설": "blue",
    "공연행사": "purple",
    "관광기념품": "green",
    "한국음식점": "orange",
    "미술관/전시": "pink",
    "종로구 관광지": "red",
    "기타": "gray"
}

# 파일명과 카테고리 매핑
FILE_CATEGORIES = {
    "체육시설": ["체육시설", "공연행사"],
    "관광기념품": ["관광기념품", "외국인전용"],
    "한국음식점": ["음식점", "한국음식"],
    "미술관/전시": ["미술관", "전시"],
    "종로구 관광지": ["종로구", "관광데이터"]
}

# 세션 데이터 저장 파일
SESSION_DATA_FILE = "data/session_data.json"

# 경험치 설정
XP_PER_LEVEL = 200
PLACE_XP = {
    "경복궁": 80,
    "남산서울타워": 65,
    "동대문 DDP": 35,
    "명동": 25,
    "인사동": 40,
    "창덕궁": 70,
    "북촌한옥마을": 50,
    "광장시장": 30,
    "서울숲": 20,
    "63빌딩": 45
}

# 언어 코드 매핑
LANGUAGE_CODES = {
    "한국어": "ko",
    "영어": "en", 
    "중국어": "zh-CN"
}

# 추천 코스 데이터
RECOMMENDATION_COURSES = {
    "문화 코스": ["경복궁", "인사동", "창덕궁", "북촌한옥마을"],
    "쇼핑 코스": ["동대문 DDP", "명동", "광장시장", "남산서울타워"],
    "자연 코스": ["서울숲", "남산서울타워", "한강공원", "북한산"],
    "대중적 코스": ["경복궁", "명동", "남산서울타워", "63빌딩"]
}

# UI 관련 함수
def apply_custom_css():
    """앱 전체에 적용되는 커스텀 CSS"""
    st.markdown("""
    <style>
        .main-header {color:#1E88E5; font-size:30px; font-weight:bold; text-align:center;}
        .sub-header {color:#1976D2; font-size:24px; font-weight:bold; margin-top:20px;}
        .card {
            border-radius:10px; 
            padding:20px; 
            margin:10px 0px; 
            background-color:#f0f8ff; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }
        .blue-btn {
            background-color:#1976D2; 
            color:white; 
            padding:10px 20px; 
            border-radius:5px; 
            border:none;
            text-align:center;
            cursor:pointer;
            font-weight:bold;
        }
        .xp-text {
            color:#4CAF50; 
            font-weight:bold;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            border-radius: 4px 4px 0 0;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        div[data-testid="stHorizontalBlock"] > div:first-child {
            border: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

def page_header(title):
    """페이지 헤더 표시"""
    st.markdown(f'<div class="main-header">{title}</div>', unsafe_allow_html=True)

def display_user_level_info():
    """사용자 레벨 및 경험치 정보 표시"""
    username = st.session_state.username
    user_xp = st.session_state.user_xp.get(username, 0)
    user_level = calculate_level(user_xp)
    xp_percentage = calculate_xp_percentage(user_xp)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://i.imgur.com/W3UVTgZ.png", width=100)  # 사용자 아이콘
    with col2:
        st.markdown(f"**레벨 {user_level}** ({user_xp} XP)")
        st.progress(xp_percentage / 100)
        st.caption(f"다음 레벨까지 {XP_PER_LEVEL - (user_xp % XP_PER_LEVEL)} XP 남음")

# 인증 관련 함수
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

# 데이터 로딩 및 처리 함수
def init_session_state():
    """세션 상태 초기화"""
    # 로그인 관련 상태
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "login"
        
    # 사용자 데이터
    if "users" not in st.session_state:
        st.session_state.users = {"admin": "admin"}  # 기본 관리자 계정
    if "user_xp" not in st.session_state:
        st.session_state.user_xp = {}
    if "user_visits" not in st.session_state:
        st.session_state.user_visits = {}
        
    # 지도 관련 상태
    if 'language' not in st.session_state:
        st.session_state.language = "한국어"
    if 'clicked_location' not in st.session_state:
        st.session_state.clicked_location = None
    if 'navigation_active' not in st.session_state:
        st.session_state.navigation_active = False
    if 'navigation_destination' not in st.session_state:
        st.session_state.navigation_destination = None
    if 'transport_mode' not in st.session_state:
        st.session_state.transport_mode = None
        
    # Google Maps API 키
    if "google_maps_api_key" not in st.session_state:
        # secrets.toml에서 가져오기 시도
        try:
            st.session_state.google_maps_api_key = st.secrets["google_maps_api_key"]
        except:
            st.session_state.google_maps_api_key = ""
    
    # 저장된 세션 데이터 로드
    load_session_data()

def load_session_data():
    """저장된 세션 데이터 로드"""
    try:
        if os.path.exists(SESSION_DATA_FILE):
            with open(SESSION_DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 데이터 복원
                st.session_state.users = data.get("users", {"admin": "admin"})
                st.session_state.user_visits = data.get("user_visits", {})
                st.session_state.user_xp = data.get("user_xp", {})
                return True
    except Exception as e:
        print(f"세션 데이터 로드 오류: {e}")
    return False

def save_session_data():
    """세션 데이터 저장"""
    try:
        # 데이터 폴더 생성
        os.makedirs(os.path.dirname(SESSION_DATA_FILE), exist_ok=True)
        
        data = {
            "users": st.session_state.users,
            "user_visits": st.session_state.user_visits,
            "user_xp": st.session_state.user_xp
        }
        
        with open(SESSION_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"세션 데이터 저장 오류: {e}")
        return False

def load_excel_files(language="한국어"):
    """데이터 폴더에서 모든 Excel 파일 로드"""
    data_folder = Path("data")
    all_markers = []
    
    if not data_folder.exists():
        st.warning("데이터 폴더가 존재하지 않습니다.")
        return []
        
    # 모든 Excel 파일 찾기
    excel_files = list(data_folder.glob("*.xlsx"))
    
    if not excel_files:
        st.warning("데이터 폴더에 Excel 파일이 없습니다.")
        return []
    
    for file_path in excel_files:
        try:
            # 파일 카테고리 결정
            file_category = "기타"
            file_name = file_path.name.lower()
            
            for category, keywords in FILE_CATEGORIES.items():
                if any(keyword.lower() in file_name for keyword in keywords):
                    file_category = category
                    break
            
            # 파일 로드
            df = pd.read_excel(file_path, engine='openpyxl')
            
            # 데이터 전처리 및 마커 변환
            markers = process_dataframe(df, file_category, language)
            all_markers.extend(markers)
            
            st.success(f"{file_path.name}: {len(markers)}개 마커 로드")
        
        except Exception as e:
            st.error(f"{file_path.name} 처리 오류: {str(e)}")
    
    return all_markers

def process_dataframe(df, category, language="한국어"):
    """데이터프레임을 Google Maps 마커 형식으로 변환"""
    markers = []
    
    # 필수 열 확인: X좌표, Y좌표
    if 'X좌표' not in df.columns or 'Y좌표' not in df.columns:
        # 중국어 데이터의 경우 열 이름이 다를 수 있음
        if 'X坐标' in df.columns and 'Y坐标' in df.columns:
            df['X좌표'] = df['X坐标']
            df['Y좌표'] = df['Y坐标']
        else:
            st.warning(f"'{category}' 데이터에 좌표 열이 없습니다.")
            return []
    
    # 언어별 열 이름 결정
    name_col = '명칭(한국어)'
    if language == "영어" and '명칭(영어)' in df.columns:
        name_col = '명칭(영어)'
    elif language == "중국어" and '명칭(중국어)' in df.columns:
        name_col = '명칭(중국어)'
    
    # 중국어 종로구 데이터 특별 처리
    if category == "종로구 관광지" and language == "중국어":
        if '名称' in df.columns:
            name_col = '名称'
    
    # 주소 열 결정
    address_col = None
    address_candidates = ['주소(한국어)', '주소', '소재지', '도로명주소', '지번주소']
    if language == "영어":
        address_candidates = ['주소(영어)'] + address_candidates
    elif language == "중국어":
        address_candidates = ['주소(중국어)', '地址'] + address_candidates
    
    for col in address_candidates:
        if col in df.columns:
            address_col = col
            break
    
    # 유효한 좌표 데이터만 사용
    df = df.dropna(subset=['X좌표', 'Y좌표'])
    valid_coords = (df['X좌표'] >= 124) & (df['X좌표'] <= 132) & (df['Y좌표'] >= 33) & (df['Y좌표'] <= 43)
    df = df[valid_coords]
    
    # 마커 색상 결정
    color = CATEGORY_COLORS.get(category, "gray")
    
    # 각 행을 마커로 변환
    for _, row in df.iterrows():
        try:
            # 기본 정보
            name = row[name_col] if name_col in row and pd.notna(row[name_col]) else "이름 없음"
            lat = float(row['Y좌표'])
            lng = float(row['X좌표'])
            
            # 주소 정보
            address = ""
            if address_col and address_col in row and pd.notna(row[address_col]):
                address = row[address_col]
            
            # 추가 정보 (있는 경우)
            info = ""
            if address:
                info += f"주소: {address}<br>"
            
            # 전화번호 (있는 경우)
            for tel_col in ['전화번호', 'TELNO', '연락처']:
                if tel_col in row and pd.notna(row[tel_col]):
                    info += f"전화: {row[tel_col]}<br>"
                    break
            
            # 마커 생성
            marker = {
                'lat': lat,
                'lng': lng,
                'title': name,
                'color': color,
                'category': category,
                'info': info
            }
            markers.append(marker)
            
        except Exception as e:
            print(f"마커 생성 오류: {e}")
            continue
    
    return markers

# 경험치 및 레벨 관련 함수
def calculate_level(xp):
    """레벨 계산 함수"""
    return int(xp / XP_PER_LEVEL) + 1

def calculate_xp_percentage(xp):
    """경험치 비율 계산 (다음 레벨까지)"""
    current_level = calculate_level(xp)
    xp_for_current_level = (current_level - 1) * XP_PER_LEVEL
    xp_for_next_level = current_level * XP_PER_LEVEL
    
    xp_in_current_level = xp - xp_for_current_level
    xp_needed_for_next = xp_for_next_level - xp_for_current_level
    
    return int((xp_in_current_level / xp_needed_for_next) * 100)

def add_visit(username, place_name, lat, lng):
    """방문 기록 추가"""
    if username not in st.session_state.user_visits:
        st.session_state.user_visits[username] = []
    
    # XP 획득
    if username not in st.session_state.user_xp:
        st.session_state.user_xp[username] = 0
    
    xp_gained = PLACE_XP.get(place_name, 10)  # 기본 10XP, 장소별로 다른 XP
    st.session_state.user_xp[username] += xp_gained
    
    # 방문 데이터 생성
    visit_data = {
        "place_name": place_name,
        "latitude": lat,
        "longitude": lng,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "xp_gained": xp_gained,
        "rating": None
    }
    
    # 중복 방문 검사 (같은 날, 같은 장소)
    is_duplicate = False
    for visit in st.session_state.user_visits[username]:
        if (visit["place_name"] == place_name and 
            visit["date"] == visit_data["date"]):
            is_duplicate = True
            break
    
    if not is_duplicate:
        st.session_state.user_visits[username].append(visit_data)
        save_session_data()  # 방문 기록 저장
        return True, xp_gained
    return False, 0

def get_location_position():
    """사용자의 현재 위치를 반환"""
    try:
        from streamlit_js_eval import get_geolocation
        
        location = get_geolocation()
        if location and "coords" in location:
            return [location["coords"]["latitude"], location["coords"]["longitude"]]
    except Exception as e:
        st.warning(f"위치 정보를 가져올 수 없습니다: {e}")
        
    return DEFAULT_LOCATION  # 기본 위치 (서울시청)

# Google Maps 관련 함수
def create_google_maps_html(api_key, center_lat, center_lng, markers=None, zoom=13, language="ko"):
    """Google Maps HTML 생성"""
    if markers is None:
        markers = []
    
    # 카테고리별 마커 그룹화
    categories = {}
    for marker in markers:
        category = marker.get('category', '기타')
        if category not in categories:
            categories[category] = []
        categories[category].append(marker)
    
    # 범례 HTML
    legend_items = []
    for category, color in CATEGORY_COLORS.items():
        # 해당 카테고리의 마커가 있는 경우만 표시
        if any(m.get('category') == category for m in markers):
            count = sum(1 for m in markers if m.get('category') == category)
            legend_items.append(f'<div class="legend-item"><img src="http://maps.google.com/mapfiles/ms/icons/{color}-dot.png" alt="{category}"> {category} ({count})</div>')
    
    legend_html = "".join(legend_items)
    
    # 마커 JavaScript 코드 생성
    markers_js = ""
    for i, marker in enumerate(markers):
        color = marker.get('color', 'red')
        title = marker.get('title', '').replace("'", "\\'").replace('"', '\\"')
        info = marker.get('info', '').replace("'", "\\'").replace('"', '\\"')
        category = marker.get('category', '').replace("'", "\\'").replace('"', '\\"')
        
        # 마커 아이콘 URL
        icon_url = f"http://maps.google.com/mapfiles/ms/icons/{color}-dot.png"
        
        # 정보창 HTML 내용
        info_content = f"""
            <div style="padding: 10px; max-width: 300px;">
                <h3 style="margin-top: 0; color: #1976D2;">{title}</h3>
                <p><strong>분류:</strong> {category}</p>
                <div>{info}</div>
            </div>
        """
        
        # 마커 생성 코드
        markers_js += f"""
            var marker{i} = new google.maps.Marker({{
                position: {{ lat: {marker['lat']}, lng: {marker['lng']} }},
                map: map,
                title: '{title}',
                icon: '{icon_url}',
                animation: google.maps.Animation.DROP
            }});
            
            markers.push(marker{i});
            markerCategories.push('{category}');
            
            var infowindow{i} = new google.maps.InfoWindow({{
                content: '{info_content}'
            }});
            
            marker{i}.addListener('click', function() {{
                closeAllInfoWindows();
                infowindow{i}.open(map, marker{i});
                
                // 마커 바운스 애니메이션
                if (currentMarker) currentMarker.setAnimation(null);
                marker{i}.setAnimation(google.maps.Animation.BOUNCE);
                currentMarker = marker{i};
                
                // 애니메이션 종료
                setTimeout(function() {{
                    marker{i}.setAnimation(null);
                }}, 1500);
                
                // 부모 창에 마커 클릭 이벤트 전달
                window.parent.postMessage({{
                    'type': 'marker_click',
                    'id': {i},
                    'title': '{title}',
                    'lat': {marker['lat']},
                    'lng': {marker['lng']},
                    'category': '{category}'
                }}, '*');
            }});
            
            infoWindows.push(infowindow{i});
        """
    
    # 필터링 함수
    filter_js = """
        function filterMarkers(category) {
            for (var i = 0; i < markers.length; i++) {
                if (category === 'all' || markerCategories[i] === category) {
                    markers[i].setVisible(true);
                } else {
                    markers[i].setVisible(false);
                }
            }
            
            // 필터 버튼 활성화 상태 업데이트
            document.querySelectorAll('.filter-button').forEach(function(btn) {
                btn.classList.remove('active');
            });
            document.getElementById('filter-' + category).classList.add('active');
        }
    """
    
    # 마커 클러스터링 코드
    clustering_js = """
        // 마커 클러스터링
        var markerCluster = new MarkerClusterer(map, markers, {
            imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m',
            maxZoom: 15,
            gridSize: 50
        });
    """
    
    # 전체 HTML 코드 생성
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>서울 관광 지도</title>
        <meta charset="utf-8">
        <style>
            #map {{
                height: 100%;
                width: 100%;
                margin: 0;
                padding: 0;
            }}
            html, body {{
                height: 100%;
                margin: 0;
                padding: 0;
                font-family: 'Noto Sans KR', Arial, sans-serif;
            }}
            .map-controls {{
                position: absolute;
                top: 10px;
                left: 10px;
                z-index: 5;
                background-color: white;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 2px 6px rgba(0,0,0,.3);
                max-width: 90%;
                overflow-x: auto;
                white-space: nowrap;
            }}
            .filter-button {{
                margin: 5px;
                padding: 5px 10px;
                background-color: #f8f9fa;
                border: 1px solid #dadce0;
                border-radius: 4px;
                cursor: pointer;
            }}
            .filter-button:hover {{
                background-color: #e8eaed;
            }}
            .filter-button.active {{
                background-color: #1976D2;
                color: white;
            }}
            #legend {{
                font-family: 'Noto Sans KR', Arial, sans-serif;
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
                bottom: 25px;
                box-shadow: 0 2px 6px rgba(0,0,0,.3);
                font-size: 12px;
                padding: 10px;
                position: absolute;
                right: 10px;
                z-index: 5;
            }}
            .legend-item {{
                margin-bottom: 5px;
                display: flex;
                align-items: center;
            }}
            .legend-item img {{
                width: 20px;
                height: 20px;
                margin-right: 5px;
            }}
            .custom-control {{
                background-color: #fff;
                border: 0;
                border-radius: 2px;
                box-shadow: 0 1px 4px -1px rgba(0, 0, 0, 0.3);
                margin: 10px;
                padding: 0 0.5em;
                font: 400 18px Roboto, Arial, sans-serif;
                overflow: hidden;
                height: 40px;
                cursor: pointer;
            }}
        </style>
        <script src="https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/markerclusterer.js"></script>
    </head>
    <body>
        <div id="map"></div>
        
        <!-- 카테고리 필터 -->
        <div class="map-controls" id="category-filter">
            <div style="margin-bottom: 8px; font-weight: bold;">카테고리 필터</div>
            <button id="filter-all" class="filter-button active" onclick="filterMarkers('all')">전체 보기</button>
            {' '.join([f'<button id="filter-{cat}" class="filter-button" onclick="filterMarkers(\'{cat}\')">{cat}</button>' for cat in categories.keys()])}
        </div>
        
        <!-- 지도 범례 -->
        <div id="legend">
            <div style="font-weight: bold; margin-bottom: 8px;">지도 범례</div>
            {legend_html}
        </div>
        
        <script>
            // 지도 변수
            var map;
            var markers = [];
            var markerCategories = [];
            var infoWindows = [];
            var currentMarker = null;
            
            // 모든 정보창 닫기
            function closeAllInfoWindows() {{
                for (var i = 0; i < infoWindows.length; i++) {{
                    infoWindows[i].close();
                }}
            }}
            
            function initMap() {{
                // 지도 생성
                map = new google.maps.Map(document.getElementById('map'), {{
                    center: {{ lat: {center_lat}, lng: {center_lng} }},
                    zoom: {zoom},
                    fullscreenControl: true,
                    mapTypeControl: true,
                    streetViewControl: true,
                    zoomControl: true,
                    mapTypeId: 'roadmap'
                }});
                
                // 현재 위치 버튼 추가
                const locationButton = document.createElement("button");
                locationButton.textContent = "📍 내 위치";
                locationButton.classList.add("custom-control");
                locationButton.addEventListener("click", () => {{
                    if (navigator.geolocation) {{
                        navigator.geolocation.getCurrentPosition(
                            (position) => {{
                                const pos = {{
                                    lat: position.coords.latitude,
                                    lng: position.coords.longitude,
                                }};
                                
                                // 부모 창에 현재 위치 전달
                                window.parent.postMessage({{
                                    'type': 'current_location',
                                    'lat': pos.lat,
                                    'lng': pos.lng
                                }}, '*');
                                
                                map.setCenter(pos);
                                map.setZoom(15);
                                
                                // 현재 위치 마커 추가
                                new google.maps.Marker({{
                                    position: pos,
                                    map: map,
                                    title: '내 위치',
                                    icon: {{
                                        path: google.maps.SymbolPath.CIRCLE,
                                        fillColor: '#4285F4',
                                        fillOpacity: 1,
                                        strokeColor: '#FFFFFF',
                                        strokeWeight: 2,
                                        scale: 8
                                    }}
                                }});
                            }},
                            () => {{
                                alert("위치 정보를 가져오는데 실패했습니다.");
                            }}
                        );
                    }} else {{
                        alert("이 브라우저에서는 위치 정보 기능을 지원하지 않습니다.");
                    }}
                }});
                
                map.controls[google.maps.ControlPosition.TOP_RIGHT].push(locationButton);
                
                // 범례를 지도에 추가
                map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(
                    document.getElementById('legend')
                );
                
                // 마커 추가
                {markers_js}
                
                // 마커 클러스터링
                {clustering_js}
                
                // 필터링 함수
                {filter_js}
                
                // 지도 클릭 이벤트
                map.addListener('click', function(event) {{
                    // 열린 정보창 닫기
                    closeAllInfoWindows();
                    
                    // 바운스 애니메이션 중지
                    if (currentMarker) currentMarker.setAnimation(null);
                    
                    // 클릭 이벤트 데이터 전달
                    window.parent.postMessage({{
                        'type': 'map_click',
                        'lat': event.latLng.lat(),
                        'lng': event.latLng.lng()
                    }}, '*');
                }});
            }}
        </script>
        <script src="https://maps.googleapis.com/maps/api/js?key={api_key}&callback=initMap&language={language}" async defer></script>
    </body>
    </html>
    """
    
    return html

def show_google_map(api_key, center_lat, center_lng, markers=None, zoom=13, height=600, language="한국어"):
    """Google Maps 컴포넌트 표시"""
    # 언어 코드 변환
    lang_code = LANGUAGE_CODES.get(language, "ko")
    
    # HTML 생성
    map_html = create_google_maps_html(
        api_key=api_key,
        center_lat=center_lat,
        center_lng=center_lng,
        markers=markers,
        zoom=zoom,
        language=lang_code
    )
    
    # HTML 컴포넌트로 표시
    st.components.v1.html(map_html, height=height, scrolling=False)
