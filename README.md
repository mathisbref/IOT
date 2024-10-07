# Projet IOT : Localisation des places de parking PMR libres dans la ville de Toulouse

## Auteurs
- **Brefuel Mathis**
- **Al Masri Marwan**
- **Espinasse Paul**

---

## 1. Présentation du projet

Ce projet vise à simuler l’installation d’un dispositif capable de détecter la présence d’un véhicule sur une place de stationnement réservée aux personnes à mobilité réduite (PMR). Cela permettra de connaître en temps réel les places PMR libres dans la ville de Toulouse, facilitant ainsi la mobilité des personnes concernées.

Le projet est situé sur un site en MarkDown affichant la carte qui montre en temps réel les places PMR disponible.

### 1.1 Compétences à acquérir

- **Spécifications et conception**
    - Concevoir une architecture d'infrastructure IoT
    - Choisir un protocole adapté
    - Standardiser le format des données
- **Développement**
    - Récupération de flux de données sur une page web
    - Création d'un simulateur de flux en Python
    - Développement d'une application IoT en JavaScript
- **Mise en œuvre**
    - Installation et configuration d'un broker MQTT
    - Installation et configuration d'un serveur web
    - Installation et configuration de services IoT (InfluxDB, Grafana, Node-RED)
- **Tests et validation**
    - Tester les limites de charge de l'infrastructure
    - Déterminer des actions pour améliorer la scalabilité
    - Prendre en compte la cybersécurité

### 1.2 Livrables attendus

- Un compte-rendu de projet détaillant la démarche de conception et de mise en œuvre de la solution
- Une VM Debian avec le projet fonctionnel

### 1.3 Technologies utilisées

- **Portail Open Data de Toulouse Métropole** : [Lien](https://data.toulouse-metropole.fr/explore/?sort=modified)
- **MQTT Explorer**
- **Visual Studio Code** pour le développement

---

## 2. Mise en place

### 2.1 Prérequis

1. Mkdocs :
```
sudo apt-get update
```
```
sudo apt install mkdocs mkdocs-material mkdocs-material-extensions
```
2. Broker MQTT
```
sudo apt-get install mosquitto
```
Modifier la configuration du broker :
```
sudo nano /etc/mosquitto/mosquitto.conf
```
Rajouter:
```
allow_anonymous true
listener 1883
listener 9001
protocol websockets
persistence true
```
```
sudo systemctl restart mosquitto
```

### 2.2 Installation du projet

1. Cloner le dépôt GitHub :  
   `git clone https://github.com/mathisbref/IOT.git`
2. Se placer dans le dossier du projet :  
   `cd IOT/iot`
3. Installer la librairie **paho-mqtt** :  
   `sudo apt install python3-paho-mqtt`
4. Lancer le simulateur Python :  
   `python3 simul.py`
5. Dans un autre temrinal se rendre dans le dossier **PMR-project** et lancer MkDocs :  
   `mkdocs serve`

### 2.3 Explication du script Python

#### Bibliothèques utilisées
- **paho.mqtt.client** : Communication via le protocole MQTT
- **json** : Manipulation des données en JSON
- **time** : Manipulation des horodatages et gestion des pauses
- **random** : Génération de valeurs aléatoires pour les mises à jour de disponibilité

#### Explication du code

1. **Configuration du Broker MQTT**
    ```python
    broker = "localhost"
    port = 1883
    topic_places = "pmr_parking/places"  # Sujet pour l'envoi des emplacements initiaux
    topic_updates = "pmr_parking/updates"  # Sujet pour l'envoi des mises à jour de disponibilité
    ```
    - `broker` définit l'adresse du serveur MQTT.
    - `topic_places` et `topic_updates` sont les topics utilisés pour envoyer respectivement les emplacements des places PMR et les mises à jour de disponibilité.

2. **Connexion au Broker MQTT**
    ```python
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(broker, port, 60)
    client.loop_start()
    ```
    - Création du client MQTT et connexion au broker. La fonction `on_connect` est appelée pour indiquer le succès de la connexion.
    - `client.loop_start()` démarre une boucle qui maintient la connexion au broker.

3. **Chargement des données des places PMR depuis un fichier JSON**
    ```python
    with open('pmr.json') as f:
        places = json.load(f)
    ```
    - Le fichier `pmr.json` est chargé, contenant les informations des places PMR, notamment les coordonnées GPS et l'identifiant unique.

4. **Initialisation des données des places PMR**
    ```python
    places_data = {}
    for place in places:
        if place["no"] is not None:  # Vérifie si l'identifiant est non nul
            lat = place["geo_point_2d"]["lat"]
            lon = place["geo_point_2d"]["lon"]
            availability = True  # Disponibilité initiale à True pour toutes les places
            places_data[place["no"]] = {
                "latitude": lat,
                "longitude": lon,
                "availability": availability
            }
    ```
    - Un dictionnaire `places_data` est créé, contenant les informations des places, telles que leur latitude, longitude et disponibilité.

5. **Conversion du dictionnaire en liste**
    ```python
    places_data = [{'id': id, **info} for id, info in places_data.items()]
    ```
    - Le dictionnaire `places_data` est converti en une liste de dictionnaires, où chaque élément contient un identifiant, la latitude, la longitude et l'état de disponibilité.

6. **Envoi initial des informations des places PMR**
    ```python
    payload_places = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "places": places_data[:100]  # Envoi des 100 premières places
    }
    client.publish(topic_places, json.dumps(payload_places))
    print(f"Published initial places: {payload_places}")
    ```
    - Les informations des 100 premières places PMR sont envoyées au topic `pmr_parking/places`, avec un horodatage.

7. **Mise à jour de la disponibilité des places PMR**
    ```python
    while True:
        for _ in range(min(20, len(places_data[:100]))):
            place = random.choice(places_data[:100])
            place["availability"] = random.choice([True, False])

            payload_update = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "place_id": place["id"],
                "availability": place["availability"],
                "latitude": place["latitude"],
                "longitude": place["longitude"]
            }
            client.publish(topic_updates, json.dumps(payload_update))
            print(f"Published update: {payload_update}")
    ```
    - À chaque itération, la disponibilité de 20 places parmi les 100 premières est mise à jour aléatoirement. Ces informations sont ensuite publiées sur le topic `pmr_parking/updates`.

8. **Ré-envoi périodique des emplacements**
    ```python
    if current_time - last_send_time >= 30:
        payload_places = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "places": places_data[:100]  # Ré-envoi des 100 premières places
        }
        client.publish(topic_places, json.dumps(payload_places))
        print(f"Published initial places again: {payload_places}")
        last_send_time = current_time
    ```
    - Toutes les 30 secondes, les 100 premières places PMR sont ré-envoyées pour maintenir les données à jour.

9. **Pause entre les mises à jour**
    ```python
    time.sleep(5)
    ```
    - Le script fait une pause de 5 secondes entre chaque cycle de mise à jour.


