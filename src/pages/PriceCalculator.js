import React, { useState, useEffect } from 'react';
import { MapPinIcon, ClockIcon, CurrencyDollarIcon } from '@heroicons/react/24/outline';

const PriceCalculator = () => {
  const [formData, setFormData] = useState({
    pickup_lat: 40.7128,
    pickup_lng: -74.0060,
    dropoff_lat: 40.7589,
    dropoff_lng: -73.9851,
    ride_type: 'standard'
  });

  const [prediction, setPrediction] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const rideTypes = [
    { id: 'economy', name: 'Economy', description: 'Affordable rides', multiplier: 0.8 },
    { id: 'standard', name: 'Standard', description: 'Standard comfort', multiplier: 1.0 },
    { id: 'premium', name: 'Premium', description: 'Extra comfort', multiplier: 1.3 },
    { id: 'luxury', name: 'Luxury', description: 'Luxury vehicles', multiplier: 1.8 }
  ];

  const presetLocations = {
    'Manhattan Midtown': { lat: 40.7549, lng: -73.9840 },
    'JFK Airport': { lat: 40.6413, lng: -73.7781 },
    'LaGuardia Airport': { lat: 40.7769, lng: -73.8740 },
    'Brooklyn Bridge': { lat: 40.7061, lng: -73.9969 },
    'Central Park': { lat: 40.7812, lng: -73.9665 },
    'Times Square': { lat: 40.7580, lng: -73.9855 },
    'Financial District': { lat: 40.7074, lng: -74.0113 },
    'Williamsburg': { lat: 40.7081, lng: -73.9571 }
  };

  useEffect(() => {
    // Auto-calculate when form changes
    if (formData.pickup_lat && formData.pickup_lng && formData.dropoff_lat && formData.dropoff_lng) {
      calculatePrice();
    }
  }, [formData]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: parseFloat(value) || value
    }));
  };

  const setPresetLocation = (type, locationName) => {
    const location = presetLocations[locationName];
    setFormData(prev => ({
      ...prev,
      [`${type}_lat`]: location.lat,
      [`${type}_lng`]: location.lng
    }));
  };

  const calculatePrice = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/api/predict_price', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error('Failed to calculate price');
      }

      const data = await response.json();
      
      // Apply ride type multiplier
      const rideTypeMultiplier = rideTypes.find(rt => rt.id === formData.ride_type)?.multiplier || 1.0;
      const adjustedData = {
        ...data,
        predicted_price: data.predicted_price * rideTypeMultiplier,
        breakdown: {
          ...data.breakdown,
          ride_type_adjustment: (data.predicted_price * rideTypeMultiplier) - data.predicted_price
        }
      };

      setPrediction(adjustedData);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const swapLocations = () => {
    setFormData(prev => ({
      ...prev,
      pickup_lat: prev.dropoff_lat,
      pickup_lng: prev.dropoff_lng,
      dropoff_lat: prev.pickup_lat,
      dropoff_lng: prev.pickup_lng
    }));
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Price Calculator</h1>
        <p className="mt-2 text-gray-600">Get instant price predictions for your ride</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Trip Details</h2>
          
          {/* Pickup Location */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <MapPinIcon className="h-4 w-4 inline mr-1" />
              Pickup Location
            </label>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <input
                  type="number"
                  name="pickup_lat"
                  value={formData.pickup_lat}
                  onChange={handleInputChange}
                  placeholder="Latitude"
                  step="any"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <input
                  type="number"
                  name="pickup_lng"
                  value={formData.pickup_lng}
                  onChange={handleInputChange}
                  placeholder="Longitude"
                  step="any"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <div className="mt-2">
              <select
                onChange={(e) => e.target.value && setPresetLocation('pickup', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                defaultValue=""
              >
                <option value="">Select preset location</option>
                {Object.keys(presetLocations).map(location => (
                  <option key={location} value={location}>{location}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Swap Button */}
          <div className="flex justify-center mb-6">
            <button
              onClick={swapLocations}
              className="p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
              title="Swap pickup and dropoff"
            >
              <svg className="h-5 w-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
              </svg>
            </button>
          </div>

          {/* Dropoff Location */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <MapPinIcon className="h-4 w-4 inline mr-1" />
              Dropoff Location
            </label>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <input
                  type="number"
                  name="dropoff_lat"
                  value={formData.dropoff_lat}
                  onChange={handleInputChange}
                  placeholder="Latitude"
                  step="any"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <input
                  type="number"
                  name="dropoff_lng"
                  value={formData.dropoff_lng}
                  onChange={handleInputChange}
                  placeholder="Longitude"
                  step="any"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <div className="mt-2">
              <select
                onChange={(e) => e.target.value && setPresetLocation('dropoff', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                defaultValue=""
              >
                <option value="">Select preset location</option>
                {Object.keys(presetLocations).map(location => (
                  <option key={location} value={location}>{location}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Ride Type */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">Ride Type</label>
            <div className="grid grid-cols-2 gap-3">
              {rideTypes.map(type => (
                <label
                  key={type.id}
                  className={`relative flex cursor-pointer rounded-lg p-4 border ${
                    formData.ride_type === type.id
                      ? 'bg-blue-50 border-blue-500 ring-2 ring-blue-500'
                      : 'bg-white border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <input
                    type="radio"
                    name="ride_type"
                    value={type.id}
                    checked={formData.ride_type === type.id}
                    onChange={handleInputChange}
                    className="sr-only"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{type.name}</div>
                    <div className="text-sm text-gray-500">{type.description}</div>
                    <div className="text-xs text-gray-400">{type.multiplier}x multiplier</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <button
            onClick={calculatePrice}
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'Calculating...' : 'Calculate Price'}
          </button>
        </div>

        {/* Results */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Price Prediction</h2>
          
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
              <p className="text-red-800">Error: {error}</p>
            </div>
          )}

          {prediction ? (
            <div className="space-y-6">
              {/* Main Price */}
              <div className="text-center p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg">
                <div className="flex items-center justify-center mb-2">
                  <CurrencyDollarIcon className="h-8 w-8 text-blue-600 mr-2" />
                  <span className="text-4xl font-bold text-blue-600">
                    ${prediction.predicted_price.toFixed(2)}
                  </span>
                </div>
                <p className="text-gray-600">Estimated ride cost</p>
                {prediction.surge_multiplier > 1.0 && (
                  <div className="mt-2 inline-flex items-center px-3 py-1 rounded-full text-sm bg-orange-100 text-orange-800">
                    Surge pricing: {prediction.surge_multiplier}x
                  </div>
                )}
              </div>

              {/* Trip Info */}
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-center mb-1">
                    <MapPinIcon className="h-5 w-5 text-gray-500 mr-1" />
                    <span className="font-semibold">{prediction.distance} mi</span>
                  </div>
                  <p className="text-sm text-gray-600">Distance</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-center mb-1">
                    <ClockIcon className="h-5 w-5 text-gray-500 mr-1" />
                    <span className="font-semibold">{prediction.estimated_time} min</span>
                  </div>
                  <p className="text-sm text-gray-600">Est. Time</p>
                </div>
              </div>

              {/* Price Breakdown */}
              <div className="space-y-3">
                <h3 className="font-semibold text-gray-900">Price Breakdown</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Base fare</span>
                    <span className="font-medium">${prediction.breakdown.base_fare.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Distance cost</span>
                    <span className="font-medium">${prediction.breakdown.distance_cost.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Time cost</span>
                    <span className="font-medium">${prediction.breakdown.time_cost.toFixed(2)}</span>
                  </div>
                  {prediction.breakdown.surge_adjustment > 0 && (
                    <div className="flex justify-between text-orange-600">
                      <span>Surge adjustment</span>
                      <span className="font-medium">+${prediction.breakdown.surge_adjustment.toFixed(2)}</span>
                    </div>
                  )}
                  {prediction.breakdown.ride_type_adjustment > 0 && (
                    <div className="flex justify-between text-blue-600">
                      <span>Ride type adjustment</span>
                      <span className="font-medium">+${prediction.breakdown.ride_type_adjustment.toFixed(2)}</span>
                    </div>
                  )}
                  <div className="border-t pt-2 flex justify-between font-semibold">
                    <span>Total</span>
                    <span>${prediction.predicted_price.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              {/* Market Factors */}
              <div className="space-y-3">
                <h3 className="font-semibold text-gray-900">Market Factors</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="p-3 bg-gray-50 rounded">
                    <div className="font-medium text-gray-700">Demand</div>
                    <div className={`text-sm ${
                      prediction.factors.demand_level === 'High' ? 'text-red-600' :
                      prediction.factors.demand_level === 'Medium' ? 'text-yellow-600' : 'text-green-600'
                    }`}>
                      {prediction.factors.demand_level}
                    </div>
                  </div>
                  <div className="p-3 bg-gray-50 rounded">
                    <div className="font-medium text-gray-700">Supply</div>
                    <div className={`text-sm ${
                      prediction.factors.supply_level === 'Low' ? 'text-red-600' :
                      prediction.factors.supply_level === 'Medium' ? 'text-yellow-600' : 'text-green-600'
                    }`}>
                      {prediction.factors.supply_level}
                    </div>
                  </div>
                  <div className="p-3 bg-gray-50 rounded">
                    <div className="font-medium text-gray-700">Weather</div>
                    <div className="text-sm text-gray-600">{prediction.factors.weather_impact}x</div>
                  </div>
                  <div className="p-3 bg-gray-50 rounded">
                    <div className="font-medium text-gray-700">Traffic</div>
                    <div className="text-sm text-gray-600">{prediction.factors.traffic_impact}x</div>
                  </div>
                </div>
              </div>

              {/* Recommendations */}
              <div className="p-4 bg-blue-50 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">💡 Price Optimization Tips</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  {prediction.surge_multiplier > 1.5 && (
                    <li>• Consider waiting a bit - surge pricing is currently high</li>
                  )}
                  {prediction.factors.demand_level === 'High' && (
                    <li>• High demand period - try nearby pickup points</li>
                  )}
                  {prediction.factors.traffic_impact > 1.3 && (
                    <li>• Heavy traffic detected - expect longer ride times</li>
                  )}
                  <li>• Peak hours typically have higher prices (7-9 AM, 5-7 PM)</li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <CurrencyDollarIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Enter trip details to see price prediction</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PriceCalculator;