'use client';

import dynamic from 'next/dynamic';
import { useEffect } from 'react';
import { Radio, AlertTriangle, User, Battery, MapPin, CheckCircle } from 'lucide-react';
import { useOpsSocket } from '@/features/realtime/use-socket';
import { useIncidentStore } from '@/shared/stores/incident-store';
import { incidentApi } from '@/shared/api/incidents';
import IncidentDetailsPanel from '@/features/incidents/IncidentDetailsPanel';

// Динамический импорт карты (отключает SSR, так как Leaflet требует window)
const LiveMap = dynamic(() => import('@/features/map/LiveMap'), {
  ssr: false,
  loading: () => (
    <div className="h-full w-full flex items-center justify-center bg-slate-900 text-slate-500">
      Загрузка карты...
    </div>
  ),
});

export default function LivePage() {
  // Подключаем WebSocket
  const { readyState } = useOpsSocket();

  // Подключаем Store
  const {
    getSortedIncidents,
    setActiveIncidentId,
    activeIncidentId,
    setIncidents
  } = useIncidentStore();

  const incidents = getSortedIncidents();

  // Загрузка начальных данных при открытии страницы
  useEffect(() => {
    const fetchActive = async () => {
      try {
        const data = await incidentApi.getActive();
        setIncidents(data);
      } catch (e) {
        console.error("Failed to fetch initial incidents", e);
      }
    };
    fetchActive();
  }, [setIncidents]);

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden relative">

      {/* ЛЕВАЯ ПАНЕЛЬ: Список инцидентов */}
      <aside className="w-96 border-r border-slate-800 flex flex-col z-10 bg-slate-900/95 backdrop-blur shadow-2xl h-full">

        {/* Хедер списка */}
        <header className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900 shrink-0">
          <div className="flex items-center gap-2">
            <Radio className={`h-5 w-5 ${readyState === 1 ? 'text-green-500 animate-pulse' : 'text-red-500'}`} />
            <span className="font-bold tracking-wider text-sm">LIVE MONITOR</span>
          </div>
          <span className="text-xs font-mono text-slate-500 bg-slate-800 px-2 py-1 rounded">
            {incidents.length} ACTIVE
          </span>
        </header>

        {/* Список */}
        <div className="flex-1 overflow-y-auto p-2 space-y-2">
          {incidents.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-slate-600 gap-3">
              <div className="h-16 w-16 rounded-full border-2 border-slate-800 flex items-center justify-center bg-slate-900">
                <CheckCircle size={32} className="text-emerald-600" />
              </div>
              <p className="text-sm font-medium">Система в норме</p>
              <p className="text-xs text-slate-500">Нет активных угроз</p>
            </div>
          )}

          {incidents.map((incident) => (
            <div
              key={incident.event_uid}
              onClick={() => setActiveIncidentId(incident.event_uid)}
              className={`
                p-4 rounded-lg border cursor-pointer transition-all duration-200 group
                ${activeIncidentId === incident.event_uid 
                  ? 'bg-slate-800 border-blue-500 shadow-lg shadow-blue-900/20' 
                  : 'bg-slate-900 border-slate-800 hover:border-slate-600 hover:bg-slate-800/50'}
                ${incident.status === 'NEW' ? 'border-l-4 border-l-red-500' : 'border-l-4 border-l-yellow-500'}
              `}
            >
              {/* Верхняя строка карточки */}
              <div className="flex justify-between items-start mb-3">
                <span className={`
                  inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide border
                  ${incident.status === 'NEW' 
                    ? 'bg-red-500/10 text-red-500 border-red-500/20' 
                    : 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'}
                `}>
                  <AlertTriangle size={10} className="mr-1" />
                  {incident.detected_type}
                </span>
                <span className="text-xs text-slate-500 font-mono">
                  {new Date(incident.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                </span>
              </div>

              {/* Пользователь */}
              <div className="flex items-center gap-3 mb-3">
                <div className="h-8 w-8 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700">
                  <User size={14} className="text-slate-400" />
                </div>
                <div className="flex flex-col">
                  <span className="font-medium text-sm text-slate-200 leading-tight">
                    {incident.user?.full_name || 'Неизвестный'}
                  </span>
                  <span className="text-xs text-slate-500">
                    {incident.user?.phone_number}
                  </span>
                </div>
              </div>

              {/* Инфобар внизу карточки */}
              <div className="flex items-center justify-between text-xs text-slate-500 pt-3 border-t border-slate-800/50">
                <div className="flex items-center gap-1.5" title="Battery Level">
                  <Battery size={12} className={incident.device?.battery_level < 20 ? 'text-red-500' : 'text-green-500'} />
                  <span>{incident.device?.battery_level}%</span>
                </div>
                <div className="flex items-center gap-1.5 font-mono" title="Coordinates">
                  <MapPin size={12} />
                  <span>{incident.lat.toFixed(4)}, {incident.lon.toFixed(4)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </aside>

      {/* ЦЕНТРАЛЬНАЯ ЧАСТЬ: Карта */}
      <main className="flex-1 relative bg-slate-950">
        <LiveMap />

        {/* ПАНЕЛЬ ДЕТАЛЕЙ (Появляется поверх карты справа) */}
        <IncidentDetailsPanel />

        {/* Глобальные стили для карты (инверсия цветов для темной темы) */}
        <style jsx global>{`
          .map-tiles-dark {
            filter: invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%) grayscale(20%);
          }
          .leaflet-container {
            background: #020617 !important;
          }
          .custom-popup .leaflet-popup-content-wrapper {
            background: #1e293b;
            color: white;
            border-radius: 8px;
            border: 1px solid #334155;
          }
          .custom-popup .leaflet-popup-tip {
            background: #1e293b;
          }
          .custom-popup .leaflet-popup-close-button {
            color: #94a3b8 !important;
          }
        `}</style>
      </main>
    </div>
  );
}