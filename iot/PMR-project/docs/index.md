<link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
<script src="https://unpkg.com/mqtt/dist/mqtt.min.js"></script>

# Service PMR pour Toulouse

Bienvenue sur la documentation du **Service PMR** pour la commune de **Toulouse**.

Ce projet propose une carte interactive permettant de visualiser les places de stationnement PMR disponibles dans la commune. Le service permet de :
- Consulter les emplacements des places PMR.
- Voir en temps réel si les places sont libres ou occupées.


<h2>Carte interactive des places PMR</h2>

<!-- Conteneur pour la carte -->
<div id="map" style="width: 100%; height: 600px;"></div>

<!-- Script pour initialiser la carte Leaflet et gérer les marqueurs via MQTT -->
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Initialiser la carte Leaflet
        const map = L.map('map').setView([43.6045, 1.444], 14);

        // Ajouter une couche de carte (OpenStreetMap)
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        // Configuration du client MQTT
        const client = mqtt.connect('ws://192.168.6.13:9001'); // Assurez-vous que le port et l'URL sont corrects

        const markers = {};

        client.on('connect', function () {
            console.log('Connected to MQTT broker');
            client.subscribe('pmr_parking/locations');
        });

        client.on('message', function (topic, message) {
            const data = JSON.parse(message.toString());

            // Si le marqueur existe, mettez à jour sa position
            if (markers[data.place_id]) {
                markers[data.place_id].setLatLng([data.latitude, data.longitude])
                    .setPopupContent(`Place ID: ${data.place_id}`);
            } else {
                // Créez un nouveau marqueur si nécessaire
                markers[data.place_id] = L.marker([data.latitude, data.longitude])
                    .bindPopup(`Place ID: ${data.place_id}`)
                    .addTo(map);
            }
        });
    });
</script>

