from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os
import math
from datetime import datetime

class FareRequest(BaseModel):
    pickup_lat: float
    pickup_lon: float
    dropoff_lat: float
    dropoff_lon: float
    passenger_count: int = 1
    pickup_datetime: datetime | None = None

class FareResponse(BaseModel):
    predicted_fare: float

app = FastAPI(title="Taxi Fare Prediction API")

MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(os.path.dirname(__file__), "model.joblib"))

# Load model once at startup
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    model = None
    print(f"[WARN] Model file not found at {MODEL_PATH}. Make sure to train the model first.")


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth."""
    R = 6371  # Earth radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def build_feature_vector(req: FareRequest):
    distance_km = haversine_distance(req.pickup_lat, req.pickup_lon, req.dropoff_lat, req.dropoff_lon)
    if req.pickup_datetime:
        hour_of_day = req.pickup_datetime.hour
    else:
        hour_of_day = datetime.utcnow().hour
    return [[distance_km, hour_of_day, req.passenger_count]]


@app.post("/predict", response_model=FareResponse)
def predict_fare(req: FareRequest):
    """Predict taxi fare based on trip parameters."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not available. Train the model first.")

    features = build_feature_vector(req)
    fare = float(model.predict(features)[0])
    return FareResponse(predicted_fare=round(fare, 2))