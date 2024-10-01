import paho.mqtt.client as mqtt
import json
import time
import random

# Configuration du broker MQTT
broker = "localhost"  # Adresse IP du broker
port = 1883  # Port MQTT par défaut
topic_places = "pmr_parking/places"  # Sujet pour l'envoi des emplacements initiaux
topic_updates = "pmr_parking/updates"  # Sujet pour l'envoi des mises à jour de disponibilité

# Fonction de connexion
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

client = mqtt.Client()
client.on_connect = on_connect
client.connect(broker, port, 60)
client.loop_start()

# Chargement des données à partir du fichier JSON
with open('pmr.json') as f:
    places = json.load(f)

# Utilisation d'un dictionnaire pour éviter les doublons d'ID
places_data = {}
for place in places:
    if place["no"] is not None:  # Vérifiez que l'identifiant n'est pas None
        lat = place["geo_point_2d"]["lat"]
        lon = place["geo_point_2d"]["lon"]
        availability = True  # Supposons que toutes les places soient disponibles au départ
        places_data[place["no"]] = {  # Utiliser l'ID comme clé pour garantir l'unicité
            "latitude": lat,
            "longitude": lon,
            "availability": availability
        }

# Convertir le dictionnaire en liste
places_data = [{'id': id, **info} for id, info in places_data.items()]

# Étape 1: Envoyer les emplacements fixes de toutes les places d'un coup
payload_places = {
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "places": places_data[:100]  # Liste des 100 premières places
}
client.publish(topic_places, json.dumps(payload_places))
print(f"Published initial places: {payload_places}")

# Compteur de temps pour envoyer les emplacements toutes les 30 secondes
last_send_time = time.time()

# Boucle pour mettre à jour la disponibilité des places
while True:
    # Mise à jour de la disponibilité pour 20 places parmi les 100 premières
    for _ in range(min(20, len(places_data[:100]))):  # Met à jour jusqu'à 20 places parmi les 100 premières
        place = random.choice(places_data[:100])  # Choisir une place parmi les 100 premières
        place["availability"] = random.choice([True, False])

        payload_update = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "place_id": place["id"],
            "availability": place["availability"],
            "latitude": place["latitude"],  # Ajouter latitude
            "longitude": place["longitude"]  # Ajouter longitude
        }

        client.publish(topic_updates, json.dumps(payload_update))
        print(f"Published update: {payload_update}")

    # Vérifier si 30 secondes se sont écoulées pour envoyer les 100 premières places à nouveau
    current_time = time.time()
    if current_time - last_send_time >= 30:
        payload_places = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "places": places_data[:100]  # Ré-envoyer uniquement les 100 premières places
        }
        client.publish(topic_places, json.dumps(payload_places))
        print(f"Published initial places again: {payload_places}")
        last_send_time = current_time  # Réinitialiser le temps

    time.sleep(5)  # Pause de 5 secondes entre chaque mise à jour
