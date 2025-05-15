from flask import Flask, request, jsonify
from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime
import sys
import os

# Add parent directory to path to allow importing logger module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import logger

app = Flask(__name__)

# InfluxDB setup
bucket = "esp32_data"
token = "1h0JhallhRUnV9uJXQuGS7anVF-fBtmLJEV99F0wDEDtRe0gTGc0qAqaHv360czgg60w7pod4h2DiJ7PaXv-oA=="
org = "LUMS"
url = "http://localhost:8086"

logger.info("Initializing InfluxDB client connection")
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api()

@app.route('/send-data', methods=['POST'])
def receive_data():
    try:
        data = request.json
        logger.info(f"Received data: {data}")
        
        point = (
            Point("sensor_data")
            .tag("device", "esp32")
            .field("temperature", data["temperature"])
            .field("humidity", data["humidity"])
            .field("soil_moisture", data["soil_moisture"])
            .time(datetime.utcnow(), WritePrecision.NS)
        )
        write_api.write(bucket=bucket, org=org, record=point)
        logger.info("Data successfully written to InfluxDB")
        return jsonify({"status": "success", "message": "Data written to InfluxDB"}), 200
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Flask server on port 5000")
    app.run(host='0.0.0.0', port=5000)
