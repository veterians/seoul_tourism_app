import streamlit as st
import pandas as pd
import os
import json
from pathlib import Path
import config

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
        st.session_state.google_maps_api_key = st.secrets["google_maps_api_key"] if "google_maps_api_key" in st.secrets else ""
    
    # 저장된 세션 데이터 로드
    load_session_data()

def load_session_data():
    """저장된 세션 데이터 로드"""
    try:
        if os.path.exists(config.SESSION_DATA_FILE):
            with open(config.SESSION_DATA_FILE, "r", encoding="utf-8") as f:
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
        os.makedirs(os.path.dirname(config.SESSION_DATA_FILE), exist_ok=True)
        
        data = {
            "users": st.session_state.users,
            "user_visits": st.session_state.user_visits,
            "user_xp": st.session_state.user_xp
        }
        
        with open(config.SESSION_DATA_FILE, "w", encoding="utf-8") as f:
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
            
            for category, keywords in config.FILE_CATEGORIES.items():
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
    color = config.CATEGORY_COLORS.get(category, "gray")
    
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
