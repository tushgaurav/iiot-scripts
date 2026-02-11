import time
import random
import json
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv

load_dotenv()

# ----------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------

BROKER_ADDRESS = "dev.infra.orangewood.co" 
BROKER_PORT = 1883
TOPIC = "factory1/assembly_line_01/conveyor_01/motor_temperature"

SEND_INTERVAL = 2
BASE_TEMP = 25.0

# ----------------------------------------------------------------
# SETUP MQTT CLIENT
# ----------------------------------------------------------------

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT Broker: {BROKER_ADDRESS}")
    else:
        print(f"Failed to connect, return code {rc}")

client = mqtt.Client()
client.on_connect = on_connect
client.username_pw_set(os.getenv("BROKER_USERNAME"), os.getenv("BROKER_PASSWORD"))

print(f"Connecting to {BROKER_ADDRESS}...")
try:
    client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
except Exception as e:
    print(f"Connection failed: {e}")
    exit(1)

client.loop_start()

# ----------------------------------------------------------------
# MAIN LOOP (DATA GENERATION)
# ----------------------------------------------------------------

current_temp = BASE_TEMP

try:
    while True:
        # 1. Generate Dummy Data
        # Randomly change the temp by -0.5 to +0.5 degrees to make it look realistic
        change = random.uniform(-0.5, 0.5)
        current_temp += change
        
        # Keep it reasonable (e.g., between 20 and 80 degrees)
        if current_temp < 20: current_temp = 20
        if current_temp > 80: current_temp = 80

        # 2. Format the Payload (JSON is best for Telegraf)
        payload = {
            "sensor_id": "temp_sensor_01",
            "value": round(current_temp, 2),
            "unit": "celsius",
            "status": "ok"
        }
        
        # Convert dict to JSON string
        payload_json = json.dumps(payload)

        # 3. Publish to MQTT
        # qos=1 means "at least once delivery" (good for sensors)
        client.publish(TOPIC, payload_json, qos=1)
        
        print(f"Published to {TOPIC}: {payload_json}")

        # 4. Wait before next reading
        time.sleep(SEND_INTERVAL)

except KeyboardInterrupt:
    print("\nStopping script...")
    client.loop_stop()
    client.disconnect()
    print("Disconnected.")