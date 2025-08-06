import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import math

class DataSimulator:
    def __init__(self):
        self.base_drivers = 150
        self.base_requests = 45
        self.time_patterns = self._create_time_patterns()
        self.weather_states = ['clear', 'rain', 'snow', 'fog']
        self.current_weather = 'clear'
        
    def _create_time_patterns(self):
        """Create realistic time-based patterns for demand and supply"""
        patterns = {}
        
        # Hourly patterns (0-23)
        patterns['hourly_demand'] = {
            0: 0.3, 1: 0.2, 2: 0.15, 3: 0.1, 4: 0.1, 5: 0.2,
            6: 0.4, 7: 0.8, 8: 1.2, 9: 0.9, 10: 0.7, 11: 0.8,
            12: 1.0, 13: 0.9, 14: 0.8, 15: 0.9, 16: 1.1, 17: 1.5,
            18: 1.8, 19: 1.6, 20: 1.3, 21: 1.1, 22: 0.8, 23: 0.5
        }
        
        patterns['hourly_supply'] = {
            0: 0.4, 1: 0.3, 2: 0.2, 3: 0.15, 4: 0.2, 5: 0.3,
            6: 0.6, 7: 1.0, 8: 1.3, 9: 1.2, 10: 1.0, 11: 1.0,
            12: 1.1, 13: 1.0, 14: 1.0, 15: 1.0, 16: 1.1, 17: 1.2,
            18: 1.4, 19: 1.3, 20: 1.1, 21: 0.9, 22: 0.7, 23: 0.5
        }
        
        # Day of week patterns (0=Monday, 6=Sunday)
        patterns['daily_demand'] = {
            0: 1.0, 1: 1.0, 2: 1.0, 3: 1.1, 4: 1.2, 5: 1.4, 6: 1.1
        }
        
        patterns['daily_supply'] = {
            0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.2, 6: 0.9
        }
        
        return patterns
    
    def update_market_conditions(self, current_data):
        """Update market conditions based on time and random factors"""
        now = datetime.now()
        hour = now.hour
        day_of_week = now.weekday()
        
        # Get base patterns
        demand_multiplier = (
            self.time_patterns['hourly_demand'][hour] * 
            self.time_patterns['daily_demand'][day_of_week]
        )
        supply_multiplier = (
            self.time_patterns['hourly_supply'][hour] * 
            self.time_patterns['daily_supply'][day_of_week]
        )
        
        # Add random variation
        demand_noise = np.random.normal(1.0, 0.1)
        supply_noise = np.random.normal(1.0, 0.08)
        
        # Calculate new values
        new_requests = max(5, int(self.base_requests * demand_multiplier * demand_noise))
        new_drivers = max(20, int(self.base_drivers * supply_multiplier * supply_noise))
        
        # Update weather occasionally
        if random.random() < 0.1:  # 10% chance to change weather
            self.current_weather = random.choice(self.weather_states)
        
        # Weather impact
        weather_factor = self._get_weather_factor()
        
        # Traffic factor based on time and random events
        traffic_factor = self._get_traffic_factor(hour, day_of_week)
        
        # Calculate surge multiplier
        demand_supply_ratio = new_requests / new_drivers
        surge_multiplier = self._calculate_surge(demand_supply_ratio, weather_factor, traffic_factor)
        
        # Create updated data
        updated_data = {
            'active_drivers': new_drivers,
            'ride_requests': new_requests,
            'surge_multiplier': round(surge_multiplier, 2),
            'weather_factor': round(weather_factor, 2),
            'traffic_factor': round(traffic_factor, 2),
            'weather_condition': self.current_weather,
            'demand_supply_ratio': round(demand_supply_ratio, 3),
            'timestamp': now.isoformat()
        }
        
        return updated_data
    
    def _get_weather_factor(self):
        """Get weather impact factor"""
        weather_impacts = {
            'clear': 1.0,
            'rain': 1.3,
            'snow': 1.6,
            'fog': 1.2
        }
        return weather_impacts.get(self.current_weather, 1.0)
    
    def _get_traffic_factor(self, hour, day_of_week):
        """Get traffic impact factor"""
        base_traffic = 1.0
        
        # Rush hour traffic
        if (7 <= hour <= 9) or (17 <= hour <= 19):
            base_traffic *= 1.5
        
        # Weekend traffic patterns
        if day_of_week >= 5:  # Weekend
            if 12 <= hour <= 16:  # Weekend afternoon
                base_traffic *= 1.2
            elif 20 <= hour <= 23:  # Weekend evening
                base_traffic *= 1.3
        
        # Random traffic events
        if random.random() < 0.05:  # 5% chance of traffic incident
            base_traffic *= random.uniform(1.3, 2.0)
        
        return min(2.5, base_traffic + np.random.normal(0, 0.1))
    
    def _calculate_surge(self, demand_supply_ratio, weather_factor, traffic_factor):
        """Calculate surge pricing multiplier"""
        base_surge = 1.0
        
        # Demand-supply based surge
        if demand_supply_ratio > 1.0:
            base_surge += (demand_supply_ratio - 1.0) * 0.8
        elif demand_supply_ratio > 0.8:
            base_surge += (demand_supply_ratio - 0.8) * 0.5
        elif demand_supply_ratio > 0.6:
            base_surge += (demand_supply_ratio - 0.6) * 0.25
        
        # Weather impact
        if weather_factor > 1.2:
            base_surge *= 1.1
        
        # Traffic impact
        if traffic_factor > 1.4:
            base_surge *= 1.05
        
        return min(3.0, max(1.0, base_surge))
    
    def generate_historical_data(self, days=7):
        """Generate historical pricing and demand data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        data = []
        current_date = start_date
        
        while current_date <= end_date:
            for hour in range(0, 24, 2):  # Every 2 hours
                timestamp = current_date.replace(hour=hour, minute=0, second=0)
                
                # Get patterns for this time
                demand_mult = (
                    self.time_patterns['hourly_demand'][hour] * 
                    self.time_patterns['daily_demand'][timestamp.weekday()]
                )
                supply_mult = (
                    self.time_patterns['hourly_supply'][hour] * 
                    self.time_patterns['daily_supply'][timestamp.weekday()]
                )
                
                # Add historical variation
                requests = max(5, int(self.base_requests * demand_mult * np.random.normal(1.0, 0.15)))
                drivers = max(20, int(self.base_drivers * supply_mult * np.random.normal(1.0, 0.12)))
                
                # Random weather and traffic for historical data
                weather_factor = random.choice([1.0, 1.0, 1.0, 1.2, 1.4])  # Mostly clear
                traffic_factor = random.uniform(0.8, 2.0)
                
                demand_supply_ratio = requests / drivers
                surge = self._calculate_surge(demand_supply_ratio, weather_factor, traffic_factor)
                
                # Calculate average price for this period
                avg_distance = 4.5  # Average ride distance
                base_price = 2.50 + (avg_distance * 1.75) + (avg_distance / 20 * 60 * 0.35)
                avg_price = base_price * surge * weather_factor * (traffic_factor * 0.1 + 0.9)
                
                data.append({
                    'timestamp': timestamp.isoformat(),
                    'hour': hour,
                    'day_of_week': timestamp.weekday(),
                    'active_drivers': drivers,
                    'ride_requests': requests,
                    'surge_multiplier': round(surge, 2),
                    'average_price': round(avg_price, 2),
                    'demand_supply_ratio': round(demand_supply_ratio, 3),
                    'weather_factor': weather_factor,
                    'traffic_factor': round(traffic_factor, 2)
                })
            
            current_date += timedelta(days=1)
        
        return data
    
    def generate_surge_zones(self):
        """Generate current surge pricing zones on a map"""
        # NYC-like coordinates with surge zones
        zones = []
        
        # Define base zones (simplified NYC areas)
        base_zones = [
            {'name': 'Manhattan Midtown', 'center_lat': 40.7549, 'center_lng': -73.9840},
            {'name': 'Financial District', 'center_lat': 40.7074, 'center_lng': -74.0113},
            {'name': 'Brooklyn Heights', 'center_lat': 40.6962, 'center_lng': -73.9961},
            {'name': 'Long Island City', 'center_lat': 40.7505, 'center_lng': -73.9426},
            {'name': 'Williamsburg', 'center_lat': 40.7081, 'center_lng': -73.9571},
            {'name': 'Upper East Side', 'center_lat': 40.7736, 'center_lng': -73.9566},
            {'name': 'Greenwich Village', 'center_lat': 40.7336, 'center_lng': -74.0027},
            {'name': 'Chinatown', 'center_lat': 40.7157, 'center_lng': -73.9970}
        ]
        
        for zone in base_zones:
            # Random surge for each zone
            surge = random.uniform(1.0, 2.5)
            
            # Higher surge in popular areas during peak times
            hour = datetime.now().hour
            if zone['name'] in ['Manhattan Midtown', 'Financial District'] and (7 <= hour <= 9 or 17 <= hour <= 19):
                surge *= 1.3
            
            # Create polygon points around center
            radius = 0.01  # Rough radius in degrees
            points = []
            for i in range(8):  # Octagon
                angle = (i * 2 * math.pi) / 8
                lat = zone['center_lat'] + radius * math.sin(angle)
                lng = zone['center_lng'] + radius * math.cos(angle)
                points.append([lat, lng])
            
            zones.append({
                'name': zone['name'],
                'center': [zone['center_lat'], zone['center_lng']],
                'polygon': points,
                'surge_multiplier': round(surge, 1),
                'color': self._get_surge_color(surge),
                'active_drivers': random.randint(5, 25),
                'ride_requests': random.randint(3, 20)
            })
        
        return zones
    
    def _get_surge_color(self, surge):
        """Get color based on surge multiplier"""
        if surge < 1.2:
            return '#22c55e'  # Green
        elif surge < 1.5:
            return '#eab308'  # Yellow
        elif surge < 2.0:
            return '#f97316'  # Orange
        else:
            return '#ef4444'  # Red
    
    def generate_real_time_events(self):
        """Generate random events that affect pricing"""
        events = []
        
        # Random event types
        event_types = [
            {'type': 'concert', 'impact': 1.4, 'duration': 180},
            {'type': 'sports_game', 'impact': 1.6, 'duration': 240},
            {'type': 'weather_alert', 'impact': 1.3, 'duration': 120},
            {'type': 'traffic_incident', 'impact': 1.5, 'duration': 90},
            {'type': 'public_transport_delay', 'impact': 1.7, 'duration': 150}
        ]
        
        # 20% chance of an active event
        if random.random() < 0.2:
            event = random.choice(event_types)
            events.append({
                'type': event['type'],
                'description': f"Active {event['type'].replace('_', ' ')} affecting demand",
                'impact_multiplier': event['impact'],
                'estimated_duration': event['duration'],
                'affected_zones': random.sample(['Manhattan', 'Brooklyn', 'Queens', 'Bronx'], 
                                              random.randint(1, 3))
            })
        
        return events
    
    def get_demand_forecast(self, hours_ahead=6):
        """Generate demand forecast for the next few hours"""
        forecast = []
        current_time = datetime.now()
        
        for i in range(hours_ahead):
            future_time = current_time + timedelta(hours=i)
            hour = future_time.hour
            day_of_week = future_time.weekday()
            
            demand_mult = (
                self.time_patterns['hourly_demand'][hour] * 
                self.time_patterns['daily_demand'][day_of_week]
            )
            
            forecasted_requests = int(self.base_requests * demand_mult)
            confidence = random.uniform(0.75, 0.95)  # Confidence decreases with time
            
            forecast.append({
                'time': future_time.strftime('%H:%M'),
                'forecasted_requests': forecasted_requests,
                'confidence': round(confidence, 2),
                'expected_surge': round(max(1.0, demand_mult * 0.8), 1)
            })
        
        return forecast

if __name__ == "__main__":
    # Test the data simulator
    simulator = DataSimulator()
    
    # Test market update
    initial_data = {
        'active_drivers': 150,
        'ride_requests': 45,
        'surge_multiplier': 1.0,
        'weather_factor': 1.0,
        'traffic_factor': 1.0,
        'timestamp': datetime.now().isoformat()
    }
    
    updated_data = simulator.update_market_conditions(initial_data)
    print("Updated market data:", updated_data)
    
    # Test historical data
    historical = simulator.generate_historical_data(2)
    print(f"\nGenerated {len(historical)} historical data points")
    
    # Test surge zones
    zones = simulator.generate_surge_zones()
    print(f"\nGenerated {len(zones)} surge zones")
    
    # Test forecast
    forecast = simulator.get_demand_forecast()
    print(f"\nDemand forecast: {forecast}")