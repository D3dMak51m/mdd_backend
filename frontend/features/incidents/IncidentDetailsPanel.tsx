'use client';

import { useState } from 'react';
import { useIncidentStore } from '@/shared/stores/incident-store';
import { incidentApi } from '@/shared/api/incidents';
import { X, Phone, Navigation, CheckCircle, ShieldAlert, User, Clock } from 'lucide-react';

export default function IncidentDetailsPanel() {
  const { activeIncidentId, incidents, setActiveIncidentId, addOrUpdateIncident, removeIncident } = useIncidentStore();
  const [loading, setLoading] = useState(false);
  const [notes, setNotes] = useState('');

  // Если инцидент не выбран или не найден в сторе — не рендерим ничего
  if (!activeIncidentId) return null;
  const incident = incidents.get(activeIncidentId);
  if (!incident) return null;

  const handleRespond = async () => {
    if (!confirm('Вы уверены, что хотите принять этот вызов?')) return;
    setLoading(true);
    try {
      await incidentApi.respond(incident.event_uid);
      // Оптимистичное обновление UI (или ждем прилета по WS)
      addOrUpdateIncident({ ...incident, status: 'IN_PROGRESS' });
    } catch (error) {
      alert('Ошибка: Возможно, вызов уже принят другим оператором.');
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async () => {
    if (!notes.trim()) {
      alert('Пожалуйста, укажите комментарий к решению.');
      return;
    }
    setLoading(true);
    try {
      await incidentApi.resolve(incident.event_uid, notes);
      // Удаляем из активных, так как он закрыт
      removeIncident(incident.event_uid);
      setActiveIncidentId(null);
    } catch (error) {
      alert('Ошибка при закрытии инцидента.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="absolute top-4 right-4 w-96 bg-slate-900/95 backdrop-blur border border-slate-700 shadow-2xl rounded-xl overflow-hidden z-[1000] text-slate-100 flex flex-col max-h-[calc(100vh-2rem)]">

      {/* Header */}
      <div className="p-4 border-b border-slate-700 flex justify-between items-start bg-slate-800/50">
        <div>
          <h2 className="text-lg font-bold flex items-center gap-2">
            <ShieldAlert className="text-red-500" size={20} />
            {incident.detected_type}
          </h2>
          <span className="text-xs text-slate-400 font-mono">{incident.event_uid.slice(0, 8)}...</span>
        </div>
        <button
          onClick={() => setActiveIncidentId(null)}
          className="p-1 hover:bg-slate-700 rounded transition-colors"
        >
          <X size={20} />
        </button>
      </div>

      {/* Body */}
      <div className="p-4 space-y-6 overflow-y-auto">

        {/* User Info */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Пострадавший</h3>
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-slate-700 flex items-center justify-center">
              <User size={20} />
            </div>
            <div>
              <div className="font-medium">{incident.user?.full_name || 'Неизвестный'}</div>
              <div className="text-sm text-slate-400 flex items-center gap-1">
                <Phone size={12} /> {incident.user?.phone_number}
              </div>
            </div>
          </div>
        </div>

        {/* Location & Device */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-800 p-3 rounded-lg">
            <div className="text-xs text-slate-500 mb-1">Координаты</div>
            <div className="text-sm font-mono flex items-center gap-1">
              <Navigation size={12} />
              {incident.lat.toFixed(4)}, {incident.lon.toFixed(4)}
            </div>
          </div>
          <div className="bg-slate-800 p-3 rounded-lg">
            <div className="text-xs text-slate-500 mb-1">Устройство</div>
            <div className="text-sm">
              {incident.device?.model || 'N/A'}
              <span className="ml-1 text-xs text-green-400">({incident.device?.battery_level}%)</span>
            </div>
          </div>
        </div>

        {/* Status & Actions */}
        <div className="pt-4 border-t border-slate-700">
          <div className="flex justify-between items-center mb-4">
            <span className="text-xs font-bold text-slate-500 uppercase">Статус</span>
            <span className={`px-2 py-1 rounded text-xs font-bold ${
              incident.status === 'NEW' ? 'bg-red-500/20 text-red-400' : 
              incident.status === 'IN_PROGRESS' ? 'bg-yellow-500/20 text-yellow-400' : 
              'bg-green-500/20 text-green-400'
            }`}>
              {incident.status}
            </span>
          </div>

          {incident.status === 'NEW' && (
            <button
              onClick={handleRespond}
              disabled={loading}
              className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? 'Обработка...' : 'ПРИНЯТЬ ВЫЗОВ'}
            </button>
          )}

          {incident.status === 'IN_PROGRESS' && (
            <div className="space-y-3">
              <div className="bg-yellow-500/10 border border-yellow-500/20 p-3 rounded text-sm text-yellow-200 flex items-center gap-2">
                <Clock size={16} />
                В работе. Исполнитель назначен.
              </div>

              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Результат выезда (обязательно)..."
                className="w-full bg-slate-800 border border-slate-600 rounded p-2 text-sm text-white focus:border-blue-500 outline-none h-20 resize-none"
              />

              <button
                onClick={handleResolve}
                disabled={loading}
                className="w-full py-3 bg-green-600 hover:bg-green-500 text-white font-bold rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <CheckCircle size={18} />
                ЗАВЕРШИТЬ ИНЦИДЕНТ
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}