import platform
import time

# 운영체제 확인 (맥/윈도우 vs 라즈베리파이)
OS_TYPE = platform.system()
IS_RASPBERRY = False

try:
    if OS_TYPE == "Linux":
        # 라즈베리파이인지 확인 (GPIO 라이브러리 체크)
        import RPi.GPIO as GPIO
        IS_RASPBERRY = True
    else:
        # 맥/윈도우용 키보드 감지 라이브러리
        # 터미널에서: pip install keyboard (윈도우) 또는 pynput (맥)
        from pynput import keyboard
except ImportError:
    pass

class BerryButton:
    def __init__(self):
        self.is_pressed = False
        self.press_start_time = 0
        
        # 🍓 라즈베리 파이 설정 (GPIO 18번 핀 사용 예시)
        if IS_RASPBERRY:
            self.PIN = 18
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
        # 💻 맥북/윈도우 설정 (키보드 엔터키를 버튼처럼 씀)
        else:
            self.listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
            self.listener.start()

    # --- [맥북용 키보드 감지] ---
    def on_key_press(self, key):
        if key == keyboard.Key.enter: # 엔터키를 버튼으로 씀!
            self.is_pressed = True

    def on_key_release(self, key):
        if key == keyboard.Key.enter:
            self.is_pressed = False
    # ---------------------------

    def check_status(self):
        """
        버튼의 현재 상태를 확인해서 'CLICK', 'LONG', 'START' 중 하나를 리턴함
        """
        # 1. 버튼이 눌려있는지 확인
        current_pressed = False
        
        if IS_RASPBERRY:
            # GPIO는 스위치 떼면 1(True), 누르면 0(False)인 경우가 많음 (풀업)
            # 회로에 따라 다르니 반대면 `not GPIO.input(self.PIN)` 으로 변경
            if GPIO.input(self.PIN) == False: 
                current_pressed = True
        else:
            current_pressed = self.is_pressed

        # 2. 누르기 시작했다! (타이머 잼)
        if current_pressed and self.press_start_time == 0:
            self.press_start_time = time.time()
            return None

        # 3. 손을 뗐다! (얼마나 눌렀는지 계산)
        elif not current_pressed and self.press_start_time != 0:
            duration = time.time() - self.press_start_time
            self.press_start_time = 0 # 리셋
            
            if duration > 3.0: # 3초 이상 (시작)
                return "START"
            elif duration > 0.5: # 0.5초 이상 (모드 변경)
                return "LONG"
            else: # 살짝 (시간 추가)
                return "CLICK"
        
        # 4. 계속 누르고 있는 중... (피드백용)
        elif current_pressed and self.press_start_time != 0:
            duration = time.time() - self.press_start_time
            if duration > 3.0:
                return "HOLDING_START" # 3초 넘어가면 '곧 시작합니다!' 표시용
            
        return None

    def cleanup(self):
        if IS_RASPBERRY:
            GPIO.cleanup()