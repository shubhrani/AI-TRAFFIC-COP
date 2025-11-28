import time
from ultralytics import YOLO
import cv2

model_path = r"C:\Users\shubh\Downloads\virtual_env\runs\detect\train3\weights\best.pt"
model = YOLO(model_path)
video_source = r"C:\Users\shubh\Videos\vlc-record-2024-07-03-11h28m25s-rtsp___172.11.20.16_554-.mp4"

def generate_frames():
    cap = cv2.VideoCapture(video_source)
    class_names = model.names

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(source=frame, conf=0.5, verbose=False)
        annotated_frame = results[0].plot()

        helmet_count = 0
        no_helmet_count = 0

        for box in results[0].boxes:
            cls_id = int(box.cls)
            cls_name = class_names[cls_id].lower()

            if "helmet" in cls_name and "no" not in cls_name:
                helmet_count += 1
                time.sleep(0.1)
            elif "no" in cls_name and "helmet" in cls_name:
                no_helmet_count += 1
                time.sleep(0.1)

        cv2.rectangle(annotated_frame, (10, 10), (310, 90), (0, 0, 0), -1)
        cv2.putText(annotated_frame, f"Helmet: {helmet_count}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(annotated_frame, f"No Helmet: {no_helmet_count}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        annotated_frame = cv2.resize(annotated_frame, (1220, 720))

        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()
