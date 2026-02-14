from flask import Flask, render_template, Response, jsonify, request
from camera_manager import camera_manager
import advisor

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')
@app.route('/live_feed')
def live_feed():
    return render_template('live_feed.html')
@app.route('/faults')
def faults():
    return render_template('faults.html')
@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(camera_manager),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stats')
def get_stats():
    return jsonify({
        "stats": camera_manager.stats,
        "status": camera_manager.robot_status,
        "detected": camera_manager.detected_object,
        "battery": round(camera_manager.battery_level, 1)
    })

@app.route('/api/toggle')
def toggle_status():
    status = camera_manager.toggle_status()
    return jsonify({"status": status})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    # Trigger analysis of the currently seen object
    advice = camera_manager.analyze_object()
    return jsonify({"advice": advice})

@app.route('/api/chat', methods=['POST'])
def chat():

    data = request.get_json()
    message = data.get("message", "")

    try:
        response = advisor.get_advice(message)
    except Exception as e:
        response = str(e)

    return jsonify({"response": response})

@app.route('/api/faults')
def get_faults():
    faults = camera_manager.get_faults()
    return jsonify(faults)

@app.route('/api/analytics')
def get_analytics():
    return jsonify({
        "stats": camera_manager.stats,
        "history": camera_manager.hourly_history
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
