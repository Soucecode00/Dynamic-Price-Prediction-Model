#!/usr/bin/env python3
"""
Model Training Script for RidePrice Pro
Trains a price prediction model using the existing Uber dataset
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_and_preprocess_data(file_path='sample_data.xlsx'):
    """
    Load and preprocess the Uber dataset
    """
    try:
        # Load the data
        df = pd.read_excel(file_path)
        print(f"✅ Loaded data with {len(df)} rows and {len(df.columns)} columns")
        
        # Display basic info
        print("\n📊 Dataset Overview:")
        print(f"Columns: {list(df.columns)}")
        print(f"Shape: {df.shape}")
        print(f"Missing values: {df.isnull().sum().sum()}")
        
        return df
        
    except FileNotFoundError:
        print(f"❌ File {file_path} not found. Creating synthetic data...")
        return create_synthetic_data()
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return create_synthetic_data()

def create_synthetic_data(n_samples=1000):
    """
    Create synthetic data for demonstration purposes
    """
    np.random.seed(42)
    
    # Generate synthetic features
    data = {
        'distance_miles': np.random.uniform(0.5, 50, n_samples),
        'duration_minutes': np.random.uniform(5, 120, n_samples),
        'demand_level': np.random.uniform(0.1, 1.0, n_samples),
        'supply_level': np.random.uniform(0.1, 1.0, n_samples),
        'weather_clear': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'weather_rainy': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
        'weather_snowy': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
        'traffic_normal': np.random.choice([0, 1], n_samples, p=[0.6, 0.4]),
        'traffic_heavy': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'time_rush_hour': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'time_night': np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
    }
    
    df = pd.DataFrame(data)
    
    # Generate target variable (price) based on features
    base_fare = 2.50
    per_mile_rate = 1.50
    per_minute_rate = 0.35
    
    # Calculate base price
    df['base_price'] = (base_fare + 
                       df['distance_miles'] * per_mile_rate + 
                       df['duration_minutes'] * per_minute_rate)
    
    # Apply multipliers
    demand_supply_multiplier = 1.0 + (df['demand_level'] - df['supply_level']) * 0.5
    weather_multiplier = (1.0 * df['weather_clear'] + 
                         1.1 * df['weather_rainy'] + 
                         1.3 * df['weather_snowy'])
    traffic_multiplier = (1.0 * df['traffic_normal'] + 
                         1.15 * df['traffic_heavy'])
    time_multiplier = (1.0 * (1 - df['time_rush_hour'] - df['time_night']) + 
                       1.2 * df['time_rush_hour'] + 
                       1.1 * df['time_night'])
    
    # Calculate final price
    df['price'] = (df['base_price'] * 
                   demand_supply_multiplier * 
                   weather_multiplier * 
                   traffic_multiplier * 
                   time_multiplier)
    
    # Add some noise to make it more realistic
    df['price'] += np.random.normal(0, 0.5, n_samples)
    df['price'] = df['price'].clip(lower=2.50)  # Minimum fare
    
    print(f"✅ Created synthetic dataset with {len(df)} samples")
    return df

def prepare_features(df):
    """
    Prepare features for model training
    """
    # Select features for training
    feature_columns = [
        'distance_miles', 'duration_minutes', 'demand_level', 'supply_level',
        'weather_clear', 'weather_rainy', 'weather_snowy',
        'traffic_normal', 'traffic_heavy',
        'time_rush_hour', 'time_night'
    ]
    
    X = df[feature_columns]
    y = df['price']
    
    print(f"✅ Prepared {len(feature_columns)} features for training")
    print(f"Feature names: {list(X.columns)}")
    
    return X, y

def train_models(X, y):
    """
    Train multiple models and compare performance
    """
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\n🔄 Training models...")
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42)
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\n📈 Training {name}...")
        
        # Train the model
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        results[name] = {
            'model': model,
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'predictions': y_pred
        }
        
        print(f"✅ {name} Results:")
        print(f"   RMSE: ${rmse:.2f}")
        print(f"   MAE: ${mae:.2f}")
        print(f"   R²: {r2:.3f}")
    
    return results, X_test, y_test

def save_best_model(results, model_name='price_prediction_model'):
    """
    Save the best performing model
    """
    # Find the best model based on R² score
    best_model_name = max(results.keys(), key=lambda k: results[k]['r2'])
    best_model = results[best_model_name]['model']
    
    # Create models directory
    os.makedirs('models', exist_ok=True)
    
    # Save the model
    model_path = f'models/{model_name}.pkl'
    joblib.dump(best_model, model_path)
    
    print(f"\n💾 Saved best model ({best_model_name}) to {model_path}")
    print(f"Model performance: R² = {results[best_model_name]['r2']:.3f}")
    
    return model_path

def create_model_info(results, model_path):
    """
    Create a model info file with performance metrics
    """
    best_model_name = max(results.keys(), key=lambda k: results[k]['r2'])
    best_results = results[best_model_name]
    
    model_info = {
        'model_name': best_model_name,
        'training_date': datetime.now().isoformat(),
        'performance_metrics': {
            'rmse': best_results['rmse'],
            'mae': best_results['mae'],
            'r2': best_results['r2']
        },
        'feature_names': [
            'distance_miles', 'duration_minutes', 'demand_level', 'supply_level',
            'weather_clear', 'weather_rainy', 'weather_snowy',
            'traffic_normal', 'traffic_heavy',
            'time_rush_hour', 'time_night'
        ],
        'model_path': model_path
    }
    
    # Save model info
    info_path = model_path.replace('.pkl', '_info.json')
    import json
    with open(info_path, 'w') as f:
        json.dump(model_info, f, indent=2)
    
    print(f"📋 Model info saved to {info_path}")
    return model_info

def main():
    """
    Main training pipeline
    """
    print("🚗 RidePrice Pro - Model Training")
    print("=" * 50)
    
    # Load and preprocess data
    df = load_and_preprocess_data()
    
    # Prepare features
    X, y = prepare_features(df)
    
    # Train models
    results, X_test, y_test = train_models(X, y)
    
    # Save best model
    model_path = save_best_model(results)
    
    # Create model info
    model_info = create_model_info(results, model_path)
    
    print("\n🎉 Model training completed successfully!")
    print(f"📁 Model saved to: {model_path}")
    print(f"📊 Best model: {model_info['model_name']}")
    print(f"📈 R² Score: {model_info['performance_metrics']['r2']:.3f}")
    
    print("\n🔧 To use this model in the app:")
    print("1. The model will be automatically loaded by app.py")
    print("2. You can also manually load it with:")
    print(f"   model = joblib.load('{model_path}')")
    
    return model_path

if __name__ == "__main__":
    main()