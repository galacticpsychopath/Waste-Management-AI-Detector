import cv2
from ultralytics import YOLO
import threading
import time
import numpy as np
import advisor

class CameraManager:
    def __init__(self):
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                print("Warning: Camera not found, using dummy.")
                self.dummy = True
            else:
                self.dummy = False
        except Exception as e:
            print(f"Error opening camera: {e}")
            self.dummy = True
            
        print("Loading YOLO model...")
        self.model = YOLO('yolov8n.pt')
        self.lock = threading.Lock()
        self.active = True
        self.stats = {
            "items_found": 0,
            "recycled": 0,
            "toxic": 0
        }
        self.detected_object = None
        self.robot_status = "Active"

    def get_frame(self):
        if not self.active:
            frame = np.zeros((480, 640, 3), np.uint8)
            cv2.putText(frame, "STANDBY", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 100, 100), 3)
        else:
            if self.dummy:
                frame = np.zeros((480, 640, 3), np.uint8)
                cv2.putText(frame, "NO CAMERA", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                # Simulate detection for testing
                self.detected_object = "bottle"
            else:
                success, frame = self.camera.read()
                if not success:
                    frame = np.zeros((480, 640, 3), np.uint8)
                    cv2.putText(frame, "CAMERA ERROR", (180, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                else:
                    # Run Inference
                    results = self.model(frame, verbose=False)
                    frame = results[0].plot()
                    
                    # Update detection
                    boxes = results[0].boxes
                    if len(boxes) > 0:
                        cls = int(boxes[0].cls[0])
                        self.detected_object = self.model.names[cls]
                    else:
                        self.detected_object = None

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes() if ret else None

    def toggle_status(self):
        self.active = not self.active
        self.robot_status = "Active" if self.active else "Standby"
        return self.robot_status

    def analyze_object(self):
        if not self.detected_object:
            return "No object detected to analyze."
            
        obj = self.detected_object
        self.stats["items_found"] += 1
        
        # Get advice
        # Note: This is a synchronous call, might block if network is slow. 
        # For a simple app it's okay, but ideally should be async.
        advice = advisor.get_advice(obj)
        
        # Simple heuristic to update stats based on advice text
        # This relies on the prompt in advisor.py asking "Is it recyclable? (Yes/No)"
        clean_advice = advice.lower()
        if "yes" in clean_advice[:50]: # Look for yes in the beginning
            self.stats["recycled"] += 1
        else:
            self.stats["toxic"] += 1 # Counting non-recyclable as 'toxic/trash' for now
            
        return advice

camera_manager = CameraManager()
