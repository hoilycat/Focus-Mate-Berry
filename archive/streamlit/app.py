import streamlit as st
import sqlite3
import pandas as pd
import time
import os
import datetime

# --- [1. 페이지 설정] ---
st.set_page_config(page_title="Focus Mate Berry", page_icon="🍓", layout="centered")

DB_PATH = "berry_log_final.db"

# --- [2. 데이터베이스 함수] ---
def get_latest_log():
    try:
        if not os.path.exists(DB_PATH): return None
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        df = pd.read_sql("SELECT * FROM logs ORDER BY id DESC LIMIT 1", conn)
        conn.close()
        return df.iloc[0] if not df.empty else None
    except: return None

def get_achievements():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        df = pd.read_sql("SELECT user_name, goal_minutes, final_status, completed_at FROM achievements ORDER BY id DESC", conn)
        conn.close()
        return df
    except: return pd.DataFrame()

def send_command(cmd):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO commands (cmd, created_at) VALUES (?, ?)", (cmd, now))
        conn.commit()
        conn.close()
        return True
    except: return False

# --- [3. 세션 상태 초기화] ---
if 'is_running' not in st.session_state:
    st.session_state['is_running'] = False

# 초기값 로드 (에러 방지용 안전 로직)
if 'user_name' not in st.session_state:
    last_log = get_latest_log()
    
    # 데이터가 있고, 그 안에 'user_name'이라는 칸이 실제로 존재할 때만 가져옴
    if last_log is not None and 'user_name' in last_log:
        st.session_state['user_name'] = str(last_log['user_name'])
        st.session_state['goal_time'] = int(last_log.get('goal_minutes', 10))
    else:
        # 데이터가 없거나 예전 버전 DB라면 기본값 사용
        st.session_state['user_name'] = "용용"
        st.session_state['goal_time'] = 10

