from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import os
import json
from datetime import datetime, timedelta
import threading
import time
import random
from geopy.distance import geodesic
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global variables for real-time data
current_demand = 0.5
current_supply = 0.5
weather_conditions = "clear"
traffic_conditions = "normal"
base_fare = 2.50
price_multiplier = 1.0

# Load the trained model (we'll create this)
model = None
print("Using built-in price prediction algorithm")

class PricePredictor:
    def __init__(self):
        self.base_fare = 2.50
        self.per_mile_rate = 1.50
        self.per_minute_rate = 0.35
        self.surge_multiplier = 1.0
        
    def predict_price(self, distance_miles, duration_minutes, demand_level=0.5, 
                     supply_level=0.5, weather="clear", traffic="normal", 
                     time_of_day="day", day_of_week="weekday"):
        """Predict ride price based on various factors"""
        
        # Base calculation
        base_price = self.base_fare + (distance_miles * self.per_mile_rate) + (duration_minutes * self.per_minute_rate)
        
        # Demand/supply multiplier
        demand_supply_multiplier = 1.0 + (demand_level - supply_level) * 0.5
        self.surge_multiplier = max(0.8, min(2.0, demand_supply_multiplier))
        
        # Weather multiplier
        weather_multipliers = {
            "clear": 1.0,
            "rainy": 1.1,
            "snowy": 1.3,
            "stormy": 1.2
        }
        weather_multiplier = weather_multipliers.get(weather, 1.0)
        
        # Traffic multiplier
        traffic_multipliers = {
            "normal": 1.0,
            "heavy": 1.15,
            "congested": 1.25
        }
        traffic_multiplier = traffic_multipliers.get(traffic, 1.0)
        
        # Time of day multiplier
        time_multipliers = {
            "day": 1.0,
            "rush_hour": 1.2,
            "night": 1.1,
            "early_morning": 1.05
        }
        time_multiplier = time_multipliers.get(time_of_day, 1.0)
        
        # Calculate final price
        final_price = base_price * self.surge_multiplier * weather_multiplier * traffic_multiplier * time_multiplier
        
        return round(final_price, 2)
    
    def get_surge_multiplier(self):
        return self.surge_multiplier

predictor = PricePredictor()

# Real-time data simulation
def simulate_real_time_data():
    """Simulate real-time changes in demand, supply, and conditions"""
    global current_demand, current_supply, weather_conditions, traffic_conditions
    
    while True:
        # Simulate demand changes
        current_demand += random.uniform(-0.1, 0.1)
        current_demand = max(0.1, min(1.0, current_demand))
        
        # Simulate supply changes
        current_supply += random.uniform(-0.05, 0.05)
        current_supply = max(0.1, min(1.0, current_supply))
        
        # Simulate weather changes (less frequent)
        if random.random() < 0.1:
            weather_options = ["clear", "rainy", "snowy", "stormy"]
            weather_conditions = random.choice(weather_options)
        
        # Simulate traffic changes
        if random.random() < 0.15:
            traffic_options = ["normal", "heavy", "congested"]
            traffic_conditions = random.choice(traffic_options)
        
        # Emit real-time updates
        socketio.emit('real_time_update', {
            'demand': round(current_demand, 2),
            'supply': round(current_supply, 2),
            'weather': weather_conditions,
            'traffic': traffic_conditions,
            'surge_multiplier': round(predictor.get_surge_multiplier(), 2)
        })
        
        time.sleep(5)  # Update every 5 seconds

