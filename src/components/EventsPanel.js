import React, { useState, useEffect } from 'react';
import {
  ExclamationTriangleIcon,
  ClockIcon,
  CloudIcon,
  TruckIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

const EventsPanel = ({ marketData }) => {
  const [events, setEvents] = useState([]);
  const [forecast, setForecast] = useState([]);

  useEffect(() => {
    // Generate some mock events based on market data
    generateEvents();
    generateForecast();
  }, [marketData]);

  const generateEvents = () => {
    const currentEvents = [];

    // Weather-based events
    if (marketData.weather_factor > 1.3) {
      currentEvents.push({
        id: 'weather-1',
        type: 'weather',
        title: 'Severe Weather Alert',
        description: 'Poor weather conditions increasing demand',
        impact: 'High',
        severity: 'warning',
        timestamp: new Date().toISOString(),
        icon: CloudIcon
      });
    }

    // Traffic-based events
    if (marketData.traffic_factor > 1.5) {
      currentEvents.push({
        id: 'traffic-1',
        type: 'traffic',
        title: 'Heavy Traffic Conditions',
        description: 'Traffic congestion affecting ride times',
        impact: 'Medium',
        severity: 'info',
        timestamp: new Date().toISOString(),
        icon: ClockIcon
      });
    }

    // Surge-based events
    if (marketData.surge_multiplier > 1.8) {
      currentEvents.push({
        id: 'surge-1',
        type: 'surge',
        title: 'High Surge Pricing',
        description: `Current surge multiplier: ${marketData.surge_multiplier}x`,
        impact: 'High',
        severity: 'error',
        timestamp: new Date().toISOString(),
        icon: ExclamationTriangleIcon
      });
    }

    // Supply/demand imbalance
    if (marketData.demand_supply_ratio > 0.8) {
      currentEvents.push({
        id: 'demand-1',
        type: 'demand',
        title: 'High Demand Period',
        description: 'Ride requests significantly exceeding driver availability',
        impact: 'High',
        severity: 'warning',
        timestamp: new Date().toISOString(),
        icon: TruckIcon
      });
    }

    // Random events (simulating real-world events)
    if (Math.random() < 0.3) {
      const randomEvents = [
        {
          id: 'event-1',
          type: 'event',
          title: 'Concert at Madison Square Garden',
          description: 'Large event ending, expect increased demand',
          impact: 'Medium',
          severity: 'info',
          timestamp: new Date().toISOString(),
          icon: ChartBarIcon
        },
        {
          id: 'event-2',
          type: 'event',
          title: 'Airport Flight Delays',
          description: 'Multiple flight delays increasing airport rides',
          impact: 'Medium',
          severity: 'warning',
          timestamp: new Date().toISOString(),
          icon: ClockIcon
        }
      ];
      
      currentEvents.push(randomEvents[Math.floor(Math.random() * randomEvents.length)]);
    }

    setEvents(currentEvents);
  };

  const generateForecast = () => {
    const now = new Date();
    const forecastData = [];

    for (let i = 1; i <= 6; i++) {
      const futureTime = new Date(now.getTime() + i * 60 * 60 * 1000);
      const hour = futureTime.getHours();
      
      // Predict surge based on hour patterns
      let predictedSurge = 1.0;
      if ((hour >= 7 && hour <= 9) || (hour >= 17 && hour <= 19)) {
        predictedSurge = 1.4 + Math.random() * 0.4;
      } else if (hour >= 22 || hour <= 5) {
        predictedSurge = 1.2 + Math.random() * 0.3;
      } else {
        predictedSurge = 1.0 + Math.random() * 0.2;
      }

      forecastData.push({
        time: futureTime.toLocaleTimeString('en-US', { 
          hour: '2-digit', 
          minute: '2-digit',
          hour12: false 
        }),
        surge: predictedSurge.toFixed(1),
        confidence: Math.max(0.6, 1 - (i * 0.05)), // Decreasing confidence
        trend: predictedSurge > marketData.surge_multiplier ? 'up' : 'down'
      });
    }

    setForecast(forecastData);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'error':
        return 'border-red-200 bg-red-50 text-red-800';
      case 'warning':
        return 'border-yellow-200 bg-yellow-50 text-yellow-800';
      case 'info':
        return 'border-blue-200 bg-blue-50 text-blue-800';
      default:
        return 'border-gray-200 bg-gray-50 text-gray-800';
    }
  };

  const getTrendIcon = (trend) => {
    if (trend === 'up') {
      return (
        <svg className="w-3 h-3 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 17l9.2-9.2M17 17V7H7" />
        </svg>
      );
    }
    return (
      <svg className="w-3 h-3 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 7l-9.2 9.2M7 7v10h10" />
      </svg>
    );
  };

  return (
    <div className="space-y-6">
      {/* Active Events */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Events</h3>
        <div className="space-y-3">
          {events.length > 0 ? (
            events.map((event) => {
              const Icon = event.icon;
              return (
                <div
                  key={event.id}
                  className={`p-3 rounded-lg border ${getSeverityColor(event.severity)}`}
                >
                  <div className="flex items-start">
                    <Icon className="h-5 w-5 mt-0.5 mr-3 flex-shrink-0" />
                    <div className="flex-1">
                      <div className="flex justify-between items-start">
                        <h4 className="font-medium">{event.title}</h4>
                        <span className="text-xs bg-white bg-opacity-60 px-2 py-1 rounded">
                          {event.impact}
                        </span>
                      </div>
                      <p className="text-sm mt-1 opacity-90">
                        {event.description}
                      </p>
                      <p className="text-xs mt-2 opacity-75">
                        {new Date(event.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="text-center py-4 text-gray-500">
              <ChartBarIcon className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No active events</p>
            </div>
          )}
        </div>
      </div>

      {/* Surge Forecast */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Surge Forecast</h3>
        <div className="space-y-3">
          {forecast.map((item, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <ClockIcon className="h-4 w-4 text-gray-500 mr-2" />
                <span className="text-sm font-medium">{item.time}</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-semibold">{item.surge}x</span>
                {getTrendIcon(item.trend)}
                <span className="text-xs text-gray-500">
                  {Math.round(item.confidence * 100)}%
                </span>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-xs text-blue-700">
            <strong>Note:</strong> Forecasts are based on historical patterns and current market conditions. 
            Confidence decreases for longer time periods.
          </p>
        </div>
      </div>

      {/* Market Status */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Status</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Supply Level</span>
            <span className={`text-sm font-semibold ${
              marketData.active_drivers > 150 ? 'text-green-600' : 
              marketData.active_drivers > 100 ? 'text-yellow-600' : 'text-red-600'
            }`}>
              {marketData.active_drivers > 150 ? 'High' : 
               marketData.active_drivers > 100 ? 'Medium' : 'Low'}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Demand Level</span>
            <span className={`text-sm font-semibold ${
              marketData.ride_requests > 60 ? 'text-red-600' : 
              marketData.ride_requests > 40 ? 'text-yellow-600' : 'text-green-600'
            }`}>
              {marketData.ride_requests > 60 ? 'High' : 
               marketData.ride_requests > 40 ? 'Medium' : 'Low'}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Market Balance</span>
            <span className={`text-sm font-semibold ${
              marketData.demand_supply_ratio > 0.7 ? 'text-red-600' : 
              marketData.demand_supply_ratio > 0.4 ? 'text-yellow-600' : 'text-green-600'
            }`}>
              {marketData.demand_supply_ratio > 0.7 ? 'Imbalanced' : 
               marketData.demand_supply_ratio > 0.4 ? 'Tight' : 'Balanced'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EventsPanel;