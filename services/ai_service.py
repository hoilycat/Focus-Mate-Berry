import os
import time
import random
# import google.generativeai as genai
from google import genai
from dotenv import load_dotenv
# .env 파일에서 환경 변수 로드
load_dotenv()

class BerryBrain:    
    def __init__(self, goal_minutes, user_name):
        # 🔑 키 설정
        self.API_KEY = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.API_KEY)
        # self.model = genai.Model("models/gemini-1.5-flash-latest") --- IGNORE ---

        # 🔍 모델 자동 선택!
        self.MODEL_ID = self._auto_pick_model()
        print(f"📌 선택된 모델: {self.MODEL_ID}")

        # 🎯 [목표 설정]
        self.GOAL_MINUTES = goal_minutes
        self.USER_NAME = user_name

        self.is_running = False  
        self.is_finished = False 
        self.milestones = []             
        self.nag_cooldown = 0 

        self.last_state = None
        self.last_message = f"베리 준비 완료! 목표는 {goal_minutes}분이야? {self.USER_NAME}(아)야 파이팅! 🐥💕"

        self.last_talk_time = 0
        self.LONG_COOLDOWN = 30
        
        self.accumulated_time = 0 
        self.history_time = 0    
        self.last_update_time = time.time()

        self.doom_grace_start = None      # 딴짓 시작 시간
        self.DOOM_GRACE_SECONDS = 30      # 딴짓 유예 시간 (테스트용)

        # 🍓 상황별 멘트 은행 (API 안 쓸 때 여기서 골라요)
        self.MESSAGE_BANK = {
            "GROWTH_SEED": ["와! 새 생명이 태어날 것 같아!", "두근두근.. 싹이 틀 준비 중이야!", f"{self.USER_NAME}(아)야, 나를 잘 키워줘! 🌱"],
            "GROWTH_SPROUT": ["나 좀 봐! 잎사귀가 돋았어!", "초록초록하지? 기분 좋아!", "무럭무럭 자라는 중이야! 🌿"],
            "GROWTH_SMALL": ["우와, 열매가 맺혔어!", "점점 달콤한 냄새가 나지 않아?", "조금만 더 힘내자! 🍓"],
            "EATING": ["냠냠! 이거 진짜 맛있다!", "유튜브 보면서 먹으니까 꿀맛이야!", "하나 더 먹어도 돼? 😋"],
            "SICK": ["윽.. 배가 살살 아파와..", "미안해.. 아까 너무 많이 먹었나 봐.. 🤢", f"{self.USER_NAME}(아)야.. 나 좀 도와줘.."],
            "SLEEP": [f"쿨쿨.. {self.USER_NAME}이 기다리다 잠들었어..", "음냐냐.. 공부 다 했어?.. 💤", "졸려어.."],
            "DOOM": ["🚑 너무 아파.. 응급실 가야 할 것 같아..", "미안해, 도저히 못 참아서 연락드렸어.. 😭"]
        }

    
    # ----------------------------------------------------
    # 🔎 모델 자동 고르기 함수 (에러 방지 핵심!!)
    # ----------------------------------------------------
    def _auto_pick_model(self):
        try:
            model_list = list(self.client.models.list())

            # 1) flash 최신 모델 먼저 찾기
            flash_models = [
                m.name for m in model_list if "flash" in m.name and "latest" in m.name
            ]
            if flash_models:
                return flash_models[0]

            # 2) flash 계열이라도 있으면 사용
            flash_any = [m.name for m in model_list if "flash" in m.name]
            if flash_any:
                return flash_any[0]

            # 3) flash가 없으면 pro 계열 최신
            pro_models = [
                m.name for m in model_list if "pro" in m.name and "latest" in m.name
            ]
            if pro_models:
                return pro_models[0]

            # 4) 그래도 없으면 pro 아무거나
            pro_any = [m.name for m in model_list if "pro" in m.name]
            if pro_any:
                return pro_any[0]

            # 5) 진짜 아무 것도 없으면 첫 모델
            return model_list[0].name

        except Exception as e:
            print(f"❌ 모델 자동 선택 실패: {e}")
            # 안전 대비: 기본 flash-latest 시도
            return "models/gemini-1.5-flash-latest"

     


    def update_user(self, new_name, new_goal):
    
        self.USER_NAME = new_name
        self.GOAL_MINUTES = new_goal
    
        self.last_message = f"오케이! {self.USER_NAME}(아)야, {self.GOAL_MINUTES}분 동안 열공해보자! 🔥"
        self.last_talk_time = time.time()
       
    def get_evolution_stage(self):
        progress_percent = (self.accumulated_time / (self.GOAL_MINUTES * 60)) * 100
        
        # 리액트의 이미지 전환 기준(19, 38, 57, 76%)과 똑같이 맞춥니다.
        if progress_percent < 19:   return "GROWTH_SEED"
        elif progress_percent < 38: return "GROWTH_SPROUT"
        elif progress_percent < 57: return "GROWTH_SMALL"
        elif progress_percent < 76: return "GROWTH_BIG"
        else:                       return "GROWTH_FAIRY"

    def think(self, current_state, detected_app=""):
        current_time = time.time()

        #--- 시간 경과 계산 ---
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        if delta_time > 5.0: 
            delta_time = 0

        detailed_state = self.get_evolution_stage()
        last_det = getattr(self, 'last_detailed_state', None)

        # 🚨 [핵심] 진화(SEED->SPROUT 등)는 '중요한 사건'으로 간주
        evolution_happened = (detailed_state != last_det)
        state_changed = (current_state != self.last_state)


        # --- 공부 시간 누적 ---
        if self.is_running and not self.is_finished and current_state == "GROWTH":
            
            self.accumulated_time += delta_time

        progress = min(self.accumulated_time / (self.GOAL_MINUTES * 60), 1.0)
        

        # --- 딴짓 유예시간 관리 ---
        if current_state in ["EATING", "SICK"]:
            # 딴짓 시작 시간 기록
            if self.doom_grace_start is None:
                self.doom_grace_start = time.time()
        else:
            # 다시 공부 상태 등으로 돌아오면 초기화
            self.doom_grace_start = None


        # --- 베리 말 스타일 ---
        concept_prompt = ""
        if current_state == "GROWTH":
            if detailed_state == "GROWTH_SEED":
                concept_prompt = f"씨앗 상태. '우와! 싹이 틀 것 같아! {self.USER_NAME}이가 열공해서 그래!'"
            elif detailed_state == "GROWTH_SPROUT":
                concept_prompt = "새싹 상태. '나 좀 봐! 잎사귀가 커졌어!'"
            elif detailed_state == "GROWTH_SMALL":
                concept_prompt = "작은 열매 상태. '열매가 맺혔어! 조금만 더!'"
            elif detailed_state == "GROWTH_BIG":
                concept_prompt = "큰 딸기 상태. '내 몸집이 이만큼 커졌어!'"
            else:
                concept_prompt = "최종 요정 베리! '역시 내 짝꿍 최고야!'"

            if progress >= 1.0 and not self.is_finished:
                self.is_finished = True
                return f"🎉 와아아!! {self.GOAL_MINUTES}분 성공!! {self.USER_NAME} 진짜 멋지다! 🥰"

        elif current_state == "EATING":
            concept_prompt = f"{detected_app}을 같이 보며 과자를 먹어서 행복함. '냠냠! 이거 진짜 맛있다!'"
        elif current_state == "SICK":
            concept_prompt = f"과자를 너무 먹어서 배가 아픔. {self.USER_NAME}에게 미안해하며 아픔을 호소함."
        elif current_state == "SLEEP":
            concept_prompt = f"{self.USER_NAME}을 기다리다 지쳐 잠이 오거나 심심해함."
        else:
            concept_prompt = "배가 너무 아파서 응급실에 가야 함. 미안해하며 부모님께 연락드린 슬픈 상황."

          # --- 멘트 결정 로직 ---
        if state_changed or evolution_happened or (current_time - self.last_talk_time >= self.LONG_COOLDOWN):
            
            # 💡 [하이브리드 전략] 
            # 1. 진화했거나, 목표 달성 등 '특별한 순간'에만 AI 호출 시도
            # 2. 평상시 상태 변화나 API 에러 시에는 '멘트 은행' 사용
            
            use_ai = evolution_happened or (current_state in ["SICK", "DOOM"]) # 중요할 때만 AI
            
            if use_ai:
                try:
                    # AI 호출 시도
                    full_prompt = f"상황: {current_state}. 애교 듬뿍 상냥한 한 마디."
                    response = self.client.models.generate_content(model=self.MODEL_ID, contents=full_prompt)
                    self.last_message = response.text.strip()
                    print("🤖 [AI 응답 성공]")
                except Exception as e:
                    # 429 에러 등이 나면 즉시 멘트 은행으로 전환
                    print(f"⚠️ AI 호출 제한(429 등) -> 멘트 은행 사용: {e}")
                    self.last_message = self._get_bank_message(current_state, detailed_state)
            else:
                # 평상시에는 멘트 은행에서 랜덤 추출 (API 사용량 0)
                self.last_message = self._get_bank_message(current_state, detailed_state)

            self.last_talk_time = current_time
            self.last_state = current_state
            self.last_detailed_state = detailed_state

        return self.last_message

    def _get_bank_message(self, state, stage):
        # 현재 상태에 맞는 멘트 리스트 가져오기
        key = stage if state == "GROWTH" else state
        messages = self.MESSAGE_BANK.get(key, ["응원할게! 파이팅!"])
        return random.choice(messages)