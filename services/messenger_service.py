import requests
import json
import time
import os

class BerryMessenger:
    def __init__(self):
        # 👇 용용이의 앱 키들 (설정 완료!)
        self.API_KEY = os.getenv("KAKAO_API_KEY")
        self.CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
        
        # 토큰 파일 이름
        self.TOKEN_FILE = "kakao_token.json"
        
        self.ACCESS_TOKEN = ""
        self.load_token() # 시작하자마자 파일에서 토큰 로딩!

    def load_token(self):
        """파일에서 토큰을 읽어오는 함수"""
        try:
            with open(self.TOKEN_FILE, "r") as f:
                tokens = json.load(f)
                self.ACCESS_TOKEN = tokens.get("access_token")
        except Exception as e:
            print(f"❌ 토큰 파일 읽기 실패: {e}")

    def update_token(self):
        """토큰이 만료되면 '리프레시 토큰'으로 새거 받아오는 함수"""
        print("🔄 토큰이 만료된 것 같아! 새 토큰을 받아올게...")
        
        try:
            # 파일에서 리프레시 토큰 꺼내기
            with open(self.TOKEN_FILE, "r") as f:
                tokens = json.load(f)
            
            refresh_token = tokens.get("refresh_token")
            
            if not refresh_token:
                print("❌ 리프레시 토큰이 없어! 다시 로그인해야 해.")
                return False

            # 카카오에게 "새 토큰 주세요!" 요청
            url = "https://kauth.kakao.com/oauth/token"
            data = {
                "grant_type": "refresh_token",
                "client_id": self.API_KEY,
                "client_secret": self.CLIENT_SECRET,
                "refresh_token": refresh_token
            }
            
            response = requests.post(url, data=data)
            new_tokens = response.json()

            # 성공했으면 파일 덮어쓰기 (저장)
            if "access_token" in new_tokens:
                self.ACCESS_TOKEN = new_tokens["access_token"]
                
                # 리프레시 토큰이 갱신될 수도 있고 아닐 수도 있음 (있는 것만 합치기)
                if "refresh_token" in new_tokens:
                    tokens["refresh_token"] = new_tokens["refresh_token"]
                tokens["access_token"] = new_tokens["access_token"]
                
                with open(self.TOKEN_FILE, "w") as fp:
                    json.dump(tokens, fp)
                    
                print("✅ 토큰 갱신 성공! (파일 저장 완료)")
                return True
            else:
                print(f"❌ 토큰 갱신 실패: {new_tokens}")
                return False
                
        except Exception as e:
            print(f"❌ 토큰 갱신 중 에러: {e}")
            return False

    def send_report(self, user_name, bad_app):
        """카톡 보내기 (실패하면 알아서 갱신 후 재시도)"""
        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        
        # 1차 시도
        res = self._send_request(url, user_name, bad_app)
        
        # 만약 토큰 만료(-401) 에러가 나면?
        if res.get('code') == -401:
            # 토큰 갱신 시도!
            if self.update_token():
                # 갱신 성공하면 2차 시도 (재전송)
                res = self._send_request(url, user_name, bad_app)
            else:
                return False, "토큰 갱신 실패"
        
        if res.get('result_code') == 0:
            return True, "전송 성공"
        else:
            return False, f"전송 실패 ({res})"

    def _send_request(self, url, user_name, bad_app):
        """실제 전송 요청을 날리는 내부 함수"""
        headers = {"Authorization": "Bearer " + self.ACCESS_TOKEN}
        
        template = {
            "object_type": "text",
            "text": f"🚨 [베리 긴급 신고]\n\n{user_name}(이)가 '{bad_app}' 켜놓고 딴짓 중이에요!\n아파서 쓰러졌는데도 안 살려줘요... 😭",
            "link": {
                "web_url": "https://www.google.com",
                "mobile_web_url": "https://www.google.com"
            },
            "button_title": "혼내러 가기"
        }
        
        data = {"template_object": json.dumps(template)}
        
        try:
            return requests.post(url, headers=headers, data=data).json()
        except Exception as e:
            return {'code': -999, 'msg': str(e)}

    # 예비용 함수
    def send_to_me(self, user_name, bad_app):
        return self.send_report(user_name, bad_app)