# Start real-time simulation in background
real_time_thread = threading.Thread(target=simulate_real_time_data, daemon=True)
real_time_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_price():
    """API endpoint for price prediction"""
    try:
        data = request.get_json()
        
        # Extract parameters
        pickup_lat = float(data.get('pickup_lat', 0))
        pickup_lng = float(data.get('pickup_lng', 0))
        dropoff_lat = float(data.get('dropoff_lat', 0))
        dropoff_lng = float(data.get('dropoff_lng', 0))
        
        # Calculate distance
        pickup_coords = (pickup_lat, pickup_lng)
        dropoff_coords = (dropoff_lat, dropoff_lng)
        distance_miles = geodesic(pickup_coords, dropoff_coords).miles
        
        # Estimate duration (assuming average speed of 25 mph)
        estimated_duration = distance_miles / 25 * 60  # minutes
        
        # Get current conditions
        time_now = datetime.now()
        hour = time_now.hour
        
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            time_of_day = "rush_hour"
        elif 22 <= hour or hour <= 6:
            time_of_day = "night"
        elif 6 < hour < 7:
            time_of_day = "early_morning"
        else:
            time_of_day = "day"
        
        # Predict price
        predicted_price = predictor.predict_price(
            distance_miles=distance_miles,
            duration_minutes=estimated_duration,
            demand_level=current_demand,
            supply_level=current_supply,
            weather=weather_conditions,
            traffic=traffic_conditions,
            time_of_day=time_of_day
        )
        
        return jsonify({
            'success': True,
            'predicted_price': predicted_price,
            'distance_miles': round(distance_miles, 2),
            'estimated_duration': round(estimated_duration, 1),
            'surge_multiplier': round(predictor.get_surge_multiplier(), 2),
            'current_conditions': {
                'demand': round(current_demand, 2),
                'supply': round(current_supply, 2),
                'weather': weather_conditions,
                'traffic': traffic_conditions
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/current-conditions')
def get_current_conditions():
    """API endpoint to get current market conditions"""
    return jsonify({
        'demand': round(current_demand, 2),
        'supply': round(current_supply, 2),
        'weather': weather_conditions,
        'traffic': traffic_conditions,
        'surge_multiplier': round(predictor.get_surge_multiplier(), 2),
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'status': 'connected'})

@socketio.on('request_prediction')
def handle_prediction_request(data):
    """Handle real-time prediction requests"""
    try:
        # Extract data
        pickup_lat = float(data.get('pickup_lat', 0))
        pickup_lng = float(data.get('pickup_lng', 0))
        dropoff_lat = float(data.get('dropoff_lat', 0))
        dropoff_lng = float(data.get('dropoff_lng', 0))
        
        # Calculate distance
        pickup_coords = (pickup_lat, pickup_lng)
        dropoff_coords = (dropoff_lat, dropoff_lng)
        distance_miles = geodesic(pickup_coords, dropoff_coords).miles
        
        # Estimate duration
        estimated_duration = distance_miles / 25 * 60
        
        # Get time of day
        time_now = datetime.now()
        hour = time_now.hour
        
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            time_of_day = "rush_hour"
        elif 22 <= hour or hour <= 6:
            time_of_day = "night"
        elif 6 < hour < 7:
            time_of_day = "early_morning"
        else:
            time_of_day = "day"
        
        # Predict price
        predicted_price = predictor.predict_price(
            distance_miles=distance_miles,
            duration_minutes=estimated_duration,
            demand_level=current_demand,
            supply_level=current_supply,
            weather=weather_conditions,
            traffic=traffic_conditions,
            time_of_day=time_of_day
        )
        
        emit('prediction_result', {
            'predicted_price': predicted_price,
            'distance_miles': round(distance_miles, 2),
            'estimated_duration': round(estimated_duration, 1),
            'surge_multiplier': round(predictor.get_surge_multiplier(), 2),
            'current_conditions': {
                'demand': round(current_demand, 2),
                'supply': round(current_supply, 2),
                'weather': weather_conditions,
                'traffic': traffic_conditions
            }
        })
        
    except Exception as e:
        emit('prediction_error', {'error': str(e)})

if __name__ == '__main__':
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("🚗 Starting Uber-like Price Prediction App...")
    print("📍 Access the app at: http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)