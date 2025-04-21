from influxdb_client import InfluxDBClient, Point, WritePrecision
import requests
import time
from datetime import datetime

esp32_ip = "http://127.0.0.1:5000/"

bucket = "esp32_data"
token = "1h0JhallhRUnV9uJXQuGS7anVF-fBtmLJEV99F0wDEDtRe0gTGc0qAqaHv360czgg60w7pod4h2DiJ7PaXv-oA=="
org = "LUMS"
url = "http://localhost:8086"

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api()

while True:
    try:
        response = requests.get(esp32_ip)
        if response.status_code == 200:
            data = response.json()
            point = (
                Point("sensor_data")
                .tag("device", "esp32")
                .field("temperature", data["temperature"])
                .field("humidity", data["humidity"])
                .field("soil_moisture", data["soil_moisture"])
                .time(datetime.utcnow(), WritePrecision.NS)
            )
            write_api.write(bucket=bucket, org=org, record=point)
            print("Data written to InfluxDB")
        time.sleep(5)
    except Exception as e:
        print("Error:", e)
