from flask import Flask, render_template, Response, jsonify, request
from camera_manager import camera_manager
import advisor

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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
        "detected": camera_manager.detected_object
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
