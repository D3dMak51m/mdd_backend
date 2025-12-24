import React from 'react';
import { AlertTriangle, Clock, MapPin } from 'lucide-react';

// Временные данные для верстки
const mockIncidents = [
  { id: 1, type: 'FALL_DETECTED', user: 'Ivan Ivanov', time: '10:42', status: 'new' },
  { id: 2, type: 'MANUAL_SOS', user: 'Petr Petrov', time: '10:30', status: 'progress' },
  { id: 3, type: 'INACTIVITY', user: 'Sidorov A.', time: '09:15', status: 'resolved' },
];

export default function Sidebar() {
  return (
    <aside className="w-96 bg-ops-panel border-r border-ops-border flex flex-col h-screen z-20">
      {/* Header */}
      <div className="p-4 border-b border-ops-border flex justify-between items-center bg-slate-900/50">
        <h2 className="font-bold text-lg tracking-wider text-slate-100 flex items-center gap-2">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
          </span>
          LIVE FEED
        </h2>
        <span className="text-xs font-mono text-slate-400">WS: CONNECTED</span>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {mockIncidents.map((inc) => (
          <div
            key={inc.id}
            className={`
              p-4 rounded-lg border cursor-pointer transition-all hover:bg-slate-700/50
              ${inc.status === 'new' ? 'border-l-4 border-l-ops-alert bg-red-500/10 border-y-transparent border-r-transparent' : 'border-ops-border bg-slate-800'}
            `}
          >
            <div className="flex justify-between items-start mb-1">
              <span className={`text-xs font-bold px-2 py-0.5 rounded ${inc.status === 'new' ? 'bg-red-500 text-white' : 'bg-slate-600 text-slate-300'}`}>
                {inc.type}
              </span>
              <span className="text-xs text-slate-400 flex items-center gap-1">
                <Clock size={12} /> {inc.time}
              </span>
            </div>
            <div className="font-medium text-slate-200">{inc.user}</div>
            <div className="text-xs text-slate-500 mt-2 flex items-center gap-1">
              <MapPin size={12} /> 41.311, 69.240
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}