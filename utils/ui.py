import streamlit as st

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
    from utils.data_processing import calculate_level, calculate_xp_percentage
    import config
    
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
        st.caption(f"다음 레벨까지 {config.XP_PER_LEVEL - (user_xp % config.XP_PER_LEVEL)} XP 남음")
