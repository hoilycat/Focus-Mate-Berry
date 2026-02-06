from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
import datetime

app = FastAPI()

# 💡 리액트(5173포트)가 이 서버(8000포트)에 접속할 수 있도록 허용 (CORS 설정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "berry_log_final.db"

# --- [도우미 함수] ---
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 결과를 딕셔너리 형태로 받기 위함
    return conn

# --- [API 엔드포인트] ---

# 1. 현재 상태 가져오기 (리액트가 1초마다 물어볼 창구)
@app.get("/api/status")
def get_status():
    conn = get_db_connection()
    try:
        # 최신 로그 가져오기
        log = conn.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 1").fetchone()
        if log:
            return dict(log)
        return {"status": "OFFLINE", "message": "데이터가 없습니다."}
    finally:
        conn.close()

# 2. 리모컨 명령 보내기 (리액트 버튼 클릭 시 호출)
@app.post("/api/command")
def send_command(cmd_data: dict):
    cmd = cmd_data.get("cmd")
    if not cmd: return {"success": False}
    
    conn = get_db_connection()
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("INSERT INTO commands (cmd, created_at) VALUES (?, ?)", (cmd, now))
        conn.commit()
        return {"success": True}
    finally:
        conn.close()

# 3. 명예의 전당 가져오기
@app.get("/api/achievements")
def get_achievements():
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT * FROM achievements ORDER BY id DESC LIMIT 10").fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)