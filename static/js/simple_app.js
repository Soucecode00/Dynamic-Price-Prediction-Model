// Global variables
let map;
let pickupMarker;
let dropoffMarker;
let directionsService;
let directionsRenderer;
let priceChart;
let recentPredictions = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    initializeChart();
    setupEventListeners();
    updateConnectionStatus();
    startPeriodicUpdates();
});

// Initialize Google Maps
function initializeMap() {
    // Default coordinates (New York City)
    const defaultCenter = { lat: 40.7128, lng: -74.0060 };
    
    // Create map
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        center: defaultCenter,
        styles: getMapStyles(),
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false
    });
    
    // Initialize directions service
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        suppressMarkers: true
    });
    directionsRenderer.setMap(map);
    
    // Initialize autocomplete for pickup location
    const pickupInput = document.getElementById('pickupLocation');
    const pickupAutocomplete = new google.maps.places.Autocomplete(pickupInput);
    
    // Initialize autocomplete for dropoff location
    const dropoffInput = document.getElementById('dropoffLocation');
    const dropoffAutocomplete = new google.maps.places.Autocomplete(dropoffInput);
    
    // Handle place selection
    pickupAutocomplete.addListener('place_changed', function() {
        const place = pickupAutocomplete.getPlace();
        if (place.geometry) {
            addPickupMarker(place.geometry.location);
            updateRoute();
        }
    });
    
    dropoffAutocomplete.addListener('place_changed', function() {
        const place = dropoffAutocomplete.getPlace();
        if (place.geometry) {
            addDropoffMarker(place.geometry.location);
            updateRoute();
        }
    });
}

// Add pickup marker
function addPickupMarker(position) {
    if (pickupMarker) {
        pickupMarker.setMap(null);
    }
    
    pickupMarker = new google.maps.Marker({
        position: position,
        map: map,
        icon: {
            url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" fill="#51cf66"/>
                    <circle cx="12" cy="12" r="4" fill="white"/>
                </svg>
            `),
            scaledSize: new google.maps.Size(24, 24),
            anchor: new google.maps.Point(12, 12)
        },
        title: 'Pickup Location'
    });
}

// Add dropoff marker
function addDropoffMarker(position) {
    if (dropoffMarker) {
        dropoffMarker.setMap(null);
    }
    
    dropoffMarker = new google.maps.Marker({
        position: position,
        map: map,
        icon: {
            url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" fill="#ff6b6b"/>
                    <circle cx="12" cy="12" r="4" fill="white"/>
                </svg>
            `),
            scaledSize: new google.maps.Size(24, 24),
            anchor: new google.maps.Point(12, 12)
        },
        title: 'Dropoff Location'
    });
}

// Update route between markers
function updateRoute() {
    if (!pickupMarker || !dropoffMarker) return;
    
    const request = {
        origin: pickupMarker.getPosition(),
        destination: dropoffMarker.getPosition(),
        travelMode: google.maps.TravelMode.DRIVING
    };
    
    directionsService.route(request, function(result, status) {
        if (status === 'OK') {
            directionsRenderer.setDirections(result);
        }
    });
}

// Initialize Chart.js
function initializeChart() {
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Predicted Price',
                data: [],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    display: false
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            elements: {
                point: {
                    radius: 0
                }
            }
        }
    });
}

// Setup event listeners
function setupEventListeners() {
    const predictBtn = document.getElementById('predictBtn');
    predictBtn.addEventListener('click', handlePrediction);
    
    // Enter key support for inputs
    document.getElementById('pickupLocation').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            document.getElementById('dropoffLocation').focus();
        }
    });
    
    document.getElementById('dropoffLocation').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handlePrediction();
        }
    });
}

