from collections import defaultdict
import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO('../yolov8n.pt')
video_path = r"C:\Users\shubh\PycharmProjects\Main_Project\pythonProject1\Computer Vision and Image Processing\RLVD_Project\Red Light.mp4"

def generate_frames():
    cap = cv2.VideoCapture(video_path)
    track_history = defaultdict(lambda: [])
    last_y = {}
    frame_count = 0

    while cap.isOpened():
        success, frame = cap.read()
        frame_count += 1
        if not success:
            break

        results = model.track(frame, persist=True)
        boxes = results[0].boxes.xywh.cpu()
        track_ids = results[0].boxes.id.int().cpu().tolist()
        classes = results[0].boxes.cls.int().cpu().tolist()

        annotated_frame = results[0].plot()
        roi = frame[20:35, 350:400]
        pixel_values = roi[:, :, :]
        sum_r = np.sum(pixel_values[:, :, 2])
        sum_g = np.sum(pixel_values[:, :, 1])
        sum_b = np.sum(pixel_values[:, :, 0])

        if sum_b < sum_r and sum_r > sum_g:
            traffic_light = "Red Light"
        elif sum_g > sum_b and sum_g > sum_r:
            traffic_light = "Green Light"
        else:
            traffic_light = "Yellow Light"

        for box, track_id, cls in zip(boxes, track_ids, classes):
            x, y, w, h = box
            track = track_history[track_id]
            track.append((float(x), float(y)))
            if len(track) > 20:
                track.pop(0)
            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=2)
            cv2.line(annotated_frame, (345, 242), (616, 232), (0, 255, 0), 2)

            if traffic_light == "Red Light" and (cls == 2 or cls == 5):
                prev_y = last_y.get(track_id, None)
                if prev_y is not None:
                    if prev_y > 369 and y < 369:
                        filename = f"violation_frame_{frame_count}.jpg"
                        cv2.imwrite(filename, frame)
                        print(f"[VIOLATION] Vehicle {track_id} crossed line at y=369 → Frame saved: {filename}")
                last_y[track_id] = y

        cv2.rectangle(annotated_frame, (10, 10), (350, 80), (0, 0, 0), -1)
        cv2.putText(annotated_frame, f"Traffic Light: {traffic_light}", (20, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255) if traffic_light == "Yellow Light"
                    else (0, 255, 0) if traffic_light == "Green Light" else (0, 0, 255), 2)

        annotated_frame = cv2.resize(annotated_frame, (1220, 720))

        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()
