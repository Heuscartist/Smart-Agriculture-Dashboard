from flask import Flask, request, jsonify
from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime

app = Flask(__name__)

# InfluxDB setup
bucket = "esp32_data"
token = "YOUR_TOKEN"
org = "YOUR_ORG"
url = "http://localhost:8086"
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api()

@app.route('/send-data', methods=['POST'])
def receive_data():
    try:
        data = request.json
        point = (
            Point("sensor_data")
            .tag("device", "esp32")
            .field("temperature", data["temperature"])
            .field("humidity", data["humidity"])
            .field("soil_moisture", data["soil_moisture"])
            .time(datetime.utcnow(), WritePrecision.NS)
        )
        write_api.write(bucket=bucket, org=org, record=point)
        return jsonify({"status": "success", "message": "Data written to InfluxDB"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
