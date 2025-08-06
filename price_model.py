import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
from datetime import datetime, timedelta
import os

class PricePredictionModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'distance', 'hour', 'day_of_week', 'is_weekend',
            'active_drivers', 'ride_requests', 'weather_factor',
            'traffic_factor', 'pickup_lat', 'pickup_lng',
            'dropoff_lat', 'dropoff_lng', 'demand_supply_ratio',
            'rush_hour', 'weekend_evening', 'distance_squared'
        ]
        self.load_or_train_model()
    
    def generate_training_data(self, n_samples=10000):
        """Generate synthetic training data for the price prediction model"""
        np.random.seed(42)
        
        data = []
        for i in range(n_samples):
            # Generate realistic features
            distance = np.random.exponential(5)  # Most rides are short
            hour = np.random.randint(0, 24)
            day_of_week = np.random.randint(0, 7)
            is_weekend = 1 if day_of_week >= 5 else 0
            
            # Rush hour patterns
            rush_hour = 1 if (7 <= hour <= 9) or (17 <= hour <= 19) else 0
            weekend_evening = 1 if is_weekend and (19 <= hour <= 23) else 0
            
            # Market conditions
            base_drivers = 100 + np.random.normal(0, 20)
            base_requests = 30 + np.random.normal(0, 10)
            
            # Adjust for time patterns
            if rush_hour:
                base_requests *= 2.5
                base_drivers *= 0.8
            elif weekend_evening:
                base_requests *= 1.8
                base_drivers *= 0.9
            elif 22 <= hour or hour <= 5:  # Late night
                base_requests *= 0.5
                base_drivers *= 0.3
            
            active_drivers = max(10, base_drivers + np.random.normal(0, 15))
            ride_requests = max(1, base_requests + np.random.normal(0, 8))
            
            demand_supply_ratio = ride_requests / active_drivers
            
            # Weather and traffic factors
            weather_factor = np.random.uniform(0.8, 1.5)
            traffic_factor = np.random.uniform(0.8, 2.0)
            
            if rush_hour:
                traffic_factor *= 1.5
            
            # Location (simplified NYC coordinates)
            pickup_lat = 40.7128 + np.random.normal(0, 0.1)
            pickup_lng = -74.0060 + np.random.normal(0, 0.1)
            dropoff_lat = pickup_lat + np.random.normal(0, 0.05)
            dropoff_lng = pickup_lng + np.random.normal(0, 0.05)
            
            # Feature engineering
            distance_squared = distance ** 2
            
            # Calculate base price using a realistic pricing model
            base_fare = 2.50
            distance_rate = 1.75 * distance
            time_rate = 0.35 * (distance / 20 * 60)  # Assuming 20 mph average speed
            
            # Apply factors
            price = (base_fare + distance_rate + time_rate) * weather_factor * traffic_factor
            
            # Surge pricing based on demand/supply
            if demand_supply_ratio > 0.8:
                price *= 1.5
            elif demand_supply_ratio > 0.6:
                price *= 1.3
            elif demand_supply_ratio > 0.4:
                price *= 1.1
            
            # Weekend and rush hour premiums
            if rush_hour:
                price *= 1.2
            elif weekend_evening:
                price *= 1.15
            
            # Add some noise
            price *= np.random.uniform(0.9, 1.1)
            
            data.append({
                'distance': distance,
                'hour': hour,
                'day_of_week': day_of_week,
                'is_weekend': is_weekend,
                'active_drivers': active_drivers,
                'ride_requests': ride_requests,
                'weather_factor': weather_factor,
                'traffic_factor': traffic_factor,
                'pickup_lat': pickup_lat,
                'pickup_lng': pickup_lng,
                'dropoff_lat': dropoff_lat,
                'dropoff_lng': dropoff_lng,
                'demand_supply_ratio': demand_supply_ratio,
                'rush_hour': rush_hour,
                'weekend_evening': weekend_evening,
                'distance_squared': distance_squared,
                'price': price
            })
        
        return pd.DataFrame(data)
    
    def train_model(self):
        """Train the price prediction model"""
        print("Generating training data...")
        df = self.generate_training_data()
        
        # Prepare features and target
        X = df[self.feature_columns]
        y = df['price']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train ensemble model
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        
        rf_model.fit(X_train_scaled, y_train)
        gb_model.fit(X_train_scaled, y_train)
        
        # Create ensemble predictions
        rf_pred = rf_model.predict(X_test_scaled)
        gb_pred = gb_model.predict(X_test_scaled)
        ensemble_pred = 0.6 * rf_pred + 0.4 * gb_pred
        
        # Evaluate
        mae = mean_absolute_error(y_test, ensemble_pred)
        r2 = r2_score(y_test, ensemble_pred)
        
        print(f"Model Performance - MAE: {mae:.2f}, R²: {r2:.3f}")
        
        # Store both models for ensemble prediction
        self.model = {
            'rf': rf_model,
            'gb': gb_model,
            'weights': [0.6, 0.4]
        }
        
        # Save model and scaler
        self.save_model()
        
        return self.model
    
    def predict(self, features):
        """Predict price for given features"""
        if self.model is None:
            self.load_or_train_model()
        
        # Convert to DataFrame and engineer features
        if isinstance(features, dict):
            df = pd.DataFrame([features])
        else:
            df = features.copy()
        
        # Engineer additional features
        df['demand_supply_ratio'] = df['ride_requests'] / df['active_drivers']
        df['rush_hour'] = ((df['hour'] >= 7) & (df['hour'] <= 9)) | ((df['hour'] >= 17) & (df['hour'] <= 19))
        df['weekend_evening'] = (df['is_weekend'] == 1) & (df['hour'] >= 19) & (df['hour'] <= 23)
        df['distance_squared'] = df['distance'] ** 2
        
        # Ensure all features are present
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0
        
        # Select and scale features
        X = df[self.feature_columns]
        X_scaled = self.scaler.transform(X)
        
        # Ensemble prediction
        rf_pred = self.model['rf'].predict(X_scaled)
        gb_pred = self.model['gb'].predict(X_scaled)
        
        weights = self.model['weights']
        prediction = weights[0] * rf_pred + weights[1] * gb_pred
        
        return max(2.0, prediction[0])  # Minimum fare of $2
    
    def save_model(self):
        """Save the trained model and scaler"""
        if not os.path.exists('models'):
            os.makedirs('models')
        
        joblib.dump(self.model, 'models/price_model.pkl')
        joblib.dump(self.scaler, 'models/scaler.pkl')
        print("Model saved successfully!")
    
    def load_model(self):
        """Load the trained model and scaler"""
        try:
            self.model = joblib.load('models/price_model.pkl')
            self.scaler = joblib.load('models/scaler.pkl')
            print("Model loaded successfully!")
            return True
        except FileNotFoundError:
            print("No saved model found.")
            return False
    
    def load_or_train_model(self):
        """Load existing model or train a new one"""
        if not self.load_model():
            print("Training new model...")
            self.train_model()
    
    def get_feature_importance(self):
        """Get feature importance from the random forest model"""
        if self.model is None:
            return None
        
        importance = self.model['rf'].feature_importances_
        feature_importance = dict(zip(self.feature_columns, importance))
        return dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
    
    def retrain_with_new_data(self, new_data):
        """Retrain model with new ride data"""
        # This would be called periodically with real ride data
        # For now, we'll just retrain with synthetic data
        print("Retraining model with updated data...")
        self.train_model()
        print("Model retrained successfully!")

if __name__ == "__main__":
    # Test the model
    model = PricePredictionModel()
    
    # Test prediction
    test_features = {
        'distance': 5.2,
        'hour': 18,
        'day_of_week': 1,
        'is_weekend': 0,
        'active_drivers': 85,
        'ride_requests': 65,
        'weather_factor': 1.1,
        'traffic_factor': 1.4,
        'pickup_lat': 40.7128,
        'pickup_lng': -74.0060,
        'dropoff_lat': 40.7589,
        'dropoff_lng': -73.9851
    }
    
    predicted_price = model.predict(test_features)
    print(f"Predicted price: ${predicted_price:.2f}")
    
    # Show feature importance
    importance = model.get_feature_importance()
    print("\nFeature Importance:")
    for feature, imp in importance.items():
        print(f"{feature}: {imp:.3f}")