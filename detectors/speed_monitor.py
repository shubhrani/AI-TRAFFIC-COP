# detectors/speed_monitor.py
import cv2
import numpy as np
from ultralytics import YOLO
import os

# Configuration
model_path = "../yolov8n.pt"  # adjust if your path differs
video_path = r"C:\Users\shubh\Downloads\istockphoto-1336889543-640_adpp_is.mp4"

alpha = 0.2
pixel_to_km_per_h = 0.49742994528271
tracker_cfg = "bytetrack.yaml"

# Load model
model = YOLO(model_path)

def xywh_center(xywh):
    x, y, w, h = xywh
    return (float(x), float(y))

def generate_frames():
    """
    Generator that yields MJPEG frames (multipart/x-mixed-replace) for streaming via Flask.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        # generate a single frame describing the error then stop
        blank = 255 * np.ones((480, 640, 3), dtype=np.uint8)
        cv2.putText(blank, "ERROR: Could not open video", (20, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
        _, buffer = cv2.imencode('.jpg', blank)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps is None or fps <= 0:
        fps = 30.0
    dt = 1.0 / fps

    # Optional output video (keeps a copy of annotated output)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    output_path = os.path.splitext(video_path)[0] + "_annotated.mp4"
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    prev_centers = {}
    speed_ema = {}

    names = None

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            results = model.track(frame, persist=True, tracker=tracker_cfg, verbose=False)
            annotated = frame.copy()

            if results and len(results) > 0:
                res = results[0]
                boxes = res.boxes

                if boxes is not None and len(boxes) > 0:
                    ids = boxes.id
                    clss = boxes.cls
                    xywhs = boxes.xywh
                    xyxys = boxes.xyxy

                    ids_np = ids.cpu().numpy().astype(int) if ids is not None else None
                    # model.model may hold names depending on ultralytics version
                    try:
                        names = model.model.names
                    except Exception:
                        names = {}

                    n = len(boxes)
                    for i in range(n):
                        cls_idx = int(clss[i].cpu().numpy())
                        class_name = names.get(cls_idx, str(cls_idx))
                        if class_name != "car":
                            continue

                        if ids_np is None:
                            continue
                        track_id = int(ids_np[i])

                        center = xywh_center(xywhs[i].cpu().numpy().tolist())

                        inst_kmph = None
                        if track_id in prev_centers:
                            pixel_dist = np.linalg.norm(np.array(center) - np.array(prev_centers[track_id]))
                            px_per_s = pixel_dist / dt
                            inst_kmph = px_per_s * pixel_to_km_per_h

                            if track_id not in speed_ema:
                                speed_ema[track_id] = inst_kmph
                            else:
                                speed_ema[track_id] = alpha * inst_kmph + (1 - alpha) * speed_ema[track_id]

                        prev_centers[track_id] = center

                        if inst_kmph is not None:
                            x1, y1, x2, y2 = xyxys[i].cpu().numpy().astype(int).tolist()
                            speed_value = speed_ema.get(track_id, inst_kmph)
                            text = f"{speed_value:.1f} km/h"
                            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(
                                annotated, text, (x1, max(0, y1 - 10)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA
                            )

            # write optional annotated video
            out.write(annotated)

            # encode frame as jpg
            annotated_small = annotated  # you can resize if you want lower bandwidth
            ret, buffer = cv2.imencode('.jpg', annotated_small)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    finally:
        cap.release()
        out.release()
