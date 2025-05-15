import streamlit as st
from influxdb_client import InfluxDBClient
from streamlit_autorefresh import st_autorefresh

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image

import numpy as np
import pandas as pd
import os
import sys

# Add parent directory to path to allow importing logger module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import logger
from fetch_image import fetch_and_overwrite_image

logger.info("Starting ESP32 Dashboard application")

# Constants
MODEL_PATH = "model/plant_classifier.pth"
IMAGE_PATH = "data/latest.jpg"
IMAGE_SIZE = (240, 240)

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5] * 3, [0.5] * 3)
])

# Streamlit config
st.set_page_config(page_title="ESP32 Dashboard", layout="wide")
st_autorefresh(interval=10 * 1000, key="refresh")

# Load model once
@st.cache_resource
def load_model():
    logger.info(f"Loading model from {MODEL_PATH}")
    try:
        device = torch.device("cpu")
        model = models.resnet18(pretrained=False)
        model.fc = nn.Linear(model.fc.in_features, 2)
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        model.eval()
        logger.info("Model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

try:
    model = load_model()
except Exception as e:
    st.error(f"Failed to load model: {e}")
    logger.critical(f"Failed to load model: {e}")
    model = None

st.title("🌡️ ESP32 Real-Time Sensor Dashboard")

# InfluxDB setup
token = "YOUR TOKEN HERE"
org = "YOUR ORG HERE"
url = "http://localhost:8086"
bucket = "esp32_data"

logger.info("Connecting to InfluxDB")
try:
    client = InfluxDBClient(url=url, token=token, org=org)
    logger.info("InfluxDB connection established")
except Exception as e:
    st.error(f"Failed to connect to InfluxDB: {e}")
    logger.critical(f"Failed to connect to InfluxDB: {e}")
    client = None

time_options = {
    "Last 5 Minutes": "-5m",
    "Last 10 Minutes": "-10m",
    "Last 30 Minutes": "-30m",
    "Last Hour": "-1h",
}
selected_time_range = st.selectbox("Select Time Range", list(time_options.keys()))
query_range = time_options[selected_time_range]
logger.info(f"Time range selected: {selected_time_range} ({query_range})")

query = f'''
from(bucket: "{bucket}")
|> range(start: {query_range})
|> filter(fn: (r) => r["_measurement"] == "sensor_data")
|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
|> keep(columns: ["_time", "temperature", "humidity", "soil_moisture"])
'''

try:
    logger.info("Executing InfluxDB query")
    result = client.query_api().query_data_frame(org=org, query=query)
    logger.info(f"Query returned {len(result)} records")
except Exception as e:
    st.error(f"Failed to query InfluxDB: {e}")
    logger.error(f"Failed to query InfluxDB: {e}")
    result = pd.DataFrame()

col1, col2 = st.columns(2)

with col2:
    if not result.empty:
        result["_time"] = pd.to_datetime(result["_time"])
        result.set_index("_time", inplace=True)

        # Get the latest row
        latest_row = result.iloc[-1]
        logger.info(f"Latest readings: Temperature={latest_row['temperature']:.2f}°C, "
                   f"Humidity={latest_row['humidity']:.2f}%, "
                   f"Soil Moisture={latest_row['soil_moisture']:.2f}")

        # --- Data Validation Checks ---
        alerts = []

        if not (0 <= latest_row["temperature"] <= 50):
            alert_msg = f"Temperature out of range: {latest_row['temperature']:.2f} °C"
            alerts.append(f"🌡️ {alert_msg}")
            logger.warning(alert_msg)
            
        if not (0 <= latest_row["humidity"] <= 100):
            alert_msg = f"Humidity out of range: {latest_row['humidity']:.2f} %"
            alerts.append(f"💧 {alert_msg}")
            logger.warning(alert_msg)
            
        if not (0 <= latest_row["soil_moisture"] <= 100):
            alert_msg = f"Soil Moisture out of range: {latest_row['soil_moisture']:.2f}"
            alerts.append(f"🌿 {alert_msg}")
            logger.warning(alert_msg)

        if alerts:
            for alert in alerts:
                st.error(f"⚠️ {alert}")

        def moisture_status(value):
            if value < 30:
                return "Dry"
            elif value < 60:
                return "Optimal"
            else:
                return "Wet"

        moisture = moisture_status(latest_row["soil_moisture"])
        logger.info(f"Moisture status: {moisture}")

        st.subheader("📊 Current Readings")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("🌡️ Temperature", f"{latest_row['temperature']:.2f} °C")
        m_col2.metric("💧 Humidity", f"{latest_row['humidity']:.2f} %")
        m_col3.metric("🌿 Soil Moisture", f"{latest_row['soil_moisture']:.2f}")
        m_col4.markdown(f"### 🧪 Moisture Status: **{moisture}**")

        st.subheader("📈 Raw Sensor Data")
        st.line_chart(result[["temperature", "humidity", "soil_moisture"]])

    else:
        logger.warning("No data available for the selected time range")
        st.warning("⚠️ No data available for the selected time range.")

with col1:
    st.markdown(
        """
        <style>
        [data-testid="column"]:nth-child(2) {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Fetch the latest image
    logger.info("Fetching latest plant image")
    fetch_and_overwrite_image(filename="latest.jpg")

    # Show and predict image
    st.subheader("🌿 Plant Health Prediction")

    try:
        logger.info(f"Opening image from {IMAGE_PATH}")
        image = Image.open(IMAGE_PATH).convert("RGB")
        st.image(image, caption="Latest Plant Image", width=300)

        # Preprocess image
        input_tensor = transform(image).unsqueeze(0)

        # Make prediction
        if model is not None:
            logger.info("Making prediction on plant image")
            with torch.no_grad():
                outputs = model(input_tensor)
                probs = torch.softmax(outputs, dim=1)
                predicted_class = torch.argmax(probs, dim=1).item()
                confidence = probs[0, predicted_class].item()

            label = "Healthy 🌱" if predicted_class == 0 else "Unhealthy 🥀"
            logger.info(f"Prediction: {label} with confidence {confidence:.2f}")

            st.markdown(f"### 🧠 Prediction: **{label}**")
            st.markdown(f"Confidence: {confidence:.2f}")
        else:
            logger.error("Cannot make prediction: model not loaded")
            st.error("Cannot make prediction: model not loaded")

    except Exception as e:
        logger.error(f"Failed to display or predict: {e}")
        st.error(f"Failed to display or predict: {e}")

# Rolling mean + min/max
st.subheader("📉 30-second Rolling Mean with Static Min/Max")

if not result.empty:
    temp_min = result["temperature"].min()
    temp_max = result["temperature"].max()
    hum_min = result["humidity"].min()
    hum_max = result["humidity"].max()
    soil_min = result["soil_moisture"].min()
    soil_max = result["soil_moisture"].max()
    
    logger.info(f"Temperature min/max: {temp_min:.2f}/{temp_max:.2f}°C")
    logger.info(f"Humidity min/max: {hum_min:.2f}/{hum_max:.2f}%")
    logger.info(f"Soil moisture min/max: {soil_min:.2f}/{soil_max:.2f}")

    col_temp, col_hum, col_soil = st.columns(3)
    col_temp.markdown(f"🌡️ **Temperature:** Min: {temp_min:.2f} °C, Max: {temp_max:.2f} °C")
    col_hum.markdown(f"💧 **Humidity:** Min: {hum_min:.2f} %, Max: {hum_max:.2f} %")
    col_soil.markdown(f"🌿 **Soil Moisture:** Min: {soil_min:.2f}, Max: {soil_max:.2f}")

    rolling_mean = result[["temperature", "humidity", "soil_moisture"]].rolling('30S').mean()
    st.line_chart(rolling_mean)

logger.info("Dashboard rendering complete")