// Handle prediction request
function handlePrediction() {
    const pickupInput = document.getElementById('pickupLocation');
    const dropoffInput = document.getElementById('dropoffLocation');
    
    if (!pickupInput.value || !dropoffInput.value) {
        showToast('Please enter both pickup and dropoff locations', 'error');
        return;
    }
    
    if (!pickupMarker || !dropoffMarker) {
        showToast('Please select valid locations on the map', 'error');
        return;
    }
    
    showLoading(true);
    
    // Get coordinates
    const pickupLat = pickupMarker.getPosition().lat();
    const pickupLng = pickupMarker.getPosition().lng();
    const dropoffLat = dropoffMarker.getPosition().lat();
    const dropoffLng = dropoffMarker.getPosition().lng();
    
    // Send prediction request via fetch
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            pickup_lat: pickupLat,
            pickup_lng: pickupLng,
            dropoff_lat: dropoffLat,
            dropoff_lng: dropoffLng
        })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        if (data.success) {
            displayPredictionResult(data);
        } else {
            showToast('Error: ' + data.error, 'error');
        }
    })
    .catch(error => {
        showLoading(false);
        showToast('Error: ' + error.message, 'error');
    });
}

// Display prediction result
function displayPredictionResult(data) {
    // Update price display
    const priceAmount = document.querySelector('.price-amount');
    priceAmount.textContent = `$${data.predicted_price}`;
    
    // Update details
    document.getElementById('distanceValue').textContent = `${data.distance_miles} miles`;
    document.getElementById('durationValue').textContent = `${data.estimated_duration} min`;
    document.getElementById('surgeValue').textContent = `${data.surge_multiplier}x`;
    
    // Add to recent predictions
    addToRecentPredictions({
        pickup: document.getElementById('pickupLocation').value,
        dropoff: document.getElementById('dropoffLocation').value,
        price: data.predicted_price,
        distance: data.distance_miles,
        duration: data.estimated_duration,
        timestamp: new Date()
    });
    
    // Update chart
    updateChart(data.predicted_price);
    
    showToast('Price prediction completed!', 'success');
}

// Add to recent predictions
function addToRecentPredictions(prediction) {
    recentPredictions.unshift(prediction);
    if (recentPredictions.length > 10) {
        recentPredictions.pop();
    }
    
    updateRecentPredictionsDisplay();
}

// Update recent predictions display
function updateRecentPredictionsDisplay() {
    const predictionsList = document.getElementById('predictionsList');
    
    if (recentPredictions.length === 0) {
        predictionsList.innerHTML = `
            <div class="no-predictions">
                <i class="fas fa-info-circle"></i>
                <p>No predictions yet. Enter locations to get started.</p>
            </div>
        `;
        return;
    }
    
    predictionsList.innerHTML = recentPredictions.map(prediction => `
        <div class="prediction-item">
            <div class="prediction-route">
                <div class="route">${prediction.pickup} → ${prediction.dropoff}</div>
                <div class="details">${prediction.distance} miles • ${prediction.duration} min</div>
            </div>
            <div class="prediction-price">$${prediction.price}</div>
        </div>
    `).join('');
}

// Update chart with new price
function updateChart(price) {
    const now = new Date();
    const timeLabel = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    priceChart.data.labels.push(timeLabel);
    priceChart.data.datasets[0].data.push(price);
    
    // Keep only last 10 data points
    if (priceChart.data.labels.length > 10) {
        priceChart.data.labels.shift();
        priceChart.data.datasets[0].data.shift();
    }
    
    priceChart.update('none');
}

// Start periodic updates for market conditions
function startPeriodicUpdates() {
    setInterval(updateMarketConditions, 5000); // Update every 5 seconds
}

// Update market conditions
function updateMarketConditions() {
    fetch('/api/current-conditions')
        .then(response => response.json())
        .then(data => {
            // Update demand
            document.getElementById('demandValue').textContent = data.demand;
            document.getElementById('demandProgress').style.width = `${data.demand * 100}%`;
            
            // Update supply
            document.getElementById('supplyValue').textContent = data.supply;
            document.getElementById('supplyProgress').style.width = `${data.supply * 100}%`;
            
            // Update weather
            document.getElementById('weatherValue').textContent = data.weather.charAt(0).toUpperCase() + data.weather.slice(1);
            updateWeatherIcon(data.weather);
            
            // Update traffic
            document.getElementById('trafficValue').textContent = data.traffic.charAt(0).toUpperCase() + data.traffic.slice(1);
            updateTrafficIcon(data.traffic);
        })
        .catch(error => {
            console.error('Error updating market conditions:', error);
        });
}

