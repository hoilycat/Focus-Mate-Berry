import subprocess
import sys
import time
import os

def run_berry():
    print("🍓 베리 시스템 가동 중... (뇌 + 얼굴 연결)")
    
    # 1. 뇌 깨우기 (main.py 실행)
    # shell=True를 쓰면 별도 창이 뜰 수도 있지만, 여기선 한 창에 로그를 모아볼게!
    brain_process = subprocess.Popen([sys.executable, "main.py"])
    print("🧠 베리 뇌(Back-end) 연결 완료!")

    # 2. 얼굴 켜기 (Streamlit 실행)
    # "streamlit run app.py" 명령어를 파이썬으로 실행하는 방식이야
    face_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py"])
    print("😊 베리 얼굴(Front-end) 연결 완료!")
    
    print("="*40)
    print("🚀 베리가 실행되었습니다! 멈추려면 'Ctrl + C'를 누르세요.")
    print("="*40)

    try:
        # 두 프로그램이 꺼지지 않게 계속 감시함
        while True:
            time.sleep(1)
            # 만약 둘 중 하나라도 죽으면? 같이 꺼버리기 (옵션)
            if brain_process.poll() is not None:
                print("❌ 베리 뇌가 멈췄습니다. 시스템을 종료합니다.")
                break
            if face_process.poll() is not None:
                print("❌ 베리 얼굴이 닫혔습니다. 시스템을 종료합니다.")
                break

    except KeyboardInterrupt:
        print("\n👋 시스템 종료 요청 감지!")
    
    finally:
        # 종료될 때 둘 다 확실하게 죽이기 🔫
        print("💀 시스템 셧다운 중...")
        brain_process.terminate()
        face_process.terminate()
        brain_process.wait()
        face_process.wait()
        print("✅ 베리가 안전하게 잠들었습니다.")

if __name__ == "__main__":
    run_berry()