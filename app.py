from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import threading
import time
from price_model import PricePredictionModel
from data_simulator import DataSimulator
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'taxi-price-prediction-secret'
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize models and data simulator
price_model = PricePredictionModel()
data_simulator = DataSimulator()

# Global variables for real-time data
current_market_data = {
    'active_drivers': 150,
    'ride_requests': 45,
    'surge_multiplier': 1.0,
    'weather_factor': 1.0,
    'traffic_factor': 1.0,
    'timestamp': datetime.now().isoformat()
}

@app.route('/api/predict_price', methods=['POST'])
def predict_price():
    """Predict ride price based on input parameters"""
    try:
        data = request.get_json()
        
        # Extract parameters
        pickup_lat = float(data.get('pickup_lat', 40.7128))
        pickup_lng = float(data.get('pickup_lng', -74.0060))
        dropoff_lat = float(data.get('dropoff_lat', 40.7589))
        dropoff_lng = float(data.get('dropoff_lng', -73.9851))
        ride_type = data.get('ride_type', 'standard')
        
        # Calculate distance
        distance = calculate_distance(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng)
        
        # Get current time features
        now = datetime.now()
        hour = now.hour
        day_of_week = now.weekday()
        is_weekend = day_of_week >= 5
        
        # Prepare features for model
        features = {
            'distance': distance,
            'hour': hour,
            'day_of_week': day_of_week,
            'is_weekend': is_weekend,
            'active_drivers': current_market_data['active_drivers'],
            'ride_requests': current_market_data['ride_requests'],
            'weather_factor': current_market_data['weather_factor'],
            'traffic_factor': current_market_data['traffic_factor'],
            'pickup_lat': pickup_lat,
            'pickup_lng': pickup_lng,
            'dropoff_lat': dropoff_lat,
            'dropoff_lng': dropoff_lng
        }
        
        # Predict price
        predicted_price = price_model.predict(features)
        
        # Apply surge multiplier
        final_price = predicted_price * current_market_data['surge_multiplier']
        
        # Calculate estimated time
        estimated_time = estimate_ride_time(distance, current_market_data['traffic_factor'])
        
        response = {
            'predicted_price': round(final_price, 2),
            'base_price': round(predicted_price, 2),
            'surge_multiplier': current_market_data['surge_multiplier'],
            'estimated_time': estimated_time,
            'distance': round(distance, 2),
            'breakdown': {
                'base_fare': round(predicted_price * 0.6, 2),
                'distance_cost': round(predicted_price * 0.3, 2),
                'time_cost': round(predicted_price * 0.1, 2),
                'surge_adjustment': round((final_price - predicted_price), 2)
            },
            'factors': {
                'demand_level': get_demand_level(),
                'supply_level': get_supply_level(),
                'weather_impact': current_market_data['weather_factor'],
                'traffic_impact': current_market_data['traffic_factor']
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/market_data', methods=['GET'])
def get_market_data():
    """Get current market conditions"""
    return jsonify(current_market_data)

@app.route('/api/historical_data', methods=['GET'])
def get_historical_data():
    """Get historical pricing data for charts"""
    days = int(request.args.get('days', 7))
    data = data_simulator.generate_historical_data(days)
    return jsonify(data)

@app.route('/api/surge_zones', methods=['GET'])
def get_surge_zones():
    """Get current surge pricing zones"""
    zones = data_simulator.generate_surge_zones()
    return jsonify(zones)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('market_update', current_market_data)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def update_market_data():
    """Background task to update market data and broadcast to clients"""
    global current_market_data
    
    while True:
        # Simulate real-time market changes
        current_market_data = data_simulator.update_market_conditions(current_market_data)
        
        # Broadcast to all connected clients
        socketio.emit('market_update', current_market_data)
        
        time.sleep(5)  # Update every 5 seconds

def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two points using Haversine formula"""
    from math import radians, cos, sin, asin, sqrt
    
    # Convert decimal degrees to radians
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    
    # Haversine formula
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * asin(sqrt(a))
    r = 3956  # Radius of earth in miles
    
    return c * r

def estimate_ride_time(distance, traffic_factor):
    """Estimate ride time based on distance and traffic"""
    base_speed = 25  # mph
    adjusted_speed = base_speed / traffic_factor
    return max(5, int((distance / adjusted_speed) * 60))  # Convert to minutes

def get_demand_level():
    """Get current demand level category"""
    requests = current_market_data['ride_requests']
    if requests < 20:
        return 'Low'
    elif requests < 50:
        return 'Medium'
    elif requests < 80:
        return 'High'
    else:
        return 'Very High'

def get_supply_level():
    """Get current supply level category"""
    drivers = current_market_data['active_drivers']
    if drivers < 50:
        return 'Low'
    elif drivers < 100:
        return 'Medium'
    elif drivers < 200:
        return 'High'
    else:
        return 'Very High'

if __name__ == '__main__':
    # Start background thread for market data updates
    market_thread = threading.Thread(target=update_market_data, daemon=True)
    market_thread.start()
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)