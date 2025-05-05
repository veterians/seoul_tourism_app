import streamlit as st
import json
import config

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
    for category, color in config.CATEGORY_COLORS.items():
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
    lang_code = config.LANGUAGE_CODES.get(language, "ko")
    
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
