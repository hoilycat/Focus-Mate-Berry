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

    print(f"[Berry] {current_os} 환경에서 베리 프로 가동 시작!")

    # 1. 파이썬 인터프리터 설정 (.venv가 있으면 우선 사용)
    if is_windows:
        venv_python = os.path.join(script_dir, ".venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join(script_dir, ".venv", "bin", "python")

    if os.path.exists(venv_python):
        python_cmd = venv_python
        print(f"[*] 가상 환경(.venv)을 감지했습니다: {python_cmd}")
    else:
        python_cmd = sys.executable
        print(f"[!] 가상 환경을 찾지 못해 시스템 파이썬을 사용합니다: {python_cmd}")

    # 환경 변수에 UTF-8 설정 추가
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    # 2. 베리 엔진 실행 (절대경로로 실행)
    engine = subprocess.Popen([python_cmd, os.path.join(script_dir, "main.py")], shell=is_windows, env=env)
    print("[Engine] 1. 베리 엔진 가동!")

    # 3. 백엔드 API
    api = subprocess.Popen([python_cmd, os.path.join(script_dir, "backend_api.py")], shell=is_windows, env=env)
    print("[API] 2. API 서버 가동!")

    # 4. 리액트 UI 실행
    npm_cmd = "npm.cmd" if is_windows else "npm"
    ui = subprocess.Popen([npm_cmd, "run", "dev"], cwd=os.path.join(script_dir, "berry-react"), shell=is_windows, env=env)
    print(f"[UI] 3. 리액트 UI 가동! ({npm_cmd} 사용)")

    print("\n" + "="*50)
    print("READY: 모든 시스템이 준비되었습니다!")
    print("URL: http://localhost:5173")
    print("="*50 + "\n")

    try:
        while True:
            time.sleep(2)
            if engine.poll() is not None:
                print("[!] 엔진이 죽어버렸어!")
                break
            if api.poll() is not None:
                print("[!] API 서버가 죽어버렸어!")
                break
            if ui.poll() is not None:
                print("[!] UI가 멈췄어!")
                break

    except KeyboardInterrupt:
        print("\n[Exit] 안녕! 종료할게.")
    finally:
        engine.terminate()
        api.terminate()
        ui.terminate()
        print("[Done] 안전하게 종료 완료!")

if __name__ == "__main__":
    run_berry_pro()
