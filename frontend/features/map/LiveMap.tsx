'use client';

import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import 'leaflet/dist/leaflet.css';
import { useIncidentStore } from '@/shared/stores/incident-store';
import { useEffect } from 'react';
import L from 'leaflet';

// Фикс иконок Leaflet в Next.js
const icon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

const redIcon = L.divIcon({
  className: 'custom-div-icon',
  html: "<div style='background-color:#ef4444; width:16px; height:16px; border-radius:50%; border:2px solid white; box-shadow: 0 0 10px rgba(239,68,68,0.6);'></div>",
  iconSize: [16, 16],
  iconAnchor: [8, 8],
});

// Функция для создания красивой иконки кластера
const createClusterCustomIcon = function (cluster: any) {
  return L.divIcon({
    html: `<div class="flex items-center justify-center w-full h-full bg-slate-800 border-2 border-slate-600 rounded-full text-white font-bold shadow-xl">
            ${cluster.getChildCount()}
           </div>`,
    className: 'custom-marker-cluster',
    iconSize: L.point(33, 33, true),
  });
};

// Компонент для управления зумом при выборе инцидента
function MapController() {
  const map = useMap();
  const { activeIncidentId, incidents } = useIncidentStore();

  useEffect(() => {
    if (activeIncidentId) {
      const incident = incidents.get(activeIncidentId);
      if (incident) {
        map.flyTo([incident.lat, incident.lon], 16, { duration: 1.5 });
      }
    }
  }, [activeIncidentId, incidents, map]);
  return null;
}

export default function LiveMap() {
  const { getSortedIncidents, setActiveIncidentId } = useIncidentStore();
  const incidents = getSortedIncidents();

  return (
    <MapContainer
      center={[41.311, 69.240]}
      zoom={12}
      style={{ height: '100%', width: '100%', background: '#0f172a' }}
    >
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        className="map-tiles-dark"
      />

      <MapController />

      {/* Оборачиваем маркеры в кластер */}
      <MarkerClusterGroup
        chunkedLoading
        iconCreateFunction={createClusterCustomIcon}
        spiderfyOnMaxZoom={true}
        showCoverageOnHover={false}
      >
        {incidents.map((incident) => (
          <Marker
            key={incident.event_uid}
            position={[incident.lat, incident.lon]}
            icon={redIcon}
            eventHandlers={{
              click: () => setActiveIncidentId(incident.event_uid),
            }}
          >
            <Popup className="custom-popup">
              <div className="text-slate-900 min-w-[150px]">
                <div className="flex justify-between items-center mb-2">
                    <strong className="text-red-600 text-sm">{incident.detected_type}</strong>
                    <span className="text-xs bg-slate-200 px-1 rounded">Sev: {incident.severity}</span>
                </div>
                <div className="text-sm font-medium">{incident.user.phone_number}</div>
                <div className="text-xs text-slate-500 mt-1">
                    {new Date(incident.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MarkerClusterGroup>
    </MapContainer>
  );
}