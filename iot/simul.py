import paho.mqtt.client as mqtt
import json
import time
import random

# Configuration du broker MQTT
broker = "192.168.6.13"
port = 1883
topic = "pmr_parking/locations"

# Fonction de connexion
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

client = mqtt.Client()
client.on_connect = on_connect
client.connect(broker, port, 60)
client.loop_start()

places = ["A"]*40

for i in range (40):
    places[i] += str(i)


center_lat, center_lon = 43.6045, 1.444

while True:
    place = random.choice(places)
    lat = center_lat + random.uniform(-0.02, 0.02)
    lon = center_lon + random.uniform(-0.02, 0.02)
    payload = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "place_id": place,
        "latitude": lat,
        "longitude": lon }
       
    client.publish(topic, json.dumps(payload))
    print(f"Published: {payload}")
    
    time.sleep(1)  

client.loop_stop()
