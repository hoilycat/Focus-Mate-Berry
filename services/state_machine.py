#state_machine.py

import datetime

class BerryStateMachine:
    def __init__(self):
        self.current_state = "GROWTH" # 기본 상태
        self.strikes = 0
        self.exp = 0
        self.absence_count = 0 # 🆕 자리에 없는 횟수 카운트
        
    def update(self, is_seated, is_turtle, spy_status):
        
        # 1. 스파이(PC 감시)가 보낸 신호가 최우선!
        if spy_status == 'EATING':
            self.current_state = "EATING" 
            self.absence_count = 0 # 딴짓 중이면 확실히 있는 거니까 리셋
            return self.current_state
            
        elif spy_status == 'SICK':
            self.current_state = "SICK"
            self.absence_count = 0
            return self.current_state
            
        elif spy_status == 'DOOM':
            self.current_state = "DOOM"
            self.absence_count = 0
            return self.current_state

        # 2. 자리 비움 체크 (여기가 바뀜! ✨)
        if not is_seated:
            self.absence_count += 1 # "어? 안 보이네?" 카운트 증가
            
            # 5번 연속(약 10초) 안 보이면 그때 잠듦
            if self.absence_count > 5:
                self.current_state = "SLEEP"
                return self.current_state
            else:
                # 아직 5번 안 됐으면, 방금 전 상태 유지 (잠들지 마!)
                # (만약 이전이 SLEEP이었다면 깨우지 않음)
                if self.current_state != "SLEEP":
                    return self.current_state
        else:
            # 사람이 보이면 바로 카운트 초기화!
            self.absence_count = 0

        # 3. 거북목 체크 (사람이 있을 때만)
        if is_turtle:
            # self.current_state = "WARNING"  <-- 이제 여기서 상태를 바꾸지 않음 (성장 단계 유지)
            self.strikes += 1
            if self.strikes >= 30: 
                self.current_state = "SLEEP"
                self.strikes = 0
        else:
            # 아주 훌륭함
            self.current_state = "GROWTH"
            self.exp += 1
            if self.strikes > 0:
                self.strikes -= 1 
            
        return self.current_state
    
    def reset(self):
        self.current_state = "GROWTH" # 다시 처음 상태로 돌아가기!
    
    
    def forgive(self):
        if self.current_state in ["SLEEP", "DOOM"]:
            self.current_state = "GROWTH"
            self.strikes = 0 
            self.absence_count = 0 # 용서받으면 부재중 카운트도 리셋
            return True
        else:
            return False