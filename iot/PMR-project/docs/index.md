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

        // Configuration du client MQTT pour les WebSockets
        const client = mqtt.connect('ws://localhost:9001'); // Assurez-vous que l'URL est correcte

        // Stocker les marqueurs des places
        const markers = {};

        // Créer des icônes personnalisées pour les marqueurs
        const greenIcon = L.icon({
            iconUrl: 'https://maps.gstatic.com/mapfiles/ms2/micons/green-dot.png',
            iconSize: [32, 32],
            iconAnchor: [16, 32],
            popupAnchor: [0, -32]
        });

        const redIcon = L.icon({
            iconUrl: 'https://maps.gstatic.com/mapfiles/ms2/micons/red-dot.png',
            iconSize: [32, 32],
            iconAnchor: [16, 32],
            popupAnchor: [0, -32]
        });

        client.on('connect', function () {
            console.log('Connected to MQTT broker');

            // Récupérer une seule fois les emplacements des places
            client.subscribe('pmr_parking/places');  // Topic pour les emplacements fixes
            // S'abonner également au sujet des mises à jour de disponibilité
            client.subscribe('pmr_parking/updates');  // Topic pour les mises à jour de disponibilité
        });

        // Gestion des messages MQTT
        client.on('message', function (topic, message) {
            const data = JSON.parse(message.toString());

            // Vérifier le sujet (emplacements fixes ou disponibilité)
            if (topic === 'pmr_parking/places') {
                // Topic pour les emplacements fixes
                const places = data.places; // Liste des emplacements des places
                places.forEach(place => {
                    const place_id = place.id;
                    const lat = place.latitude;
                    const lon = place.longitude;
                    const availability = place.availability; // Disponibilité initiale de la place

                    // Choisir l'icône en fonction de la disponibilité
                    const icon = availability ? greenIcon : redIcon;

                    // Créer un marqueur pour chaque place et l'ajouter à la carte
                    markers[place_id] = L.marker([lat, lon], { icon: icon })
                        .bindPopup(`Place ID: ${place_id}<br>Disponibilité: ${availability ? 'Disponible' : 'Occupé'}`)
                        .addTo(map);
                });
            } else if (topic === 'pmr_parking/updates') {
                // Topic pour les mises à jour de disponibilité et de position
                const place_id = data.place_id;
                const lat = data.latitude; // Nouvelle latitude
                const lon = data.longitude; // Nouvelle longitude
                const availability = data.availability; // Nouvelle disponibilité

                // Choisir l'icône en fonction de la disponibilité
                const icon = availability ? greenIcon : redIcon;

                // Si le marqueur existe déjà, on met à jour sa position, son icône et le popup
                if (markers[place_id]) {
                    markers[place_id].setLatLng([lat, lon]) // Mettre à jour les coordonnées
                        .setIcon(icon) // Mettre à jour l'icône
                        .setPopupContent(`Place ID: ${place_id}<br>Disponibilité: ${availability ? 'Disponible' : 'Occupé'}`);
                } else {
                    // Créer un nouveau marqueur si la place n'existe pas encore
                    markers[place_id] = L.marker([lat, lon], { icon: icon })
                        .bindPopup(`Place ID: ${place_id}<br>Disponibilité: ${availability ? 'Disponible' : 'Occupé'}`)
                        .addTo(map);
                }
            }
        });
    });
</script>