// Update weather icon
function updateWeatherIcon(weather) {
    const weatherIcon = document.getElementById('weatherIcon');
    const iconMap = {
        'clear': 'fas fa-sun',
        'rainy': 'fas fa-cloud-rain',
        'snowy': 'fas fa-snowflake',
        'stormy': 'fas fa-bolt'
    };
    
    weatherIcon.innerHTML = `<i class="${iconMap[weather] || 'fas fa-sun'}"></i>`;
}

// Update traffic icon
function updateTrafficIcon(traffic) {
    const trafficIcon = document.getElementById('trafficIcon');
    const iconMap = {
        'normal': 'fas fa-car',
        'heavy': 'fas fa-car-side',
        'congested': 'fas fa-car-crash'
    };
    
    trafficIcon.innerHTML = `<i class="${iconMap[traffic] || 'fas fa-car'}"></i>`;
}

// Update connection status
function updateConnectionStatus(connected = true) {
    const statusElement = document.getElementById('connectionStatus');
    const icon = statusElement.querySelector('i');
    const text = statusElement.querySelector('span');
    
    if (connected) {
        statusElement.classList.add('connected');
        icon.className = 'fas fa-circle';
        text.textContent = 'Connected';
    } else {
        statusElement.classList.remove('connected');
        icon.className = 'fas fa-circle';
        text.textContent = 'Disconnected';
    }
}

// Show/hide loading overlay
function showLoading(show) {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (show) {
        loadingOverlay.classList.add('show');
    } else {
        loadingOverlay.classList.remove('show');
    }
}

// Show toast notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastIcon = toast.querySelector('.toast-icon');
    const toastMessage = toast.querySelector('.toast-message');
    
    // Set icon based on type
    if (type === 'success') {
        toastIcon.className = 'fas fa-check-circle';
        toast.classList.add('success');
        toast.classList.remove('error');
    } else {
        toastIcon.className = 'fas fa-exclamation-circle';
        toast.classList.add('error');
        toast.classList.remove('success');
    }
    
    toastMessage.textContent = message;
    toast.classList.add('show');
    
    // Hide after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Map styles for a modern look
function getMapStyles() {
    return [
        {
            "featureType": "all",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "weight": "2.00"
                }
            ]
        },
        {
            "featureType": "all",
            "elementType": "geometry.stroke",
            "stylers": [
                {
                    "color": "#9c9c9c"
                }
            ]
        },
        {
            "featureType": "all",
            "elementType": "labels.text",
            "stylers": [
                {
                    "visibility": "on"
                }
            ]
        },
        {
            "featureType": "landscape",
            "elementType": "all",
            "stylers": [
                {
                    "color": "#f2f2f2"
                }
            ]
        },
        {
            "featureType": "landscape",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#ffffff"
                }
            ]
        },
        {
            "featureType": "landscape.man_made",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#ffffff"
                }
            ]
        },
        {
            "featureType": "poi",
            "elementType": "all",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "road",
            "elementType": "all",
            "stylers": [
                {
                    "saturation": -100
                },
                {
                    "lightness": 45
                }
            ]
        },
        {
            "featureType": "road",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#eeeeee"
                }
            ]
        },
        {
            "featureType": "road",
            "elementType": "labels.text.fill",
            "stylers": [
                {
                    "color": "#7b7b7b"
                }
            ]
        },
        {
            "featureType": "road",
            "elementType": "labels.text.stroke",
            "stylers": [
                {
                    "color": "#ffffff"
                }
            ]
        },
        {
            "featureType": "road.highway",
            "elementType": "all",
            "stylers": [
                {
                    "visibility": "simplified"
                }
            ]
        },
        {
            "featureType": "road.arterial",
            "elementType": "labels.icon",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "transit",
            "elementType": "all",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "all",
            "stylers": [
                {
                    "color": "#46bcec"
                },
                {
                    "visibility": "on"
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#c8d7d4"
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "labels.text.fill",
            "stylers": [
                {
                    "color": "#070707"
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "labels.text.stroke",
            "stylers": [
                {
                    "color": "#ffffff"
                }
            ]
        }
    ];
}