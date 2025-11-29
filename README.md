# 🛑🚦 AI TRAFFIC COP

### A Smart AI-Powered Traffic Management System using Python, OpenCV & YOLOv8

AI TRAFFIC COP is an intelligent, automated traffic monitoring system designed to assist traffic authorities by detecting and reporting real-time traffic violations.  
It integrates **three AI models**—Speed Monitoring, Helmet Detection, and Red-Light Violation—powered by **YOLOv8**, **OpenCV**, and a **visual dashboard** built using **HTML/CSS/JS**.

---

## 📁 Project Structure


---AI-TRAFFIC-COP
│
├── detectors/            
│
├── static/                 
│
├── templates/             
│   ├── dashboard.html
│   ├── index.html
│   └── landing.html
│
├── app.py               
├── requirements.txt      
├── README.md          
└── yolov8n.pt              


## 🚀 Features

### 🔴 1. Red Light Violation Detection
- Detects vehicles crossing the stop line during a red signal  
- Reads signal state and marks violators  
- Logs violation frames for evidence

### 🏍️ 2. Helmet Detection System
- Identifies motorcycle riders  
- Detects whether the rider is wearing a helmet  
- Marks non-helmet riders with bounding boxes and warnings

### ⚡ 3. Speed Monitoring
- Tracks vehicle movement using object tracking  
- Calculates real-time speed  
- Flags speed-limit violators automatically

### 📊 4. Real-Time Monitoring Dashboard
- Built with **HTML, CSS & JavaScript**  
- Displays live AI outputs  
- Shows analytics:
  - Speed stats  
  - Helmet violation count  
  - Red signal violation data  

---

## 🛠️ Tech Stack

### Backend & AI
- Python  
- OpenCV  
- Ultralytics YOLOv8  
- NumPy  
- Flask (or FastAPI based on your app.py)

### Frontend
- HTML5  
- CSS3  
- JavaScript  

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/AI-TRAFFIC-COP.git
cd AI-TRAFFIC-COP
