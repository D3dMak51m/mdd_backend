'use client';

import { useEffect, useState } from 'react';
import { useIncidentStore } from '@/shared/stores/incident-store';
import { incidentApi } from '@/shared/api/incidents';
import { apiClient } from '@/shared/api/client';
import {
  X, Phone, Navigation, CheckCircle, ShieldAlert,
  User, Clock, Battery, Activity, History
} from 'lucide-react';
import { format } from 'date-fns';

// Тип для лога аудита (локальный или импортированный)
interface AuditLogEntry {
  id: number;
  actor_name: string;
  action: string;
  changes: Record<string, { old: any; new: any }>;
  created_at: string;
}

export default function IncidentDetailsPanel() {
  const {
    activeIncidentId,
    incidents,
    setActiveIncidentId,
    addOrUpdateIncident,
    removeIncident
  } = useIncidentStore();

  const [loading, setLoading] = useState(false);
  const [notes, setNotes] = useState('');
  const [activeTab, setActiveTab] = useState<'details' | 'history'>('details');
  const [history, setHistory] = useState<AuditLogEntry[]>([]);

  // Получаем объект инцидента
  const incident = activeIncidentId ? incidents.get(activeIncidentId) : null;

  // Загрузка истории при открытии или смене инцидента
  useEffect(() => {
    if (incident?.id) {
      // Сбрасываем историю при смене инцидента
      setHistory([]);

      // Загружаем логи фильтруя по модели и ID
      apiClient.get<AuditLogEntry[]>(`/audit/?target_model=sos.sosevent&target_id=${incident.id}`)
        .then(res => setHistory(res.data))
        .catch(err => console.error("Failed to load history:", err));
    }
  }, [incident?.id]);

  // Если инцидент не выбран — скрываем панель
  if (!incident) return null;

  const handleRespond = async () => {
    setLoading(true);
    try {
      await incidentApi.respond(incident.event_uid);
      // Оптимистичное обновление (реальное придет по сокету)
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
      setNotes(''); // Очистка поля
    } catch (error) {
      alert('Ошибка при закрытии инцидента.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="absolute top-4 right-4 w-96 bg-slate-900/95 backdrop-blur-md border border-slate-700 shadow-2xl rounded-xl overflow-hidden z-[1000] text-slate-100 flex flex-col max-h-[calc(100vh-2rem)] animate-in slide-in-from-right duration-300">

      {/* Header */}
      <div className="p-4 border-b border-slate-700 flex justify-between items-start bg-slate-800/50 shrink-0">
        <div>
          <h2 className="text-lg font-bold flex items-center gap-2 text-white">
            <ShieldAlert className={incident.severity >= 4 ? "text-red-500" : "text-yellow-500"} size={20} />
            {incident.detected_type}
          </h2>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-slate-400 font-mono bg-slate-800 px-1.5 py-0.5 rounded">
              ID: {incident.event_uid.slice(0, 8)}
            </span>
            <span className="text-xs text-slate-400">
              {format(new Date(incident.timestamp), 'HH:mm:ss')}
            </span>
          </div>
        </div>
        <button
          onClick={() => setActiveIncidentId(null)}
          className="p-1.5 hover:bg-slate-700 rounded-lg transition-colors text-slate-400 hover:text-white"
        >
          <X size={20} />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-700 bg-slate-900 shrink-0">
        <button
          onClick={() => setActiveTab('details')}
          className={`flex-1 py-3 text-sm font-medium transition-colors relative ${
            activeTab === 'details' ? 'text-blue-400' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <span className="flex items-center justify-center gap-2">
            <Activity size={16} /> Детали
          </span>
          {activeTab === 'details' && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-400"></div>}
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`flex-1 py-3 text-sm font-medium transition-colors relative ${
            activeTab === 'history' ? 'text-blue-400' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <span className="flex items-center justify-center gap-2">
            <History size={16} /> История
          </span>
          {activeTab === 'history' && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-400"></div>}
        </button>
      </div>

      {/* Body */}
      <div className="p-4 overflow-y-auto custom-scrollbar flex-1">

        {activeTab === 'details' ? (
          <div className="space-y-6">
            {/* User Info */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Пострадавший</h3>
              <div className="flex items-center gap-3 bg-slate-800/50 p-3 rounded-lg border border-slate-700/50">
                <div className="h-10 w-10 rounded-full bg-slate-700 flex items-center justify-center text-slate-300">
                  <User size={20} />
                </div>
                <div>
                  <div className="font-medium text-white">{incident.user?.full_name || 'Неизвестный'}</div>
                  <div className="text-sm text-blue-400 flex items-center gap-1 font-mono">
                    <Phone size={12} /> {incident.user?.phone_number}
                  </div>
                </div>
              </div>
            </div>

            {/* Device & Location Grid */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/50">
                <div className="text-xs text-slate-500 mb-1 flex items-center gap-1">
                  <Navigation size={12} /> Координаты
                </div>
                <div className="text-sm font-mono text-slate-200">
                  {incident.lat.toFixed(5)}<br/>{incident.lon.toFixed(5)}
                </div>
              </div>
              <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/50">
                <div className="text-xs text-slate-500 mb-1 flex items-center gap-1">
                  <Battery size={12} /> Устройство
                </div>
                <div className="text-sm text-slate-200 truncate">
                  {incident.device?.model || 'N/A'}
                </div>
                <div className={`text-xs font-bold mt-1 ${
                  (incident.device?.battery_level || 0) < 20 ? 'text-red-400' : 'text-green-400'
                }`}>
                  {incident.device?.battery_level}% Battery
                </div>
              </div>
            </div>

            {/* Status & Actions */}
            <div className="pt-4 border-t border-slate-700 mt-auto">
              <div className="flex justify-between items-center mb-4">
                <span className="text-xs font-bold text-slate-500 uppercase">Текущий статус</span>
                <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${
                  incident.status === 'NEW' ? 'bg-red-500/10 text-red-400 border-red-500/20' : 
                  incident.status === 'IN_PROGRESS' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' : 
                  'bg-green-500/10 text-green-400 border-green-500/20'
                }`}>
                  {incident.status.replace('_', ' ')}
                </span>
              </div>

              {incident.status === 'NEW' && (
                <button
                  onClick={handleRespond}
                  disabled={loading}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white font-bold rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-900/20"
                >
                  {loading ? (
                    <span className="animate-pulse">Обработка...</span>
                  ) : (
                    <>
                      <ShieldAlert size={18} />
                      ПРИНЯТЬ ВЫЗОВ
                    </>
                  )}
                </button>
              )}

              {incident.status === 'IN_PROGRESS' && (
                <div className="space-y-3 animate-in fade-in slide-in-from-bottom-2">
                  <div className="bg-yellow-500/10 border border-yellow-500/20 p-3 rounded-lg text-sm text-yellow-200 flex items-start gap-2">
                    <Clock size={16} className="mt-0.5 shrink-0" />
                    <span>Инцидент в работе. Заполните отчет перед закрытием.</span>
                  </div>

                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Опишите результат выезда и состояние пользователя..."
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-sm text-white placeholder-slate-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none h-24 resize-none transition-all"
                  />

                  <button
                    onClick={handleResolve}
                    disabled={loading}
                    className="w-full py-3 bg-green-600 hover:bg-green-500 active:bg-green-700 text-white font-bold rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-green-900/20"
                  >
                    <CheckCircle size={18} />
                    ЗАВЕРШИТЬ ИНЦИДЕНТ
                  </button>
                </div>
              )}
            </div>
          </div>
        ) : (
          // TIMELINE TAB
          <div className="space-y-6 relative">
            {/* Вертикальная линия */}
            <div className="absolute left-2 top-2 bottom-2 w-0.5 bg-slate-800"></div>

            {history.map((log) => (
              <div key={log.id} className="relative pl-8 group">
                {/* Точка на линии */}
                <div className={`
                  absolute left-0 top-1.5 w-4 h-4 rounded-full border-2 border-slate-900 z-10
                  ${log.action === 'CREATE' ? 'bg-red-500' : 
                    log.action === 'UPDATE' ? 'bg-blue-500' : 
                    'bg-slate-600'}
                `}></div>

                <div className="flex flex-col">
                  <span className="text-xs text-slate-500 font-mono mb-0.5">
                    {format(new Date(log.created_at), 'dd MMM HH:mm')}
                  </span>

                  <div className="text-sm text-slate-200">
                    <span className="font-bold text-white">
                      {log.actor_name || 'System'}
                    </span>
                    <span className="text-slate-400 mx-1">
                      {log.action === 'CREATE' ? 'создал(а)' :
                       log.action === 'UPDATE' ? 'обновил(а)' : 'изменил(а)'}
                    </span>
                    инцидент
                  </div>

                  {/* Изменения полей */}
                  {log.changes && Object.keys(log.changes).length > 0 && (
                    <div className="mt-2 text-xs bg-slate-800/50 border border-slate-700/50 rounded p-2 space-y-1">
                      {Object.entries(log.changes).map(([key, val]: any) => (
                        <div key={key} className="flex items-center gap-2 flex-wrap">
                          <span className="text-slate-400 font-mono">{key}:</span>
                          <span className="text-red-400 line-through opacity-70">{String(val.old)}</span>
                          <span className="text-slate-600">→</span>
                          <span className="text-green-400 font-bold">{String(val.new)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {history.length === 0 && (
              <div className="text-center py-8 text-slate-500 text-sm pl-0">
                История действий пуста
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}