# --- [4. 스타일 설정] ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF0F5; }
    [data-testid="stSidebar"] { background-color: #FFE4E1; }
    .chat-bubble {
        background-color: #FFFFFF; color: #333333; border: 2px solid #FFB6C1;
        border-radius: 20px; padding: 20px; text-align: center; font-weight: bold; margin-bottom: 20px;
    }
    .stProgress > div > div > div > div { background-color: #FF69B4; }
    </style>
""", unsafe_allow_html=True)

st.title("🍓 Focus Mate Berry")

#--- 폰트 설젇---

# 구글 폰트에서 가져올 폰트 이름과 CSS 적용 이름을 매핑.
FONT_OPTIONS = {
    "기본 고딕": "Pretendard",
    "귀여운 개구체": "Gaegu",
    "둥글둥글 나눔스퀘어": "NanumSquareRound",
    "감성 가득 나눔명조": "Nanum Myeongjo",
    "힘찬 검은고딕": "Black Han Sans"
}

# 세션에 폰트 저장
if 'selected_font' not in st.session_state:
    st.session_state['selected_font'] = "기본 고딕"

# --- [사이드바에 폰트 선택창 추가] ---
with st.sidebar:
    st.write("---")
    st.subheader("🎨 분위기 바꾸기")
    # 사용자가 폰트를 선택하면 세션에 즉시 반영
    st.session_state['selected_font'] = st.selectbox(
        "글꼴 선택", 
        options=list(FONT_OPTIONS.keys()),
        index=list(FONT_OPTIONS.keys()).index(st.session_state['selected_font'])
    )

# --- [선택된 폰트를 앱 전체에 적용하는 CSS] ---
selected_font_family = FONT_OPTIONS[st.session_state['selected_font']]

st.markdown(f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Gaegu&family=Black+Han+Sans&family=Nanum+Myeongjo&display=swap" rel="stylesheet">
    <style>
        /* 1. 일반적인 텍스트 요소에만 폰트 적용 (아이콘 제외) */
        html, body, p, div, span, label, h1, h2, h3, h4, h5, h6, .stMarkdown {{
            font-family: '{selected_font_family}', sans-serif;
        }}

        /* 2. 버튼과 입력창에 폰트 적용 */
        .stButton button, .stSelectbox select, .stTextInput input, .stNumberInput input {{
            font-family: '{selected_font_family}', sans-serif !important;
        }}

        /* ---------------------------------------------------------
           ☀️ 라이트 모드 (Light Mode) 설정
           --------------------------------------------------------- */
        @media (prefers-color-scheme: light) {{
            .stApp {{
                background-color: #FFF0F5; /* 연한 핑크 배경 */
            }}
            h1, h2, h3, p, label {{
                color: #333333 !important; /* 진한 회색 글자 */
            }}
            .chat-bubble {{
                background-color: #FFFFFF;
                color: #333333;
                border: 2px solid #FFB6C1;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            }}
            [data-testid="stMetricValue"] {{
                color: #FF69B4 !important; /* 쨍한 핑크 */
            }}
            .stProgress > div > div > div > div {{
                background-color: #FF69B4 !important;
            }}
        }}

        /* ---------------------------------------------------------
           🌙 다크 모드 (Dark Mode) 설정
           --------------------------------------------------------- */
        @media (prefers-color-scheme: dark) {{
            .stApp {{
                background-color: #1E1E1E; /* 다크 그레이 배경 */
            }}
            h1, h2, h3 {{
                color: #E197A0 !important; /* 채도 낮은 인디핑크 */
            }}
            p, label, span {{
                color: #E0E0E0 !important; /* 부드러운 화이트 */
            }}
            .chat-bubble {{
                background-color: #2D2D2D;
                color: #E0E0E0;
                border: 2px solid #A67C81; /* 저채도 핑크 테두리 */
                box-shadow: none;
            }}
            [data-testid="stMetricValue"] {{
                color: #E197A0 !important; /* 저채도 핑크 */
            }}
            /* 다크모드 진행바 색상 */
            .stProgress > div > div > div > div {{
                background-color: #A67C81 !important;
            }}
            /* 사이드바 다크모드 대응 */
            [data-testid="stSidebar"] {{
                background-color: #262626 !important;
            }}
        }}
         /* 2. 아이콘 보호 로직 (지난번 버그 해결) */
        [data-testid="stIcon"], .st-emotion-cache-1v0vkay, i, 
        button[title="Collapse sidebar"] span, button[title="Expand sidebar"] span {{
            font-family: 'Material Symbols Outlined' !important;
        }}

        /* 사이드바 접기 버튼 글자 안 보이게 방어 */
        button[title="Collapse sidebar"] span, 
        button[title="Expand sidebar"] span {{
            font-family: 'Material Symbols Outlined' !important;
        }}
    </style>
""", unsafe_allow_html=True)





# --- [5. 사이드바 (입력창)] ---
# 사이드바는 루프와 상관없이 독립적으로 작동해야 합니다.
with st.sidebar:
    st.header("🕹️ 베리 설정")
    
    # 위젯의 값이 바뀌면 즉시 session_state에 반영됨
    st.session_state['user_name'] = st.text_input("이름 (닉네임)", value=st.session_state['user_name'])
    st.session_state['goal_time'] = st.number_input("목표 시간 (분)", min_value=1, value=st.session_state['goal_time'])
    
    st.write("---")

    if st.session_state['is_running']:
        st.success(f"🔥 {st.session_state['user_name']}, 열공 중!")
        if st.button("⏹️ 그만하기 (Stop)", width="stretch"):
            send_command("STOP")
            st.session_state['is_running'] = False
            st.rerun()
    else:
        if st.button("🚀 시작하기 (Start)", width="stretch", type="primary"):
            st.session_state['is_running'] = True
            send_command(f"START|{st.session_state['user_name']}|{st.session_state['goal_time']}")
            st.rerun()

    if st.session_state['is_running']:
        if st.button("➕ 10분 더 열공 (연장)", key="extend_btn", width="stretch"):
            st.session_state['goal_time'] += 10
            send_command(f"EXTEND|{st.session_state['goal_time']}")
            st.toast("10분 연장 완료! 🔥")
            st.rerun()

    if st.button("💊 베리야 미안해 (회복)", width="stretch"):
        send_command("HEAL")
        st.balloons()

# --- [6. 메인 베리 화면 (Fragment로 분리)] ---
# 이 함수는 1초마다 자동으로 실행되지만, 사이드바의 위젯은 방해하지 않음.
@st.fragment(run_every=1)
def show_berry_screen():
    log = get_latest_log()
    
    # 1. 데이터 바인딩
    if log is not None and st.session_state['is_running']:
        status = log['status']
        message = log['message']
        acc_sec = log['accumulated_time']
        goal_min = log['goal_minutes']
        temp = log['temp']
        humid = log['humid']
    else:
        # 대기 상태일 때
        status = "GROWTH_SEED"
        # 💡 여기가 핵심: 사용자가 입력 중인 이름을 실시간으로 반영
        message = f"베리 준비 완료! 목표는 {st.session_state['goal_time']}분이야? {st.session_state['user_name']}(아)야 파이팅! 🐥💕"
        acc_sec = 0.0
        goal_min = st.session_state['goal_time']
        temp, humid = 24.0, 50.0

    # 이미지 맵
    STATUS_MAP = {
        "GROWTH_SEED": {"icon": "🌱", "img": "image/seed.png"},
        "GROWTH_SPROUT": {"icon": "🌿", "img": "image/sprout.gif"},
        "GROWTH_SMALL": {"icon": "🍓", "img": "image/small.png"},
        "GROWTH_BIG": {"icon": "🍎", "img": "image/big.png"},
        "GROWTH_FAIRY": {"icon": "✨", "img": "image/finishberry.gif"},
        "SLEEP": {"icon": "💤", "img": "image/sleep.png"},
        "EATING": {"icon": "😋", "img": "image/eating.png"},
        "SICK": {"icon": "🤒", "img": "image/sick.png"},
        "DOOM": {"icon": "💀", "img": "image/doom.png"},
        "FINISHED": {"icon": "🎉", "img": "image/finished.png"},
    }

    # UI 렌더링
    config = STATUS_MAP.get(status, STATUS_MAP["GROWTH_SEED"])
    if os.path.exists(config["img"]):
        st.image(config["img"], width=400)
    else:
        st.markdown(f"<h1 style='text-align:center; font-size:100px;'>{config['icon']}</h1>", unsafe_allow_html=True)

    st.markdown(f'<div class="chat-bubble"><b>🍓 베리:</b><br>{message}</div>', unsafe_allow_html=True)

    # 진행바
    total_sec = goal_min * 60
    progress = min(acc_sec / total_sec, 1.0)
    remaining_min = max(goal_min - int(acc_sec // 60), 0)
    
    st.progress(progress)
    st.caption(f"⏳ 진행: {int(progress*100)}% (남은 시간: {remaining_min}분 / 목표: {goal_min}분)")

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("📡 상태", status)
    with col2: st.metric("🌡️ 온도", f"{temp}°C")
    with col3: st.metric("💧 습도", f"{humid}%")

    if status in ["EATING", "SICK", "DOOM"]:
        st.error("🚨 딴짓 감지! 베리가 아파하고 있어!")
    if status == "FINISHED":
        st.success("🎉 목표 달성 완료!")

    # 명예의 전당
    st.write("---")
    with st.expander("🏆 나의 베리 성장 기록 (명예의 전당)"):
        history_df = get_achievements()
        if not history_df.empty:
            emoji_map = {
                "GROWTH_SEED": "🌱 씨앗", "GROWTH_SPROUT": "🌿 새싹",
                "GROWTH_SMALL": "🍓 작은 딸기", "GROWTH_BIG": "🍎 큰 딸기",
                "GROWTH_FAIRY": "✨ 요정 베리", "FINISHED": "🎉 달성완료"
            }
            history_df['final_status'] = history_df['final_status'].map(lambda x: emoji_map.get(x, x))
            st.dataframe(history_df, width="stretch", hide_index=True)

# 메인 화면 실행
show_berry_screen()