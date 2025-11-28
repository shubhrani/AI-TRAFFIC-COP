# app.py
from flask import Flask, render_template, Response, redirect, url_for
import importlib
from datetime import datetime

current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
app = Flask(__name__, static_folder='static', template_folder='templates')

# Helper to import a generator by name. If module not found, returns None.
def get_generator(module_name):
    try:
        mod = importlib.import_module(f"detectors.{module_name}")
        gen = getattr(mod, "generate_frames", None)
        if gen is None:
            return None
        return gen
    except Exception as e:
        print(f"Error importing detectors.{module_name}: {e}")
        return None

@app.route('/')
def landing():
    # default landing page, no stream active
    return render_template('landing.html', active_module=None)

@app.route('/run/<module>')
def run_module(module):
    """
    Render landing page but with a stream embedded for the requested module.
    Valid module values: 'helmet_detection', 'red_light', 'speed_monitor'
    """
    allowed = ['helmet_detection', 'red_light', 'speed_monitor']
    if module not in allowed:
        return redirect(url_for('landing'))
    return render_template('landing.html', active_module=module)

@app.route('/dashboard')
def dashboard():
    # hardcoded violation data (example)
    violations = [
        {"id": 1, "type": "Red Light Violation", "count": 2, "last": f"{current_time}"},
        {"id": 2, "type": "No Helmet", "count": 7, "last":  f"{current_time}"},
        {"id": 3, "type": "Over_Speeding", "count": 2, "last":  f"{current_time}"},
    ]
    return render_template('dashboard.html', violations=violations)

@app.route('/video_feed/<module>')
def video_feed(module):
    """
    Return a streaming response using the appropriate generator.
    module: 'helmet_detection' | 'red_light' | 'speed_monitor'
    """
    gen = get_generator(module)
    if gen is None:
        # return a small error stream: one-frame MJPEG with error message
        def error_frame():
            import cv2, numpy as np
            blank = 255 * np.ones((360, 640, 3), dtype=np.uint8)
            cv2.putText(blank, "Stream not available", (20, 180),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2, cv2.LINE_AA)
            ret, buffer = cv2.imencode('.jpg', blank)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        return Response(error_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

    # If generator exists, return streaming response
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/index')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # set host to 0.0.0.0 if you want external access on your LAN
    app.run(host='0.0.0.0', port=5000, debug=True)
