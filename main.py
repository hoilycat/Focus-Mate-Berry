import time
import sqlite3
import datetime
import os
import platform 

from services.vision_service import BerryVision
from services.state_machine import BerryStateMachine
from services.spy_service import BerrySpy
from services.ai_service import BerryBrain
from services.messenger_service import BerryMessenger

try:
    from services.button_service import BerryButton
    BUTTON_AVAILABLE = True
except:
    BUTTON_AVAILABLE = False

# --- [화면 청소] ---
def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# --- [DB 함수] ---
def init_db():
    conn = sqlite3.connect("berry_log_final.db",timeout = 10)
    cursor = conn.cursor()
    
    # 1. 로그 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT, 
            user_name TEXT, 
            is_running INTEGER,
            is_seated INTEGER,    
            status TEXT, 
            message TEXT, 
            accumulated_time REAL, 
            goal_minutes INTEGER
        )
    ''')
    
    # 2. 업적 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,  is_running INTEGER,   
            goal_minutes INTEGER, final_status TEXT, completed_at TEXT
        )
    ''')
    
    # 3. 사용자 통계 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            user_name TEXT PRIMARY KEY, total_seconds REAL DEFAULT 0
        )
    ''')

    # 4. 명령어 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT, cmd TEXT, created_at TEXT
        )
    ''')

    conn.commit()
    conn.close()

