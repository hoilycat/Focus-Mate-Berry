import cv2
import platform
import mediapipe as mp

class BerryVision:
    def __init__(self):
        self.cap = None
        self.face_mesh = None
        
        # 시각화 도구
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        try:
            mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            print("✅ 베리 시력 강화 완료 (맥/윈도우 공용)")
        except Exception as e:
            print(f"❌ 엔진 초기화 실패: {e}")
        
        self._init_camera()

    def _init_camera(self):
        try:
            if self.cap: 
                self.cap.release()
            
            system_name = platform.system()
            if system_name == "Windows":
                # 윈도우는 DirectShow가 빨라요
                self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            elif system_name == "Darwin": # Darwin이 바로 '맥(macOS)'의 본명이야!
                # 맥은 AVFOUNDATION을 쓰거나 기본값(0)을 써요
                self.cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
            else:
                self.cap = cv2.VideoCapture(0)
            
            # 카메라 해상도 설정 (맥에서는 가끔 안 먹힐 수 있지만 기본으로 설정!)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            if not self.cap.isOpened():
                print("⚠️ 카메라를 찾을 수 없어요. 권한 설정을 확인해 주세요!")
        except Exception as e:
            print(f"카메라 초기화 오류: {e}")

    def check_status(self):
        default_val = (False, False, 0.5, "Center",0.5) # 앉아있음, 거북목 아님, 정면, 중앙, 정면
        
        try:
            if not self.cap or not self.cap.isOpened():
                self._init_camera()
                return default_val

            # 버퍼 비우기 (최신 화면 가져오기)
            for _ in range(2):
                self.cap.grab() # read()보다 grab()이 조금 더 가벼워!
            
            success, frame = self.cap.read()
            if not success or frame is None:
                return default_val

            # 맥에서는 화면이 반전되어 보일 수 있어서 필요하면 좌우 반전을 해줘
            # frame = cv2.flip(frame, 1) 

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)

            is_seated = False
            head_yaw = 0.5
            gaze = "Center"
            is_turtle = False

            if results.multi_face_landmarks:
                is_seated = True
                landmarks = results.multi_face_landmarks[0].landmark
                
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=results.multi_face_landmarks[0],
                    connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
                )

                # 주요 랜드마크 좌표
                nose_y = landmarks[1].y      # 코 끝
                top_y = landmarks[10].y      # 이마 끝
                bottom_y = landmarks[152].y  # 턱 끝
                
                # 상하 각도 계산 (0.5 근처면 정면, 커지면 숙인 것!)
                head_pitch = (nose_y - top_y) / (bottom_y - top_y + 1e-6)

                # 좌우 각도 및 시선 계산
                nose = landmarks[1].x
                l_ear = landmarks[234].x
                r_ear = landmarks[454].x
                
                head_yaw = (nose - l_ear) / (r_ear - l_ear + 1e-6)
                
                l_eye_outer = landmarks[33].x
                l_eye_inner = landmarks[133].x
                iris = landmarks[468].x
                eye_width = l_eye_inner - l_eye_outer
                gaze_ratio = (iris - l_eye_outer) / (eye_width + 1e-6)

                if gaze_ratio < 0.30: gaze = "Looking Right"
                elif gaze_ratio > 0.70: gaze = "Looking Left"

                # 2024-04-24 업데이트: 눈썹 위치 기반 거북목 감지
                # 눈썹 중앙(Landmark 105, 334)의 Y좌표가 화면 중간(0.5)보다 아래로 내려가면 거북목으로 판정
                eyebrow_y = (landmarks[105].y + landmarks[334].y) / 2
                is_turtle = eyebrow_y > 0.5

            # 디버그 창
            cv2.putText(frame, f"Seated: {is_seated} | Gaze: {gaze}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Berry Debug", frame)
            
            # 맥에서는 waitKey(1)이 창을 유지하는 데 아주 중요함
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return default_val

            return (is_seated, is_turtle, head_yaw, gaze, head_pitch) if is_seated else default_val

        except Exception as e:
            print(f"Vision Error: {e}")
            return default_val

    def stop(self): # __del__ 보다는 명시적인 stop 함수가 맥에서 더 안전해!
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1) # 맥에서 창을 완전히 닫기 위한 꿀팁!