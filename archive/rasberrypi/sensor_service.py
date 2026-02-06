import random
import platform

# 운영체제 확인 (Windows면 True, 라즈베리파이면 False)
IS_WINDOWS = platform.system() == 'Windows'

if not IS_WINDOWS:
    # 라즈베리 파이에서만 실행되는 라이브러리
    try:
        import Adafruit_DHT
        # import smbus (나중에 조도센서 쓸 때 필요)
    except ImportError:
        print("⚠️ 센서 라이브러리가 없습니다. 가상 모드로 동작합니다.")
        IS_WINDOWS = True

class BerrySensor:
    def __init__(self):
        self.dht_sensor = 11      # DHT11 센서 사용
        self.dht_pin = 4          # GPIO 4번 핀에 연결 (변경 가능)
        print(f"🌡️ 센서 서비스 시작 (모드: {'가상(PC)' if IS_WINDOWS else '리얼(Pi)'})")

    def read_environment(self):
        """
        [리턴] { 'temp': 'good'/'bad', 'humidity': 50, 'light': 'bright'/'dark' }
        """
        
        # 1. 데이터 읽기 (PC vs Pi 분기)
        if IS_WINDOWS:
            # [가상 데이터] 테스트용 랜덤 값 생성
            temp = random.randint(20, 35) # 20~35도 사이 랜덤
            humid = random.randint(40, 80)
            light_val = random.randint(0, 100) # 0(어두움) ~ 100(밝음)
        else:
            # [실제 데이터] 라즈베리 파이 센서 읽기
            # humidity, temperature = Adafruit_DHT.read_retry(self.dht_sensor, self.dht_pin)
            # (지금은 에러 방지를 위해 일단 가상값 사용, 나중에 주석 해제!)
            temp = 25 
            humid = 50
            light_val = 80 

        # 2. 상태 판단 로직 (규칙 정하기)
        env_status = {
            'temp_val': temp,
            'light_val': light_val,
            'status': 'good' # 기본은 좋음
        }

        # 더우면? (28도 이상)
        if temp >= 28:
            env_status['status'] = 'bad'
        
        # 어두우면? (빛 30 이하)
        if light_val < 30:
            env_status['light'] = 'dark'
        else:
            env_status['light'] = 'bright'

        print(f"🌿 환경 데이터: 온도{temp}°C / 조도{light_val} / 상태:{env_status['status']}")
        return env_status