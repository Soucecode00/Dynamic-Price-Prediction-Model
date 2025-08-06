import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os
import math
from datetime import datetime
from tqdm import tqdm

# Bounding box for New York City area
LAT_MIN, LAT_MAX = 40.4, 40.9
LON_MIN, LON_MAX = -74.1, -73.7

BASE_FARE = 2.5  # base flag fare in USD
PER_KM_RATE = 1.5  # per km rate
PASSENGER_SURCHARGE = 0.5  # per extra passenger

MODEL_OUTPUT_PATH = os.getenv("MODEL_OUTPUT_PATH", os.path.join(os.path.dirname(__file__), "model.joblib"))


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # km
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c


def generate_synthetic_data(num_samples: int = 20000, random_state: int = 42):
    rng = np.random.default_rng(random_state)
    pickups_lat = rng.uniform(LAT_MIN, LAT_MAX, num_samples)
    pickups_lon = rng.uniform(LON_MIN, LON_MAX, num_samples)
    dropoffs_lat = rng.uniform(LAT_MIN, LAT_MAX, num_samples)
    dropoffs_lon = rng.uniform(LON_MIN, LON_MAX, num_samples)
    passenger_count = rng.integers(1, 5, num_samples)
    pickup_hours = rng.integers(0, 24, num_samples)

    distances = haversine_distance(pickups_lat, pickups_lon, dropoffs_lat, dropoffs_lon)
    # Surge multiplier based on peak hours (4-7pm)
    surge_multiplier = np.where((pickup_hours >= 16) & (pickup_hours <= 19), 1.2, 1.0)
    fares = (
        BASE_FARE
        + distances * PER_KM_RATE * surge_multiplier
        + (passenger_count - 1) * PASSENGER_SURCHARGE
    )
    # Add some noise
    noise = rng.normal(0, 2.0, num_samples)
    fares += noise

    data = pd.DataFrame(
        {
            "distance_km": distances,
            "hour_of_day": pickup_hours,
            "passenger_count": passenger_count,
            "fare": fares,
        }
    )
    return data


def train_model(df: pd.DataFrame):
    X = df[["distance_km", "hour_of_day", "passenger_count"]]
    y = df["fare"]
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X, y)
    return model


def main():
    print("[INFO] Generating synthetic dataset...")
    df = generate_synthetic_data()
    print("[INFO] Training model...")
    model = train_model(df)
    print(f"[INFO] Saving model to {MODEL_OUTPUT_PATH}...")
    joblib.dump(model, MODEL_OUTPUT_PATH)
    print("[INFO] Done!")


if __name__ == "__main__":
    main()