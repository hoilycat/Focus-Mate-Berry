import time
import platform
import subprocess

# ---------------------------------------------------------
# 🛠️ 라이브러리 세팅 (OS에 따라 다르게 가져오기)
# ---------------------------------------------------------
os_type = platform.system()
gw = None

if os_type == "Windows":
    try:
        import pygetwindow as gw
    except ImportError:
        print("⚠️ 윈도우인데 'pygetwindow'가 없어요! (pip install pygetwindow 필요)")

class BerrySpy:
    def __init__(self):
        self.os_type = platform.system()
        # 🕵️‍♀️ 감시 대상 (대소문자 상관없이 잡음)
        self.BAD_APPS = ['YouTube', 'Netflix', 'League', 'Steam', 'Discord', 'Instagram', 'KakaoTalk', 'Melon']
        self.risk_meter = 0

    def check_activity(self):
        detected_app = ""
        is_distracted = False
        current_activity = "" # 현재 뭘 하는지 기록용

        # =========================================================
        # 🪟 1. 윈도우 (Windows) - 천리안 모드 (모든 창 검사)
        # =========================================================
        if self.os_type == "Windows" and gw:
            try:
                # 현재 활성화된 창 (제일 중요)
                active_window = gw.getActiveWindow()
                if active_window:
                    current_activity = active_window.title

                # 백그라운드까지 다 뒤지기
                all_titles = gw.getAllTitles()
                for title in all_titles:
                    if not title: continue
                    for bad in self.BAD_APPS:
                        if bad.lower() in title.lower():
                            detected_app = bad
                            is_distracted = True
                            break
                    if is_distracted: break
            except Exception as e:
                print(f"윈도우 감지 에러: {e}")

        # =========================================================
        # 🍎 2. 맥북 (Mac) - 활성창 집중 감시 (애플스크립트)
        # =========================================================
        elif self.os_type == "Darwin":
            current_activity = self.get_active_window_title_mac()
            
            # 맥은 현재 보고 있는 화면(활성창)을 기준으로 판단
            if current_activity:
                for bad in self.BAD_APPS:
                    if bad.lower() in current_activity.lower():
                        detected_app = bad
                        is_distracted = True
                        break

        # =========================================================
        # ⚖️ 3. 위험도 계산 (판사 베리 👩‍⚖️)
        # =========================================================
        if is_distracted:
            self.risk_meter += 2  # 딴짓하면 게이지 팍팍 오름! (가중치 증가)
            print(f"🚨 딴짓 감지! [{detected_app}] 위험도: {self.risk_meter}")
        else:
            if self.risk_meter > 0:
                self.risk_meter -= 1 # 공부하면 천천히 내려감
            # print(f"✅ 공부 중... ({current_activity})")

        # 최대 위험도 제한 (너무 무한히 올라가지 않게)
        if self.risk_meter > 20: self.risk_meter = 20

        # 상태 반환
        if self.risk_meter == 0:
            return 'STUDY', ""
        elif self.risk_meter <= 5:
            return 'EATING', detected_app # "냠냠... 과자 먹니?"
        elif self.risk_meter <= 10:
            return 'SICK', detected_app   # "으앙... 나 아파..."
        else:
            return 'DOOM', detected_app   # "살려줘!!! (비상)"

    # 🍎 맥북 전용: AppleScript로 크롬/사파리 탭 제목까지 가져오기
    def get_active_window_title_mac(self):
        try:
            script = '''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
            end tell
            
            if frontApp is "Google Chrome" then
                tell application "Google Chrome" to return title of active tab of front window
            else if frontApp is "Safari" then
                tell application "Safari" to return name of current tab of window 1
            else
                return frontApp
            end if
            '''
            # 스크립트 실행 (에러 나면 무시하고 빈 문자열 반환)
            result = subprocess.check_output(["osascript", "-e", script], stderr=subprocess.DEVNULL)
            return result.decode("utf-8").strip()
        except:
            return "Unknown"

# 테스트 실행
if __name__ == "__main__":
    spy = BerrySpy()
    while True:
        status, app = spy.check_activity()
        print(f"상태: {status} / 앱: {app}")
        time.sleep(1)