from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import os
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI(title="Uber-Style Real-Time Price Prediction", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for real-time data
active_connections: List[WebSocket] = []
current_demand = 1.0
current_supply = 1.0
base_prices = {
    "economy": 2.5,
    "comfort": 3.5,
    "premium": 5.0,
    "luxury": 8.0
}

# Pydantic models
class PriceRequest(BaseModel):
    pickup_lat: float
    pickup_lng: float
    dropoff_lat: float
    dropoff_lng: float
    ride_type: str = "economy"
    time_of_day: Optional[str] = None

class PriceResponse(BaseModel):
    base_price: float
    dynamic_price: float
    surge_multiplier: float
    total_price: float
    estimated_duration: int
    estimated_distance: float
    demand_factor: float
    supply_factor: float

# Simple ML model for price prediction
class PricePredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def calculate_distance(self, lat1, lng1, lat2, lng2):
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lng1, lat2, lng2 = map(np.radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlng/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        distance = R * c
        
        return distance
    
    def extract_features(self, pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, time_of_day=None):
        """Extract features for price prediction"""
        distance = self.calculate_distance(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng)
        
        # Time-based features
        now = datetime.now()
        hour = now.hour
        day_of_week = now.weekday()
        
        # Peak hours (7-9 AM, 5-7 PM)
        is_peak_hour = 1 if (7 <= hour <= 9) or (17 <= hour <= 19) else 0
        
        # Weekend factor
        is_weekend = 1 if day_of_week >= 5 else 0
        
        # Distance-based features
        distance_squared = distance ** 2
        
        return np.array([distance, distance_squared, hour, day_of_week, is_peak_hour, is_weekend])
    
    def train_model(self):
        """Train the model with synthetic data"""
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Generate random coordinates (simulating a city area)
        pickup_lats = np.random.uniform(40.7, 40.8, n_samples)
        pickup_lngs = np.random.uniform(-74.0, -73.9, n_samples)
        dropoff_lats = np.random.uniform(40.7, 40.8, n_samples)
        dropoff_lngs = np.random.uniform(-74.0, -73.9, n_samples)
        
        # Generate features and prices
        X = []
        y = []
        
        for i in range(n_samples):
            features = self.extract_features(
                pickup_lats[i], pickup_lngs[i], 
                dropoff_lats[i], dropoff_lngs[i]
            )
            X.append(features)
            
            # Generate realistic prices based on distance and time
            distance = self.calculate_distance(
                pickup_lats[i], pickup_lngs[i], 
                dropoff_lats[i], dropoff_lngs[i]
            )
            
            # Base price calculation
            base_price = 2.5 + (distance * 2.5)  # $2.5 base + $2.5 per km
            
            # Add time-based variations
            hour = features[2]
            if 7 <= hour <= 9 or 17 <= hour <= 19:  # Peak hours
                base_price *= 1.3
            elif 22 <= hour or hour <= 6:  # Late night
                base_price *= 1.2
            
            # Add some randomness
            base_price += np.random.normal(0, 0.5)
            base_price = max(base_price, 5.0)  # Minimum fare
            
            y.append(base_price)
        
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        print("Model trained successfully!")
    
    def predict_price(self, pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, time_of_day=None):
        """Predict base price for a ride"""
        if not self.is_trained:
            self.train_model()
        
        features = self.extract_features(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, time_of_day)
        features_scaled = self.scaler.transform([features])
        
        base_price = self.model.predict(features_scaled)[0]
        return max(base_price, 5.0)  # Ensure minimum fare

# Initialize price predictor
predictor = PricePredictor()

@app.get("/")
async def root():
    """Serve the main HTML page"""
    with open("static/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/predict-price", response_model=PriceResponse)
async def predict_price(request: PriceRequest):
    """Predict real-time price for a ride"""
    global current_demand, current_supply
    
    # Get base price from ML model
    base_price = predictor.predict_price(
        request.pickup_lat, request.pickup_lng,
        request.dropoff_lat, request.dropoff_lng,
        request.time_of_day
    )
    
    # Calculate distance
    distance = predictor.calculate_distance(
        request.pickup_lat, request.pickup_lng,
        request.dropoff_lat, request.dropoff_lng
    )
    
    # Calculate dynamic pricing factors
    surge_multiplier = 1.0 + (current_demand / current_supply - 1.0) * 0.5
    surge_multiplier = max(1.0, min(3.0, surge_multiplier))  # Cap between 1x and 3x
    
    # Calculate final price
    dynamic_price = base_price * surge_multiplier
    
    # Estimate duration (assuming average speed of 30 km/h in city)
    estimated_duration = int(distance / 30 * 60)  # in minutes
    
    return PriceResponse(
        base_price=round(base_price, 2),
        dynamic_price=round(dynamic_price, 2),
        surge_multiplier=round(surge_multiplier, 2),
        total_price=round(dynamic_price, 2),
        estimated_duration=estimated_duration,
        estimated_distance=round(distance, 2),
        demand_factor=round(current_demand, 2),
        supply_factor=round(current_supply, 2)
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Send real-time updates every 5 seconds
            await asyncio.sleep(5)
            
            # Simulate changing demand and supply
            global current_demand, current_supply
            
            # Random fluctuations
            current_demand += random.uniform(-0.1, 0.1)
            current_supply += random.uniform(-0.05, 0.05)
            
            # Keep values reasonable
            current_demand = max(0.5, min(2.0, current_demand))
            current_supply = max(0.5, min(2.0, current_supply))
            
            # Send update
            update_data = {
                "type": "market_update",
                "demand": round(current_demand, 2),
                "supply": round(current_supply, 2),
                "surge_multiplier": round(1.0 + (current_demand / current_supply - 1.0) * 0.5, 2),
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send_text(json.dumps(update_data))
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@app.get("/api/market-status")
async def get_market_status():
    """Get current market status"""
    return {
        "demand": round(current_demand, 2),
        "supply": round(current_supply, 2),
        "surge_multiplier": round(1.0 + (current_demand / current_supply - 1.0) * 0.5, 2),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/update-demand")
async def update_demand(demand: float):
    """Update demand factor (for testing)"""
    global current_demand
    current_demand = max(0.5, min(2.0, demand))
    return {"demand": current_demand}

@app.post("/api/update-supply")
async def update_supply(supply: float):
    """Update supply factor (for testing)"""
    global current_supply
    current_supply = max(0.5, min(2.0, supply))
    return {"supply": current_supply}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)