import cv2
from ultralytics import YOLO
import advisor
import time

def main():
    print("Loading YOLOv8 model...")
    # Load a pretrained YOLOv8n model
    model = YOLO('yolov8n.pt') 

    print("Opening webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Starting EcoVision AI...")
    print("Controls:")
    print("  SPACE: Snap & Analyze (Get Advice)")
    print("  q: Quit")

    last_advice = ""
    advice_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Run inference
        results = model(frame, stream=True, verbose=False)
        
        # We need to parse results to draw them or get the best detection
        # YOLOv8's plot() method returns the frame with boxes drawn
        # But we also want to know WHAT was detected for the advice logic.
        
        detected_objects = []
        
        # Process results
        for r in results:
            # Visualize the results on the frame
            annotated_frame = r.plot()
            
            # Extract class names
            for box in r.boxes:
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                conf = float(box.conf[0])
                detected_objects.append((class_name, conf))
        
        # If plot() was called, use that frame, otherwise original
        # Note: r.plot() returns a new array, so we should display that.
        # Since 'results' is a generator with stream=True, we iterate it above.
        # But usually for webcam we just want the first result (one frame).
        # Let's simplify: run model without stream=True for single frame usage or just iterate.
        
        # Simpler approach for single frame:
        results = model(frame, verbose=False)
        annotated_frame = results[0].plot()
        
        # Get detected objects from the first result
        current_detections = []
        for box in results[0].boxes:
            cls = int(box.cls[0])
            name = model.names[cls]
            current_detections.append(name)

        # Overlay Advice if recent
        if time.time() - advice_time < 10: # Show advice for 10 seconds
            # Split text into lines for cv2
            y0, dy = 50, 30
            for i, line in enumerate(last_advice.split('\n')):
                y = y0 + i*dy
                # Draw black background for text
                cv2.putText(annotated_frame, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4)
                cv2.putText(annotated_frame, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow('EcoVision AI - YOLOv8', annotated_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '): # Spacebar
            if current_detections:
                # Pick the most prominent object (first one usually or largest)
                # For now, just pick the first one
                obj = current_detections[0]
                print(f"\n[!] Snapped: {obj}")
                print("Asking Advisor (Ollama)...")
                
                # Show "Thinking..." on UI next frame (simplified here by just blocking)
                advice = advisor.get_advice(obj)
                print("-" * 40)
                print(advice)
                print("-" * 40)
                
                last_advice = f"Item: {obj}\n" + advice
                advice_time = time.time()
            else:
                print("No object detected to analyze.")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
