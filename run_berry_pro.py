import subprocess
import sys
import time
import os
import platform

def run_berry_pro():
    # 항상 이 스크립트가 있는 폴더로 이동!
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    current_os = platform.system()
    is_windows = (current_os == "Windows")

    print(f"🍎 {current_os} 환경에서 베리 프로 가동 시작! 🍎")

    python_cmd = sys.executable

    # 2. 베리 엔진 실행 (절대경로로 실행)
    engine = subprocess.Popen([python_cmd, os.path.join(script_dir, "main.py")], shell=is_windows)
    print("🧠 1. 베리 엔진 가동!")

    # 3. 백엔드 API
    api = subprocess.Popen([python_cmd, os.path.join(script_dir, "backend_api.py")], shell=is_windows)
    print("🔌 2. API 서버 가동!")

    # 4. 리액트 UI 실행
    npm_cmd = "npm.cmd" if is_windows else "npm"
    ui = subprocess.Popen([npm_cmd, "run", "dev"], cwd=os.path.join(script_dir, "berry-react"), shell=is_windows)
    print(f"🎨 3. 리액트 UI 가동! ({npm_cmd} 사용)")

    print("\n" + "="*50)
    print("🚀 모든 시스템이 준비되었습니다!")
    print("🔗 접속 주소: http://localhost:5173")
    print("="*50 + "\n")

    try:
        while True:
            time.sleep(2)
            if engine.poll() is not None:
                print("❌ 엔진이 시작부터 죽어버렸어!")
                break
            if api.poll() is not None:
                print("❌ API 서버가 죽어버렸어!")
                break
            if ui.poll() is not None:
                print("❌ UI가 멈췄어!")
                break

    except KeyboardInterrupt:
        print("\n👋 안녕! 종료할게.")
    finally:
        engine.terminate()
        api.terminate()
        ui.terminate()
        print("✅ 안전하게 종료 완료!")

if __name__ == "__main__":
    run_berry_pro()
