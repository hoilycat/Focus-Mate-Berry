import cv2
import mediapipe as mp
import time

def main():
    print("🚀 동영상 및 AI 테스트 시작...")

    # 1. AI(MediaPipe) 준비
    try:
        mp_face_mesh = mp.solutions.face_mesh
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        
        # 여기서 에러가 나면 아까처럼 이상한 글자가 쏟아질 수 있음
        face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        print("✅ AI 로딩 성공!")
    except Exception as e:
        print(f"❌ AI 로딩 실패 (재설치 필요): {e}")
        return

    # 2. 카메라 켜기
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # 윈도우용
    if not cap.isOpened():
        cap = cv2.VideoCapture(0) # 맥/리눅스용

    if not cap.isOpened():
        print("❌ 카메라를 열 수 없습니다.")
        return

    print("🎥 화면이 나옵니다. 얼굴을 비춰보세요! (종료: q 키)")

    while True:
        success, frame = cap.read()
        if not success:
            print("비디오 프레임 읽기 실패")
            break

        # AI 인식을 위해 색상 변경
        frame.flags.writeable = False
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)
        frame.flags.writeable = True

        # 얼굴 그리기
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
                )
                
            cv2.putText(frame, "AI DETECTED!", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No Face...", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # 화면 출력
        cv2.imshow('Final Test', frame)

        # q를 누르면 종료
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()