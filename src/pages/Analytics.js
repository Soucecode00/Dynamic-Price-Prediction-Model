import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, ScatterPlot, Scatter
} from 'recharts';
import {
  TrendingUpIcon, TrendingDownIcon, ChartBarIcon,
  ClockIcon, MapIcon, UserGroupIcon
} from '@heroicons/react/24/outline';

const Analytics = () => {
  const [historicalData, setHistoricalData] = useState([]);
  const [timeRange, setTimeRange] = useState('7'); // days
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState({
    avgPrice: 0,
    totalRides: 0,
    peakHours: [],
    surgeAnalysis: {},
    demandPatterns: {}
  });

  useEffect(() => {
    fetchAnalyticsData();
  }, [timeRange]);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:5000/api/historical_data?days=${timeRange}`);
      const data = await response.json();
      setHistoricalData(data);
      processAnalytics(data);
    } catch (error) {
      console.error('Error fetching analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const processAnalytics = (data) => {
    if (!data.length) return;

    // Calculate basic metrics
    const avgPrice = data.reduce((sum, item) => sum + item.average_price, 0) / data.length;
    const totalRides = data.reduce((sum, item) => sum + item.ride_requests, 0);

    // Find peak hours
    const hourlyData = {};
    data.forEach(item => {
      const hour = item.hour;
      if (!hourlyData[hour]) {
        hourlyData[hour] = { requests: 0, count: 0 };
      }
      hourlyData[hour].requests += item.ride_requests;
      hourlyData[hour].count += 1;
    });

    const peakHours = Object.entries(hourlyData)
      .map(([hour, data]) => ({
        hour: parseInt(hour),
        avgRequests: data.requests / data.count
      }))
      .sort((a, b) => b.avgRequests - a.avgRequests)
      .slice(0, 3);

    // Surge analysis
    const surgeRanges = {
      low: data.filter(item => item.surge_multiplier < 1.2).length,
      medium: data.filter(item => item.surge_multiplier >= 1.2 && item.surge_multiplier < 1.5).length,
      high: data.filter(item => item.surge_multiplier >= 1.5 && item.surge_multiplier < 2.0).length,
      veryHigh: data.filter(item => item.surge_multiplier >= 2.0).length
    };

    // Demand patterns by day of week
    const demandByDay = {};
    data.forEach(item => {
      const day = item.day_of_week;
      if (!demandByDay[day]) {
        demandByDay[day] = { requests: 0, count: 0 };
      }
      demandByDay[day].requests += item.ride_requests;
      demandByDay[day].count += 1;
    });

    setAnalytics({
      avgPrice,
      totalRides,
      peakHours,
      surgeAnalysis: surgeRanges,
      demandPatterns: demandByDay
    });
  };

  const formatHour = (hour) => {
    return `${hour === 0 ? 12 : hour > 12 ? hour - 12 : hour}${hour < 12 ? 'AM' : 'PM'}`;
  };

  const getDayName = (dayIndex) => {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    return days[dayIndex];
  };

  // Prepare chart data
  const hourlyChart = Array.from({ length: 24 }, (_, hour) => {
    const hourData = historicalData.filter(item => item.hour === hour);
    return {
      hour: formatHour(hour),
      requests: hourData.length ? hourData.reduce((sum, item) => sum + item.ride_requests, 0) / hourData.length : 0,
      price: hourData.length ? hourData.reduce((sum, item) => sum + item.average_price, 0) / hourData.length : 0,
      surge: hourData.length ? hourData.reduce((sum, item) => sum + item.surge_multiplier, 0) / hourData.length : 0
    };
  });

  const dailyChart = Array.from({ length: 7 }, (_, day) => {
    const dayData = historicalData.filter(item => item.day_of_week === day);
    return {
      day: getDayName(day),
      requests: dayData.length ? dayData.reduce((sum, item) => sum + item.ride_requests, 0) / dayData.length : 0,
      drivers: dayData.length ? dayData.reduce((sum, item) => sum + item.active_drivers, 0) / dayData.length : 0,
      ratio: dayData.length ? dayData.reduce((sum, item) => sum + item.demand_supply_ratio, 0) / dayData.length : 0
    };
  });

  const surgeDistribution = [
    { name: 'Low (1.0-1.2x)', value: analytics.surgeAnalysis.low || 0, color: '#22c55e' },
    { name: 'Medium (1.2-1.5x)', value: analytics.surgeAnalysis.medium || 0, color: '#eab308' },
    { name: 'High (1.5-2.0x)', value: analytics.surgeAnalysis.high || 0, color: '#f97316' },
    { name: 'Very High (2.0x+)', value: analytics.surgeAnalysis.veryHigh || 0, color: '#ef4444' }
  ];

  const priceVsDemand = historicalData.map(item => ({
    demand: item.ride_requests,
    price: item.average_price,
    surge: item.surge_multiplier
  }));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700">Time Range:</label>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="1">Last 24 hours</option>
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
          </select>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Average Price</p>
              <p className="text-3xl font-bold text-gray-900">${analytics.avgPrice.toFixed(2)}</p>
            </div>
            <ChartBarIcon className="h-12 w-12 text-blue-500" />
          </div>
          <div className="mt-2 flex items-center text-sm">
            <TrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-green-600">12% vs last period</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Requests</p>
              <p className="text-3xl font-bold text-gray-900">{analytics.totalRides.toLocaleString()}</p>
            </div>
            <UserGroupIcon className="h-12 w-12 text-green-500" />
          </div>
          <div className="mt-2 flex items-center text-sm">
            <TrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-green-600">8% vs last period</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-orange-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Peak Hour</p>
              <p className="text-3xl font-bold text-gray-900">
                {analytics.peakHours.length > 0 ? formatHour(analytics.peakHours[0].hour) : 'N/A'}
              </p>
            </div>
            <ClockIcon className="h-12 w-12 text-orange-500" />
          </div>
          <div className="mt-2 flex items-center text-sm">
            <span className="text-gray-600">
              {analytics.peakHours.length > 0 ? `${analytics.peakHours[0].avgRequests.toFixed(0)} avg requests` : 'No data'}
            </span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-red-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">High Surge %</p>
              <p className="text-3xl font-bold text-gray-900">
                {historicalData.length > 0 
                  ? (((analytics.surgeAnalysis.high || 0) + (analytics.surgeAnalysis.veryHigh || 0)) / historicalData.length * 100).toFixed(1)
                  : 0}%
              </p>
            </div>
            <MapIcon className="h-12 w-12 text-red-500" />
          </div>
          <div className="mt-2 flex items-center text-sm">
            <TrendingDownIcon className="h-4 w-4 text-red-500 mr-1" />
            <span className="text-red-600">3% vs last period</span>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Hourly Demand Pattern */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Hourly Demand Pattern</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={hourlyChart}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Area
                type="monotone"
                dataKey="requests"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.6}
                name="Ride Requests"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Daily Supply vs Demand */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Supply vs Demand</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={dailyChart}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="requests" fill="#ef4444" name="Requests" />
              <Bar dataKey="drivers" fill="#22c55e" name="Drivers" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Surge Distribution */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Surge Pricing Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={surgeDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {surgeDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Price vs Demand Correlation */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Price vs Demand Correlation</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={priceVsDemand.slice(-20)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="demand" name="Demand" />
              <YAxis dataKey="price" name="Price" />
              <Tooltip 
                formatter={(value, name) => [
                  name === 'price' ? `$${value.toFixed(2)}` : value,
                  name === 'price' ? 'Price' : 'Demand'
                ]}
              />
              <Line type="monotone" dataKey="price" stroke="#f59e0b" strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Peak Hours Analysis */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Peak Hours Analysis</h3>
          <div className="space-y-4">
            {analytics.peakHours.map((peak, index) => (
              <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <div>
                  <span className="font-medium text-gray-900">
                    #{index + 1} Peak: {formatHour(peak.hour)}
                  </span>
                  <p className="text-sm text-gray-600">
                    Average {peak.avgRequests.toFixed(1)} requests/hour
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-blue-600">
                    {peak.avgRequests.toFixed(0)}
                  </div>
                  <div className="text-xs text-gray-500">requests</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Market Insights */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Insights</h3>
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
              <h4 className="font-medium text-blue-900">Demand Pattern</h4>
              <p className="text-sm text-blue-700 mt-1">
                Peak demand occurs during {analytics.peakHours.length > 0 ? formatHour(analytics.peakHours[0].hour) : 'rush hours'}, 
                with an average of {analytics.peakHours.length > 0 ? analytics.peakHours[0].avgRequests.toFixed(0) : 'N/A'} requests per hour.
              </p>
            </div>
            
            <div className="p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
              <h4 className="font-medium text-green-900">Pricing Efficiency</h4>
              <p className="text-sm text-green-700 mt-1">
                {((analytics.surgeAnalysis.low || 0) / Math.max(historicalData.length, 1) * 100).toFixed(0)}% 
                of rides operate at standard pricing, indicating good supply-demand balance.
              </p>
            </div>
            
            <div className="p-4 bg-orange-50 rounded-lg border-l-4 border-orange-500">
              <h4 className="font-medium text-orange-900">Revenue Opportunity</h4>
              <p className="text-sm text-orange-700 mt-1">
                High surge periods represent {((analytics.surgeAnalysis.high || 0) + (analytics.surgeAnalysis.veryHigh || 0))} 
                data points with potential for optimized driver positioning.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;