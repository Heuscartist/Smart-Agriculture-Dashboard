from flask import Flask, jsonify
import random
import time

app = Flask(__name__)

@app.route('/')
def simulate_sensor_data():
    sensor_data = {
        "temperature": round(random.uniform(20.0, 35.0), 2),
        "humidity": round(random.uniform(40.0, 70.0), 2),
        "soil_moisture": round(random.uniform(30.0, 80.0), 2),
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }
    return jsonify(sensor_data)

if __name__ == "__main__":
    # Change port=80 if you want it to look exactly like an ESP32 server
    app.run(host='0.0.0.0', port=5000, debug=False)
