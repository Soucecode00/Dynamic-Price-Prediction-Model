import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';

const DemandChart = ({ data }) => {
  // Format data for the chart
  const chartData = data.map(item => ({
    ...item,
    time: new Date(item.timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    }),
    date: new Date(item.timestamp).toLocaleDateString(),
  }));

  // Get last 24 hours of data
  const last24Hours = chartData.slice(-12); // Last 12 data points (2-hour intervals)

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold">{`Time: ${label}`}</p>
          <p className="text-blue-600">{`Requests: ${data.ride_requests}`}</p>
          <p className="text-green-600">{`Drivers: ${data.active_drivers}`}</p>
          <p className="text-orange-600">{`Avg Price: $${data.average_price}`}</p>
          <p className="text-red-600">{`Surge: ${data.surge_multiplier}x`}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Demand Trends (Last 24 Hours)</h3>
      
      {/* Supply vs Demand Chart */}
      <div className="mb-8">
        <h4 className="text-md font-medium text-gray-700 mb-2">Supply vs Demand</h4>
        <ResponsiveContainer width="100%" height={250}>
          <AreaChart data={last24Hours}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="time" 
              tick={{ fontSize: 12 }}
              interval="preserveStartEnd"
            />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Area
              type="monotone"
              dataKey="ride_requests"
              stackId="1"
              stroke="#ef4444"
              fill="#ef4444"
              fillOpacity={0.6}
              name="Ride Requests"
            />
            <Area
              type="monotone"
              dataKey="active_drivers"
              stackId="2"
              stroke="#22c55e"
              fill="#22c55e"
              fillOpacity={0.6}
              name="Active Drivers"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Price and Surge Chart */}
      <div>
        <h4 className="text-md font-medium text-gray-700 mb-2">Average Price & Surge Multiplier</h4>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={last24Hours}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="time" 
              tick={{ fontSize: 12 }}
              interval="preserveStartEnd"
            />
            <YAxis 
              yAxisId="price"
              orientation="left"
              tick={{ fontSize: 12 }}
              label={{ value: 'Price ($)', angle: -90, position: 'insideLeft' }}
            />
            <YAxis 
              yAxisId="surge"
              orientation="right"
              tick={{ fontSize: 12 }}
              label={{ value: 'Surge Multiplier', angle: 90, position: 'insideRight' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              yAxisId="price"
              type="monotone"
              dataKey="average_price"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
              name="Average Price ($)"
            />
            <Line
              yAxisId="surge"
              type="monotone"
              dataKey="surge_multiplier"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={{ fill: '#f59e0b', strokeWidth: 2, r: 4 }}
              name="Surge Multiplier"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-4 border-t border-gray-200">
        <div className="text-center">
          <p className="text-2xl font-bold text-blue-600">
            ${last24Hours.length > 0 ? 
              (last24Hours.reduce((sum, item) => sum + item.average_price, 0) / last24Hours.length).toFixed(2) 
              : '0.00'}
          </p>
          <p className="text-sm text-gray-600">Avg Price (24h)</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-red-600">
            {last24Hours.length > 0 ? 
              Math.max(...last24Hours.map(item => item.surge_multiplier)).toFixed(1) 
              : '0.0'}x
          </p>
          <p className="text-sm text-gray-600">Peak Surge</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-green-600">
            {last24Hours.length > 0 ? 
              Math.max(...last24Hours.map(item => item.active_drivers))
              : '0'}
          </p>
          <p className="text-sm text-gray-600">Peak Drivers</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-orange-600">
            {last24Hours.length > 0 ? 
              Math.max(...last24Hours.map(item => item.ride_requests))
              : '0'}
          </p>
          <p className="text-sm text-gray-600">Peak Demand</p>
        </div>
      </div>
    </div>
  );
};

export default DemandChart;