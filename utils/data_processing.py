import streamlit as st
import pandas as pd
from datetime import datetime
import config
from utils.data_loader import save_session_data

def calculate_level(xp):
    """레벨 계산 함수"""
    return int(xp / config.XP_PER_LEVEL) + 1

def calculate_xp_percentage(xp):
    """경험치 비율 계산 (다음 레벨까지)"""
    current_level = calculate_level(xp)
    xp_for_current_level = (current_level - 1) * config.XP_PER_LEVEL
    xp_for_next_level = current_level * config.XP_PER_LEVEL
    
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
    
    xp_gained = config.PLACE_XP.get(place_name, 10)  # 기본 10XP, 장소별로 다른 XP
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
        
    return config.DEFAULT_LOCATION  # 기본 위치 (서울시청)
