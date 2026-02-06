import streamlit as st
import sqlite3
import pandas as pd
import time
import os

# 1. 화면 설정 (넓게 보기)
st.set_page_config(
    page_title="Focus-Mate Berry",
    page_icon="🍓",
    layout="wide"
)

# 2. 스타일 꾸미기 (CSS)
st.markdown("""
    <style>
    /* 1. 배경색 (연한 핑크) */
    .stApp {
        background-color: #FFF0F5;
    }

    /* 2. 모든 글씨 강제로 검은색으로 만들기 (중요! ⭐) */
    h1, h2, h3, p, div, span, label {
        color: #333333 !important; /* 진한 회색 */
    }

    /* 3. 글씨 크기 키우기 (노안 치료 🔍) */
    p {
        font-size: 18px !important; /* 본문 글씨 18px */
        line-height: 1.6; /* 줄 간격 넓게 */
    }
    
    /* 4. 제목 스타일 */
    h1 {
        font-size: 32px !important;
        color: #FF1493 !important; /* 제목만 진한 핑크 */
        font-weight: 700;
    }

    /* 5. 베리의 말풍선 강조 */
    .stAlert {
        background-color: white; /* 말풍선 배경 흰색 */
        border: 2px solid #FF69B4; /* 테두리 핑크 */
        border-radius: 15px;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 가져오기 함수 (DB 읽기)
def get_latest_log():
    try:
        # DB 파일 위치가 중요! (main.py랑 같은 위치에 있다고 가정)
        db_path = "berry_log.db"
        if not os.path.exists(db_path):
            return None
            
        conn = sqlite3.connect(db_path)
        # 제일 마지막(최신) 1줄만 가져오기
        df = pd.read_sql_query("SELECT * FROM logs ORDER BY id DESC LIMIT 1", conn)
        conn.close()
        
        if not df.empty:
            return df.iloc[0]
        return None
    except Exception as e:
        st.error(f"DB 읽기 오류: {e}")
        return None

# --- [메인 화면 구성] ---

st.title("🍓 Focus-Mate Berry")
st.markdown("---")

# 실시간 갱신을 위한 빈 공간(Placeholder) 만들기
# (여기에 계속 덮어쓰기를 해서 애니메이션처럼 보이게 함!)
main_placeholder = st.empty()

while True:
    # 1. 최신 데이터 읽기
    row = get_latest_log()
    
    with main_placeholder.container():
        if row is None:
            st.warning("💤 베리가 아직 잠자고 있어요... (main.py를 실행해주세요!)")
        else:
            # 2. 상태에 따른 디자인 결정
            status = row['status']
            is_seated = row['is_seated']
            ai_msg = row['message'] # 🧠 DB에서 AI가 쓴 멘트 가져오기!
            
            # 기본값
            bg_color = "#E6FFFA"
            img_file = "assets/body_lv3.png"
            emoji = "🌱"

            # 배경색과 이미지는 상태(status) 따라 결정 (기존 로직 유지)
            if status == "GROWTH":
                emoji = "😎"
                bg_color = "#D1FAE5"
            elif status == "EATING":
                emoji = "🍿"
                bg_color = "#FEF3C7"
                img_file = "assets/action_eat.png"
            elif status == "WARNING":
                emoji = "🐢"
                bg_color = "#FFEDD5"
                img_file = "assets/face_sweat.png"
            elif status == "SICK":
                emoji = "🤢"
                bg_color = "#FEE2E2"
                img_file = "assets/face_sweat.png"
            elif status == "SLEEP":
                emoji = "💤"
                bg_color = "#F1F5F9"
                img_file = "assets/action_sleep.png"
            elif status == "DOOM":
                emoji = "🚑"
                bg_color = "#FECACA"
                img_file = "assets/action_sleep.png"
            # 3. 화면 그리기 (컬럼 나누기)
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # 배경색 박스 안에 이미지 넣기
                st.markdown(f"""
                <div class="status-box" style="background-color: {bg_color};">
                    <div style="font-size: 100px;">{emoji}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 이미지 파일이 실제로 있으면 그걸 보여주고, 없으면 이모지만 둠
                if os.path.exists(img_file):
                    st.image(img_file, use_container_width=True)

            with col2:
                st.markdown(f"### 상태: **{status}**")
                
                # 말풍선 디자인
                st.info(f"🗨️ **베리:** {ai_msg}")

                # 통계 수치 (메트릭)
                m1, m2, m3 = st.columns(3)
                m1.metric("🌡️ 온도", f"{row['temp']}°C", "0.5°C")
                m2.metric("💧 습도", f"{row['humid']}%", "-2%")
                m3.metric("🪑 착석 여부", "착석 중" if is_seated else "비움")

            # 4. 하단 로그 (개발자용)
            with st.expander("🛠️ 시스템 로그 확인"):
                st.write(row)

    # 2초마다 새로고침 (이게 바로 '같이 움직이는' 효과!)
    time.sleep(2)