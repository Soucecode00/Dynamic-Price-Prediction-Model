import React from 'react';
import { 
  TruckIcon, 
  UserGroupIcon, 
  BoltIcon, 
  CloudIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

const MarketOverview = ({ marketData }) => {
  const cards = [
    {
      title: 'Active Drivers',
      value: marketData.active_drivers,
      icon: TruckIcon,
      color: 'blue',
      suffix: '',
      trend: marketData.active_drivers > 100 ? 'up' : 'down'
    },
    {
      title: 'Ride Requests',
      value: marketData.ride_requests,
      icon: UserGroupIcon,
      color: 'green',
      suffix: '',
      trend: marketData.ride_requests > 40 ? 'up' : 'down'
    },
    {
      title: 'Surge Multiplier',
      value: marketData.surge_multiplier,
      icon: BoltIcon,
      color: marketData.surge_multiplier > 1.5 ? 'red' : marketData.surge_multiplier > 1.2 ? 'yellow' : 'green',
      suffix: 'x',
      trend: marketData.surge_multiplier > 1.2 ? 'up' : 'down'
    },
    {
      title: 'Weather Factor',
      value: marketData.weather_factor,
      icon: CloudIcon,
      color: marketData.weather_factor > 1.2 ? 'orange' : 'blue',
      suffix: 'x',
      trend: marketData.weather_factor > 1.1 ? 'up' : 'down'
    },
    {
      title: 'Traffic Factor',
      value: marketData.traffic_factor,
      icon: ClockIcon,
      color: marketData.traffic_factor > 1.4 ? 'red' : 'blue',
      suffix: 'x',
      trend: marketData.traffic_factor > 1.3 ? 'up' : 'down'
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-50 text-blue-600 border-blue-200',
      green: 'bg-green-50 text-green-600 border-green-200',
      red: 'bg-red-50 text-red-600 border-red-200',
      yellow: 'bg-yellow-50 text-yellow-600 border-yellow-200',
      orange: 'bg-orange-50 text-orange-600 border-orange-200'
    };
    return colors[color] || colors.blue;
  };

  const getTrendIcon = (trend) => {
    if (trend === 'up') {
      return (
        <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 17l9.2-9.2M17 17V7H7" />
        </svg>
      );
    }
    return (
      <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 7l-9.2 9.2M7 7v10h10" />
      </svg>
    );
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      {cards.map((card, index) => {
        const Icon = card.icon;
        return (
          <div
            key={index}
            className={`bg-white p-6 rounded-lg shadow border-l-4 ${getColorClasses(card.color)}`}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">
                  {card.title}
                </p>
                <div className="flex items-center">
                  <p className="text-2xl font-bold text-gray-900">
                    {typeof card.value === 'number' ? card.value.toFixed(card.suffix === 'x' ? 1 : 0) : card.value}
                    {card.suffix}
                  </p>
                  <div className="ml-2">
                    {getTrendIcon(card.trend)}
                  </div>
                </div>
              </div>
              <div className={`p-3 rounded-full ${getColorClasses(card.color)}`}>
                <Icon className="w-6 h-6" />
              </div>
            </div>
            <div className="mt-2">
              <p className="text-xs text-gray-500">
                Updated: {new Date(marketData.timestamp).toLocaleTimeString()}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default MarketOverview;