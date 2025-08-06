import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import MarketOverview from '../components/MarketOverview';
import SurgeMap from '../components/SurgeMap';
import DemandChart from '../components/DemandChart';
import EventsPanel from '../components/EventsPanel';

const Dashboard = () => {
  const [marketData, setMarketData] = useState({
    active_drivers: 150,
    ride_requests: 45,
    surge_multiplier: 1.0,
    weather_factor: 1.0,
    traffic_factor: 1.0,
    weather_condition: 'clear',
    demand_supply_ratio: 0.3,
    timestamp: new Date().toISOString()
  });

  const [historicalData, setHistoricalData] = useState([]);
  const [surgeZones, setSurgeZones] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Initialize socket connection
    const socket = io('http://localhost:5000');

    socket.on('connect', () => {
      setIsConnected(true);
      console.log('Connected to real-time updates');
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
      console.log('Disconnected from real-time updates');
    });

    socket.on('market_update', (data) => {
      setMarketData(data);
    });

    // Fetch initial data
    fetchHistoricalData();
    fetchSurgeZones();

    // Update surge zones every 30 seconds
    const surgeInterval = setInterval(fetchSurgeZones, 30000);

    return () => {
      socket.disconnect();
      clearInterval(surgeInterval);
    };
  }, []);

  const fetchHistoricalData = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/historical_data?days=1');
      const data = await response.json();
      setHistoricalData(data);
    } catch (error) {
      console.error('Error fetching historical data:', error);
    }
  };

  const fetchSurgeZones = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/surge_zones');
      const data = await response.json();
      setSurgeZones(data);
    } catch (error) {
      console.error('Error fetching surge zones:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Real-Time Dashboard</h1>
        <div className="flex items-center space-x-2">
          <div className={`h-3 w-3 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
          <span className="text-sm text-gray-600">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Market Overview Cards */}
      <MarketOverview marketData={marketData} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Surge Map */}
        <div className="lg:col-span-2">
          <SurgeMap zones={surgeZones} />
        </div>

        {/* Events Panel */}
        <div className="lg:col-span-1">
          <EventsPanel marketData={marketData} />
        </div>
      </div>

      {/* Demand Chart */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <DemandChart data={historicalData} />
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Price Factors</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm text-gray-600">Weather Impact</span>
                <span className="text-sm font-medium">{marketData.weather_factor}x</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full" 
                  style={{ width: `${Math.min(100, (marketData.weather_factor - 0.8) / 0.8 * 100)}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm text-gray-600">Traffic Impact</span>
                <span className="text-sm font-medium">{marketData.traffic_factor}x</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-orange-600 h-2 rounded-full" 
                  style={{ width: `${Math.min(100, (marketData.traffic_factor - 0.8) / 1.7 * 100)}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm text-gray-600">Demand/Supply Ratio</span>
                <span className="text-sm font-medium">{marketData.demand_supply_ratio}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-red-600 h-2 rounded-full" 
                  style={{ width: `${Math.min(100, marketData.demand_supply_ratio * 100)}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;