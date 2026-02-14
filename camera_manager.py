import cv2
from ultralytics import YOLO
import threading
import time
import numpy as np
import advisor

class CameraManager:
    def __init__(self):
        # --- Camera Setup ---
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                print("Warning: Camera not found.")
                self.active = False
            else:
                self.active = True
        except Exception as e:
            print(f"Error opening camera: {e}")
            self.active = False

        # --- AI Model ---
        print("Loading YOLO model...")
        try:
            self.model = YOLO('yolov8n.pt')
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

        # --- Robot State ---
        self.battery_level = 100.0
        self.last_battery_check = time.time()
        self.robot_status = "Active"
        self.detected_object = None
        
        # --- Stats Counters ---
        self.stats = {
            "Plastic": 0, 
            "Metal": 0, 
            "Organic": 0, 
            "Paper": 0, 
            "Glass": 0
        }
        
        self.hourly_history = [0] * 24
        self.last_count_time = 0
        
        # --- Mapping YOLO classes to our Categories ---
        # COCO classes: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco.yaml
        self.category_map = {
            'bottle': 'Plastic',
            'cup': 'Plastic',
            'can': 'Metal',
            'banana': 'Organic',
            'apple': 'Organic',
            'orange': 'Organic',
            'broccoli': 'Organic',
            'carrot': 'Organic',
            'sandwich': 'Organic',
            'book': 'Paper',
            'vase': 'Glass'
        }

    def update_battery(self):
        """
        Updates the battery level. 
        switches between Simulation and Real Hardware modes.
        """
        # --- HARDWARE INTEGRATION POINT ---
        # If you have a real robot class, e.g., self.robot_hardware
        # Uncomment the following block:
        """
        try:
            if hasattr(self, 'robot_hardware'):
                 self.battery_level = self.robot_hardware.get_battery_percentage()
        except Exception as e:
            print(f"Hardware Battery Error: {e}")
        """
        
        # --- SIMULATION MODE ---
        # Decrease battery slowly to simulate usage
        current_time = time.time()
        if current_time - self.last_battery_check > 5: # Update every 5 seconds
            self.battery_level = max(0, self.battery_level - 0.1) # Drain 0.1% every 5s
            self.last_battery_check = current_time

    def get_frame(self):
        self.update_battery()

        if not self.active:
            frame = np.zeros((480, 640, 3), np.uint8)
            cv2.putText(frame, "SYSTEM STANDBY", (160, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
        else:
            success, frame = self.camera.read()
            if not success:
                frame = np.zeros((480, 640, 3), np.uint8)
                cv2.putText(frame, "CAMERA ERROR", (180, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                if self.model:
                    # Run Inference
                    results = self.model(frame, verbose=False)
                    frame = results[0].plot()
                    
                    # Process Detections
                    boxes = results[0].boxes
                    if len(boxes) > 0:
                        # Get the Class ID of the first detected object
                        cls_id = int(boxes[0].cls[0])
                        obj_name = self.model.names[cls_id]
                        self.detected_object = obj_name
                        
                        # --- STATS UPDATE LOGIC ---
                        # Map object to category
                        category = self.category_map.get(obj_name)
                        if category:
                            # Auto-increment every 2 seconds if object is persistent
                            current_time = time.time()
                            if current_time - self.last_count_time > 2.0:
                                self.stats[category] += 1
                                self.last_count_time = current_time
                                
                                # Update History
                                if hasattr(self, 'hourly_history'):
                                    h = time.localtime().tm_hour
                                    self.hourly_history[h] += 1 
                    else:
                        self.detected_object = None

        # --- Visual Target Overlay ---
        if self.active:
            h, w = frame.shape[:2]
            cx, cy = w // 2, h // 2
            # Draw Aiming Box
            cv2.rectangle(frame, (cx - 50, cy - 50), (cx + 50, cy + 50), (0, 255, 0), 2)
            # Draw Crosshair
            cv2.line(frame, (cx - 10, cy), (cx + 10, cy), (0, 255, 0), 1)
            cv2.line(frame, (cx, cy - 10), (cx, cy + 10), (0, 255, 0), 1)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes() if ret else None

    def analyze_object(self):
        """
        Called when user clicks 'Snap & Analyze' or manually requests analysis.
        """
        if not self.detected_object:
            return "No object detected to analyze."
            
        obj_name = self.detected_object
        
        # Update Stats
        category = self.category_map.get(obj_name, "Trash") # Default to Trash if unknown
        if category in self.stats:
            self.stats[category] += 1
            
            # Record History (Simulated for this session)
            current_hour = time.localtime().tm_hour
            # Initialize if empty
            if not hasattr(self, 'hourly_history'):
                 self.hourly_history = [0] * 24 
            
            self.hourly_history[current_hour] += 1

        # Get AI Advice
        advice_text = advisor.get_advice(obj_name)
        return advice_text

    def get_faults(self):
        """
        Checks for system faults.
        Returns a list of dictionaries describing active faults.
        """
        faults = []
        
        # 1. Camera Fault
        if not self.camera.isOpened() or not self.active:
             # If active but camera closed, it's a fault
             if self.active and not self.camera.isOpened():
                 faults.append({
                     "component": "Main Camera",
                     "issue": "Camera Connection Lost",
                     "severity": "Critical",
                     "timestamp": time.strftime("%Y-%m-%d %H:%M")
                 })
        
        # 2. Battery Faults
        if self.battery_level < 20:
             severity = "Critical" if self.battery_level < 5 else "Warning"
             faults.append({
                 "component": "Battery Unit",
                 "issue": "Low Battery Voltage",
                 "severity": severity,
                 "timestamp": time.strftime("%Y-%m-%d %H:%M")
             })

        # 3. Simulated Motor Fault (For demonstration)
        # Randomly trigger if battery is odd number just to show dynamic behavior
        if int(self.battery_level) % 10 == 7: 
             faults.append({
                 "component": "Right Wheel Motor",
                 "issue": "High Temperature Warning",
                 "severity": "Warning",
                 "timestamp": time.strftime("%Y-%m-%d %H:%M")
             })
             
        return faults


    def toggle_status(self):
        self.active = not self.active
        self.robot_status = "Active" if self.active else "Standby"
        return self.robot_status

camera_manager = CameraManager()
