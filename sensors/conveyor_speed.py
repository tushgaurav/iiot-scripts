import time
import random
import json
import math
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv

load_dotenv()

# ----------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------

BROKER_ADDRESS = "dev.infra.orangewood.co"
BROKER_PORT = 1883
TOPIC = "factory1/assembly_line_01/conveyor_01/conveyor_speed"

SEND_INTERVAL = 2

# "Mostly uniform" speed profile: stable base with tiny wobble + tiny jitter
BASE_SPEED_MPS = 1.50
WOBBLE_AMPLITUDE_MPS = 0.01  # slow periodic variation (very small)
WOBBLE_PERIOD_SEC = 30.0
JITTER_STD_MPS = 0.005  # small random noise

MIN_SPEED_MPS = 0.0
MAX_SPEED_MPS = 3.0

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

start_t = time.monotonic()

try:
    while True:
        t = time.monotonic() - start_t

        # Stable "uniform" speed with a tiny periodic wobble and tiny random jitter
        wobble = WOBBLE_AMPLITUDE_MPS * math.sin(2.0 * math.pi * (t / WOBBLE_PERIOD_SEC))
        jitter = random.gauss(0.0, JITTER_STD_MPS)
        speed_mps = BASE_SPEED_MPS + wobble + jitter

        # Keep it reasonable
        if speed_mps < MIN_SPEED_MPS:
            speed_mps = MIN_SPEED_MPS
        if speed_mps > MAX_SPEED_MPS:
            speed_mps = MAX_SPEED_MPS

        payload = {
            "sensor_id": "conveyor_speed_sensor_01",
            "value": round(speed_mps, 3),
            "unit": "mps",
            "status": "ok",
        }

        payload_json = json.dumps(payload)
        client.publish(TOPIC, payload_json, qos=1)
        print(f"Published to {TOPIC}: {payload_json}")

        time.sleep(SEND_INTERVAL)

except KeyboardInterrupt:
    print("\nStopping script...")
    client.loop_stop()
    client.disconnect()
    print("Disconnected.")