def get_user_total_time(user_name):
    conn = sqlite3.connect("berry_log_final.db",timeout = 10)
    cursor = conn.cursor()
    cursor.execute("SELECT total_seconds FROM user_stats WHERE user_name = ?", (user_name,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

def get_last_session_time(user_name):
    try:
        conn = sqlite3.connect("berry_log_final.db",timeout = 10)
        cursor = conn.cursor()
            
        # 👇 [수정됨] is_running 조건을 삭제했어! 
        # 이제 "멈춤"이나 "리셋" 상태라도 무조건 가장 마지막 시간을 가져와.
        cursor.execute("""
            SELECT accumulated_time FROM logs 
            WHERE user_name = ? 
            ORDER BY timestamp DESC LIMIT 1
        """, (user_name,))
            
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0
    except:
        return 0

def update_user_total_time(user_name, added_seconds):
    conn = sqlite3.connect("berry_log_final.db",timeout = 10)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_stats (user_name, total_seconds) VALUES (?, ?)
        ON CONFLICT(user_name) DO UPDATE SET total_seconds = total_seconds + ?
    ''', (user_name, added_seconds, added_seconds))
    conn.commit()
    conn.close()

def save_log(user_name, is_running, is_seated, status, message, acc_time, goal_min):
    try:
        conn = sqlite3.connect("berry_log_final.db",timeout = 10)
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute(
            """INSERT INTO logs 
               (timestamp, user_name, is_running, is_seated, status, message, accumulated_time, goal_minutes) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (now, user_name, 1 if is_running else 0, is_seated, status, message, acc_time, goal_min)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"💾 DB 저장 에러: {e}")
        
def save_achievement(user_name, goal_min, final_status, session_id=None):
    try:
        conn = sqlite3.connect("berry_log_final.db",timeout = 10)
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if session_id is None:
            cursor.execute(
                "INSERT INTO achievements (user_name, goal_minutes, final_status, completed_at) VALUES (?, ?, ?, ?)",
                (user_name, goal_min, final_status, now)
            )
            new_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return new_id
        else:
            cursor.execute(
                "UPDATE achievements SET goal_minutes = ?, final_status = ?, completed_at = ? WHERE id = ?",
                (goal_min, final_status, now, session_id)
            )
            conn.commit()
            conn.close()
            return session_id
    except Exception as e:
        print(f"❌ 업적 저장 에러: {e}")
        return None

def check_command():
    cmd = None
    try:
        conn = sqlite3.connect("berry_log_final.db",timeout = 10)
        cursor = conn.cursor()
        cursor.execute("SELECT id, cmd FROM commands ORDER BY id ASC LIMIT 1")
        row = cursor.fetchone()
        if row:
            cmd_id, cmd = row
            cursor.execute("DELETE FROM commands WHERE id = ?", (cmd_id,))
            conn.commit()
        conn.close()
    except: pass
    return cmd

# --- [메인 실행] ---
def main():
    init_db()
    is_mac = (platform.system() == "Darwin")

    # 기본 설정
    display_state = "GROWTH_SEED"
    ai_message = "베리 가동 준비 완료! 🍓"
    is_seated = False
    goal_time = 10 
    user_name = "용용"
    button = None

    if not is_mac and BUTTON_AVAILABLE:
        try:
            button = BerryButton()
        except: pass
        
    vision = BerryVision()
    brain = BerryStateMachine()
    spy = BerrySpy()
    messenger = BerryMessenger()
    ai_brain = BerryBrain(goal_minutes=goal_time, user_name=user_name) 
    
    ai_brain.history_time = get_user_total_time(user_name)
    print(f"🍓 베리 가동 시작!")

    ai_brain.is_running = False
    record_saved = False 
    current_session_id = None 
    
    # 시간 기록 변수들 (초기화)
    absent_start_time = None
    doom_start_time = None        # 💀 DOOM 시작 시간
    distraction_start_time = None # 딴짓 시작 시간
    last_stage = ai_brain.get_evolution_stage()


    manual_stop = False # 사용자가 멈춤 명령을 내렸는지 여부

    while True:
        try:
            # 1. 센서 및 명령 확인 (매 루프마다 한 번씩만 수행)
            is_seated_real, is_turtle, head_angle, gaze, head_pitch, eyebrow_y = vision.check_status()
            remote_cmd = check_command()
            btn_action = button.check_status() if button else None
            
            
            
            # ---------------------------------------------------------
            # 3. ☀️ 자동 깨우기 및 대기 상태 처리
            # ---------------------------------------------------------
            # '내가 직접 멈춘 게 아닐 때만' 자동으로 깨우도록 수정!
            if not ai_brain.is_running and is_seated_real and not manual_stop:
                ai_brain.is_running = True
                ai_brain.last_update_time = time.time()
                ai_message = f"어! {user_name}아(야) 왔어? 기다리고 있었어! 다시 시작하자! 🔥"
            
             

            # 💡 터미널에 실시간으로 카메라가 용용이를 보고 있는지 출력
            # 이 글자가 False면 카메라가 사용자를 못 찾고 있는 상태
            print(f"\r👀 시력 테스트: [사람감지:{is_seated_real}] [각도:{head_angle:.2f}] [눈동자:{gaze}] [눈썹:{eyebrow_y:.2f}]", end="")


            # ---------------------------------------------------------
            # 2. 🚀 명령 처리 (START, STOP, RESET, HEAL, EXTEND)
            # ---------------------------------------------------------
            if remote_cmd:
                if remote_cmd.startswith("START"):
                    manual_stop = False # 👈 시작하면 깃발을 내려!
                    record_saved = False 
                    parts = remote_cmd.split("|")
                    if len(parts) == 3:
                        user_name = parts[1]
                        goal_time = int(parts[2])
                        ai_brain.update_user(user_name, goal_time)
                        
                        last_time = get_last_session_time(user_name)
                        goal_seconds = goal_time * 60
                        
                        if last_time >= goal_seconds - 0.5: 
                            ai_brain.accumulated_time = 0
                        else:
                            ai_brain.accumulated_time = last_time
                        
                        ai_brain.last_update_time = time.time() 
                        ai_brain.is_finished = False
                        ai_brain.is_running = True
                        brain.reset()
                        ai_message = f"오케이! {user_name}아(야), 다시 0부터 달려보자! 🚀"


                elif remote_cmd == "STOP":
                    ai_brain.is_running = False
                    manual_stop = True  # 👈 멈추면 "내가 멈췄어!"라고 깃발을 들어!
                    print("🕹️ 멈춤!")

                elif remote_cmd == "RESET":
                    ai_brain.accumulated_time = 0
                    ai_brain.history_time = 0
                    ai_brain.is_finished = False
                    ai_brain.is_running = False 
                    brain.reset()
                    update_user_total_time(user_name, -get_user_total_time(user_name))
                    ai_message = "처음부터 다시 시작하자! 🌱"
                    save_log(user_name, False, 0, "GROWTH_SEED", ai_message, 0, goal_time)
                    continue

                elif remote_cmd == "HEAL" or btn_action == "LONG":
                    brain.forgive()
                    spy.risk_meter = 0
                    distraction_start_time = None
                    doom_start_time = None
                    ai_message = "알겠어.. 이번만 봐줄게! 다시 해봐! 💖"

                elif remote_cmd.startswith("EXTEND"):
                    try:
                        new_goal = int(remote_cmd.split("|")[1])
                        ai_brain.GOAL_MINUTES = new_goal
                        ai_brain.is_finished = False 
                        record_saved = False 
                    except: pass

           
            # 여전히 자고 있다면? 여기서 루프 끝내기
            if not ai_brain.is_running:
                save_log(user_name, False, 0, "SLEEP", "용용이를 기다리는 중... 💤", ai_brain.accumulated_time, goal_time)
                time.sleep(1)
                continue

            # ---------------------------------------------------------
            # 4. 🏃 공부 중 로직 (is_running이 True일 때만 여기로 옴)
            # ---------------------------------------------------------
            if ai_brain.is_finished:
                current_state = "FINISHED"
                display_state = "FINISHED"
                ai_message = f"🎉 {goal_time}분 성공!! {user_name} 최고야! 🥰"
                
                if not record_saved:
                    final_stage = ai_brain.get_evolution_stage()
                    current_session_id = save_achievement(user_name, goal_time, final_stage, current_session_id)
                    update_user_total_time(user_name, ai_brain.accumulated_time)
                    record_saved = True 
            else:
                # [실시간 감지]
                spy_status, spy_app_name = spy.check_activity()

                #평상시 책을 읽으려 할때 고개를 30도로 숙이면 눈동자가 눈꺼풀에 가려지므로 고개 각도 범위를 넓게 설정(기존의 눈동자 조건은 제거)
                vision_distracted = (head_angle < 0.15 or head_angle > 0.85)
                # 3. 독서 감지 (고개 숙임)
                is_reading = False
                if head_pitch > 0.75: # '30도 숙임' 각도
                    vision_distracted = False # 고개 숙인 건 딴짓이 아니라고 선언!
                    is_reading = True
                    is_turtle = False # 📚 독서 중에는 거북목 판정에서 제외 (자비로운 베리)


                # [자리비움 판정] (1분 유예)
                if is_seated_real:
                    absent_start_time = None
                    is_seated = True         
                else:
                    if absent_start_time is None: absent_start_time = time.time()
                    is_seated = (time.time() - absent_start_time < 60)

                # [최종 상태 결정]
                if not is_seated:
                    current_state = "SLEEP"
                    app_name = "사용자 부재중"
                elif spy_status in ["EATING", "SICK", "DOOM"]:
                    app_name = spy_app_name
                    if distraction_start_time is None: distraction_start_time = time.time()
                    elapsed = time.time() - distraction_start_time
                    if elapsed < 10: current_state = "EATING"
                    elif elapsed < 30: current_state = "SICK"
                    else: current_state = "DOOM"
                elif vision_distracted:
                    current_state = "SLEEP"
                    app_name = f"{user_name}이가 다시 집중할 때까지 쉬고 있을께!"
                else:
                    distraction_start_time = None
                    current_state = brain.update(is_seated, is_turtle, spy_status)
                    app_name = ""

                # [메시지 생성 및 진화 체크]
                if current_state == "DOOM":
                    if doom_start_time is None: doom_start_time = time.time()
                    elapsed = time.time() - doom_start_time
                    if elapsed > 20:    display_state = "CALLING_2"
                    elif elapsed > 12:  display_state = "CALLING_1"
                    elif elapsed > 5:   display_state = "DOOM_STUCK"
                    else:               display_state = "DOOM"

                    if elapsed > 12:
                        success, _ = messenger.send_report(user_name, app_name)
                        ai_message = f"📞 미안해.. 너무 아파서 연락드렸어.. 😭"
                    elif elapsed > 5:
                        ai_message = "🗿 으으.. 배가 너무 아파서 굳어버렸어.."
                    else:
                        ai_message = "🤢 앗.. 갑자기 배가 너무 아파.. 어떡하지?"
                else:
                    doom_start_time = None
                    current_stage = ai_brain.get_evolution_stage()
                    
                    if current_state == "GROWTH":
                        if current_stage != last_stage:
                            if "SPROUT" in current_stage: ai_message = f"🌱 와! {user_name}아, 나 새싹 돋았어! ✨"
                            elif "SMALL" in current_stage: ai_message = "🍓 대박! 나 이제 열매야! 으쌰!"
                            elif "BIG" in current_stage: ai_message = f"🍎 짠! {user_name} 덕분에 다 컸어! 🥰"
                            last_stage = current_stage
                        else:
                            ai_message = ai_brain.think(current_state, app_name)
                        
                        status_text = "공부 중 🔥"
                        if is_turtle: status_text = "거북목 주의! 🐢"
                        if is_reading: status_text = "독서 중 📖"
                        
                        if not is_seated_real:
                            ai_message = "👀 어라? 어디 봐? 너무 숙인 거 아냐?"
                            status_text = "딴짓 의심 🔍"
                            
                        display_state = f"{current_stage} ({status_text})"
                    else:
                        display_state = current_state
                        ai_message = ai_brain.think(current_state, app_name)

            # 5. DB 저장
            save_log(user_name, ai_brain.is_running, 1 if is_seated_real else 0, display_state, ai_message, ai_brain.accumulated_time, goal_time)
            time.sleep(1)

        except Exception as e:
            print(f"❌ 에러: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()