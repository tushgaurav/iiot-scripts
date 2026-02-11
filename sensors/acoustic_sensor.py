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
TOPIC = "factory1/assembly_line_01/globals/acoustic_db"

SEND_INTERVAL = 2

# Mostly-uniform dB signal around -2.2 with very small variation
BASE_DB = -2.2
WOBBLE_AMPLITUDE_DB = 0.02  # tiny slow periodic variation
WOBBLE_PERIOD_SEC = 45.0
JITTER_STD_DB = 0.01  # tiny random noise

MIN_DB = -20.0
MAX_DB = 20.0

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

        wobble = WOBBLE_AMPLITUDE_DB * math.sin(2.0 * math.pi * (t / WOBBLE_PERIOD_SEC))
        jitter = random.gauss(0.0, JITTER_STD_DB)
        db_value = BASE_DB + wobble + jitter

        if db_value < MIN_DB:
            db_value = MIN_DB
        if db_value > MAX_DB:
            db_value = MAX_DB

        payload = {
            "sensor_id": "acoustic_sensor_01",
            "value": round(db_value, 2),
            "unit": "db",
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

