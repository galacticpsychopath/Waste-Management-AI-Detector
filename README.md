# Waste‑Management‑AI‑Detector

A Python‑based AI system that detects and classifies waste in images/video using deep learning (YOLOv8), and provides a web interface for real‑time waste detection and visualization.

## 📌 Overview

Waste‑Management‑AI‑Detector is a smart waste detection application that uses computer vision and machine learning to identify waste objects in video or images and help automate smart waste management workflows. The project includes a web interface where users can stream camera input and see real‑time detections.

## 🚀 Features

- 🧠 **AI‑Powered Waste Detection** – Uses a pretrained YOLOv8 model to detect waste in live camera feed or static images.
- 📹 **Real‑Time Video Processing** – Processes video streams from webcams or video files.
- 🌐 **Web Interface** – Built with Flask (Python) to serve the detection UI.
- 📊 **Visualization** – Shows bounding boxes and labels for detected waste in real time.
- 🛠️ **Modular Structure** – Key modules for camera management and detection logic: `camera_manager.py`, `main.py`, `advisor.py`.

## 📁 Project Structure

📦Waste‑Management‑AI‑Detector
┣ 📁 static # CSS/JS/images for UI
┣ 📁 templates # HTML views for Flask
┣ ├ advisor.py # (Optional) logic assistant or helper
┣ ├ app.py # Flask application entry point
┣ ├ camera_manager.py # Camera/video source handling
┣ ├ main.py # Detection pipeline + model runner
┣ ├ yolov8n.pt # Trained YOLOv8 model weights
┣ ┗ requirements.txt # Python dependencies


## 🛠️ Tech Stack

| Tool / Library | Purpose |
|----------------|---------|
| **Python**     | Core language for backend logic |
| **Flask**      | Web application framework |
| **Ultralytics YOLOv8** | Object detection model |
| **OpenCV**     | Image/video processing |
| **HTML/CSS/JS**| Frontend UI for detection display |

## 💡 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/galacticpsychopath/Waste-Management-AI-Detector.git
   cd Waste-Management-AI-Detector
Create a virtual environment

python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
Install dependencies

pip install -r requirements.txt
▶️ Running the App
Make sure your webcam is connected (or update video source in camera_manager.py).

Launch the web app:

python app.py
Open your browser and navigate to:

http://localhost:5000
🧠 Model Details
This project uses a YOLOv8 model (yolov8n.pt) for object detection, trained (or fine‑tuned) to recognize waste items. You can replace this with your own trained weights for more accurate detection against your dataset.

🖼 Example Output
Screenshots can be added here showing the detection UI and bounding boxes around waste items.

🧪 Tests
You can test the system with sample images or video files by modifying the source input in camera_manager.py and observing detection results on the web interface.

🚀 Future Improvements
📦 Support for more waste classes (e.g., recyclable vs non‑recyclable)

📊 Dashboard with analytics (counts, waste type distribution)

📱 Mobile UI / dashboard

⚡ Speed and performance optimizations

🧠 Retrain model with custom dataset

📄 License
This project is open source — feel free to adapt and improve it!
