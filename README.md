# Projet IOT : Localisation des places de parking PMR libres dans la ville de Toulouse

## Auteurs
- **Brefuel Mathis**
- **Al Masri Marwan**
- **Espinasse Paul**

---

## 1. Présentation du projet

Ce projet vise à simuler l’installation d’un dispositif capable de détecter la présence d’un véhicule sur une place de stationnement réservée aux personnes à mobilité réduite (PMR). Cela permettra de connaître en temps réel les places PMR libres dans la ville de Toulouse, facilitant ainsi la mobilité des personnes concernées.

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
sudo systemctl start mosquitto
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
- **json** : Formatage des données en JSON
- **time** : Manipulation du temps pour horodatage et pauses
- **random** : Génération de valeurs aléatoires pour les positions géographiques

#### Explication du code

1. **Configuration du Broker MQTT**
    ```python
    broker = "localhost"
    port = 1883
    topic_places = "pmr_parking/places"  # Sujet pour l'envoi des emplacements initiaux
    topic_updates = "pmr_parking/updates"  # Sujet pour l'envoi des mises à jour de disponibilité
    ```

2. **Connexion au Broker MQTT**
    ```python
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(broker, port, 60)
    client.loop_start()
    ```

3. **Initialisation des places PMR**
    ```python
    places = ["A"] * 40
    for i in range(40):
        places[i] += str(i)
    ```

4. **Simulation des données des places PMR**
    ```python
    while True:
        lat = center_lat + random.uniform(-0.02, 0.02)
        lon = center_lon + random.uniform(-0.02, 0.02)
        payload = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "place_id": place, "latitude": lat, "longitude": lon}
        client.publish(topic, json.dumps(payload))
        time.sleep(1)
    ```

5. **Arrêt de la boucle**
    ```python
    client.loop_stop()
    ```

Ce script Python simule l’envoi de données de détection via MQTT, permettant de surveiller l’occupation des places PMR dans une ville.
