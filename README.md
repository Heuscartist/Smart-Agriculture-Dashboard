# 🌿 Smart Agriculture Dashboard using ESP32, InfluxDB & Streamlit

This project is a real-time IoT data engineering pipeline designed to monitor and visualize environmental conditions in agriculture. It uses an ESP32 for sensing temperature, humidity, and soil moisture, and an ESP32-CAM for capturing plant images. The data is stored in **InfluxDB** and visualized on a **Streamlit dashboard**. A PyTorch-based deep learning model classifies plant health using captured images.

---

## 🚀 Features

- 📡 **Real-time sensor data** (Temperature, Humidity, Soil Moisture)
    
- 📷 **ESP32-CAM** captures plant images
    
- 🧠 **Plant Health Prediction** using a fine-tuned ResNet18 model (PyTorch)
    
- 📈 Live **graphing & rolling average** of sensor data
    
- 🗃️ **InfluxDB integration** for time-series data storage
    
- 🔁 **Auto-refreshing dashboard** every 10 seconds
    
- 🌐 Flask-based API to simulate or relay ESP32 data
    

---

## 🛠️ Tech Stack

- ESP32 / ESP32-CAM (C++)
    
- Python: `streamlit`, `influxdb-client`, `torch`, `torchvision`, `PIL`, `requests`, `pandas`, `numpy`, `Flask`
    
- InfluxDB (Time-series database)
    
- PyTorch (for plant health classification)
    
- Streamlit (Dashboard visualization)
    
- Flask (Sensor simulator/API)
    

---

## 📦 Project Structure

```bash
.
├── app.py                     # Streamlit Dashboard
├── fetch_image.py            # ESP32-CAM image capture fetcher
├── sensor_simulator.py       # Flask server to simulate ESP32 data
├── influx_writer.py          # Python script to poll ESP32 and write to InfluxDB
├── model/
│   └── plant_classifier.pth  # Trained PyTorch model
├── data/
│   └── latest.jpg            # Latest image fetched from ESP32-CAM
├── esp_firmware/
│   ├── camera                # ESP32-CAM firmware
│   └── sensor                # ESP32 sensor firmware
└── README.md
```

---

## ⚙️ How It Works

1. **ESP32** gathers temperature, humidity, and soil moisture data.
    
2. A **Flask API** simulates or receives this data and provides it via HTTP.
    
3. A **Python writer script** pulls data every 5 seconds and writes to **InfluxDB**.
    
4. The **ESP32-CAM** streams plant images which are fetched and saved via HTTP.
    
5. A **PyTorch model** processes the latest image and classifies plant health.
    
6. **Streamlit** dashboard displays sensor metrics, charts, and prediction.
    

---

## 🖼️ Plant Health Model

- **Model**: ResNet18 (Modified FC layer for binary classification)
    
- **Classes**: Healthy (🌱), Unhealthy (🥀)
    
- **Input**: 224x224 RGB image
    
- **Confidence Score** shown in UI
    

---

## 📊 Dashboard Demo

- 📍 Metrics: Temperature (°C), Humidity (%), Soil Moisture
    
- ⏱️ Auto-refresh every 10 seconds
    
- 📷 Shows the latest image from ESP32-CAM
    
- 📈 30-second rolling average graph
    
- 🧠 Deep learning-based plant health prediction
    

---

## 🔧 Setup Instructions

There are 2 ways you can run this:
1. Using the sensor simulation file if you dont have the hardware
2. Using the ESP32 and ESP32 CAM Module if you have hardware

### 1. Download Repo and Install Requirements

First download the code from this repository by first going into directory where you would like to download the repo and running the following command:
```bash
git clone <repo-url>
```

Then create a virtual environment for this project. You can do that by using conda
```bash
conda create --name plant_monitor-venv python=3.9
conda activate plant_monitor-venv
```

Once you have activated your venv you can install the requirements by:
``` bash
pip install -r requirements.txt
```

### 2. Setup InfluxDB
Set up **influxdb** which is the database being used for this project. You can follow [this](https://www.youtube.com/watch?v=zk8NYfWAp2A&ab_channel=IOTStation) guide to set it up.
Create a **bucket** named 'esp32_data' and make sure to note your **token** and **org**. Modify the influx_writer.py and app.py file with your bucket, token and org.
### 3. Run Sensor Simulator (if you dont have hardware)

``` bash
python sensor_simulator.py
```

### 3. Start InfluxDB Writer
Make sure InfluxDB is running locally on port 8086.

```bash
python influx_writer.py
```

### 4. Launch the Dashboard
```bash
streamlit run app.py
```

---

## 📡 Hardware Setup (if available)

- **ESP32 Sensor Node**
    
    - DHT11 for temperature/humidity
        
    - Soil moisture sensor
        
- **ESP32-CAM**
    
    - Captures plant images
        
    - Serves image via HTTP server
        

Ensure both boards are connected to Wi-Fi and flashed with respective `.ino` files. Once running, go to arduino serial monitor and check the ip address at which the esp are connected. You will need to modify your code accordingly.

---

## 📸 Screenshots

| Dashboard View                                            |
| --------------------------------------------------------- |
| ![[WhatsApp Image 2025-04-21 at 15.25.48_14b528e6 1.jpg]] |

---

## 🤝 Acknowledgments

Special thanks to the open-source community and resources from [PyTorch](https://pytorch.org/), [InfluxData](https://www.influxdata.com/), and [Streamlit](https://streamlit.io/).
