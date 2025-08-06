import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const SurgeMap = ({ zones }) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const layersRef = useRef([]);

  useEffect(() => {
    if (!mapInstanceRef.current) {
      // Initialize map
      mapInstanceRef.current = L.map(mapRef.current).setView([40.7128, -74.0060], 11);

      // Add OpenStreetMap tiles
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(mapInstanceRef.current);
    }

    return () => {
      // Cleanup function
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!mapInstanceRef.current || !zones.length) return;

    // Clear existing layers
    layersRef.current.forEach(layer => {
      mapInstanceRef.current.removeLayer(layer);
    });
    layersRef.current = [];

    // Add surge zones
    zones.forEach(zone => {
      // Create polygon for surge zone
      const polygon = L.polygon(zone.polygon, {
        color: zone.color,
        fillColor: zone.color,
        fillOpacity: 0.3,
        weight: 2
      });

      // Add popup with zone information
      polygon.bindPopup(`
        <div class="p-2">
          <h3 class="font-bold text-lg">${zone.name}</h3>
          <div class="mt-2 space-y-1">
            <p><strong>Surge:</strong> ${zone.surge_multiplier}x</p>
            <p><strong>Active Drivers:</strong> ${zone.active_drivers}</p>
            <p><strong>Ride Requests:</strong> ${zone.ride_requests}</p>
          </div>
        </div>
      `);

      // Add marker at center
      const marker = L.marker(zone.center)
        .bindPopup(`
          <div class="text-center p-2">
            <h3 class="font-bold">${zone.name}</h3>
            <p class="text-xl font-bold" style="color: ${zone.color}">
              ${zone.surge_multiplier}x
            </p>
          </div>
        `);

      polygon.addTo(mapInstanceRef.current);
      marker.addTo(mapInstanceRef.current);

      layersRef.current.push(polygon, marker);
    });
  }, [zones]);

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Surge Pricing Zones</h3>
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded mr-1"></div>
            <span>Low (1.0-1.2x)</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-yellow-500 rounded mr-1"></div>
            <span>Medium (1.2-1.5x)</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-orange-500 rounded mr-1"></div>
            <span>High (1.5-2.0x)</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-red-500 rounded mr-1"></div>
            <span>Very High (2.0x+)</span>
          </div>
        </div>
      </div>
      <div 
        ref={mapRef} 
        className="w-full h-96 rounded-lg border border-gray-200"
        style={{ minHeight: '400px' }}
      />
      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div className="text-center">
          <p className="font-semibold text-gray-900">
            {zones.reduce((sum, zone) => sum + zone.active_drivers, 0)}
          </p>
          <p className="text-gray-600">Total Drivers</p>
        </div>
        <div className="text-center">
          <p className="font-semibold text-gray-900">
            {zones.reduce((sum, zone) => sum + zone.ride_requests, 0)}
          </p>
          <p className="text-gray-600">Total Requests</p>
        </div>
        <div className="text-center">
          <p className="font-semibold text-gray-900">
            {zones.length > 0 ? (zones.reduce((sum, zone) => sum + zone.surge_multiplier, 0) / zones.length).toFixed(1) : 0}x
          </p>
          <p className="text-gray-600">Avg Surge</p>
        </div>
        <div className="text-center">
          <p className="font-semibold text-gray-900">
            {zones.filter(zone => zone.surge_multiplier > 1.5).length}
          </p>
          <p className="text-gray-600">High Surge Zones</p>
        </div>
      </div>
    </div>
  );
};

export default SurgeMap;