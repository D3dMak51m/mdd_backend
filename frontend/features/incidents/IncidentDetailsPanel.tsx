// frontend/features/incidents/IncidentDetailsPanel.tsx
'use client';
import {useEffect, useState} from 'react';
import {useIncidentStore} from '@/shared/stores/incident-store';
import {incidentApi} from '@/shared/api/incidents';
import {apiClient} from '@/shared/api/client';
import {
    X, Phone, Navigation, CheckCircle, ShieldAlert, Loader2,
    User, Clock, Battery, Activity, History, MapPin, AlertCircle,
    Send, FileText, TrendingUp
} from 'lucide-react';
import {format, formatDistanceToNow} from 'date-fns';

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
    const [historyLoading, setHistoryLoading] = useState(false);

    const incident = activeIncidentId ? incidents.get(activeIncidentId) : null;

    // Загрузка истории
    useEffect(() => {
        if (incident?.id && activeTab === 'history') {
            setHistoryLoading(true);
            setHistory([]);

            apiClient.get<any>(`/audit/?target_model=sos.sosevent&target_id=${incident.id}`)
                .then(res => setHistory(res.data.results || res.data))
                .catch(err => console.error("Failed to load history:", err))
                .finally(() => setHistoryLoading(false));
        }
    }, [incident?.id, activeTab]);

    if (!incident) return null;

    const handleRespond = async () => {
        setLoading(true);
        try {
            await incidentApi.respond(incident.event_uid);
            addOrUpdateIncident({...incident, status: 'IN_PROGRESS'});
        } catch (error: any) {
            alert(error.response?.data?.detail || 'Error: Call may already be taken');
        } finally {
            setLoading(false);
        }
    };

    const handleResolve = async () => {
        if (!notes.trim()) {
            alert('Please provide resolution notes');
            return;
        }
        setLoading(true);
        try {
            await incidentApi.resolve(incident.event_uid, notes);
            removeIncident(incident.event_uid);
            setActiveIncidentId(null);
            setNotes('');
        } catch (error) {
            alert('Error resolving incident');
        } finally {
            setLoading(false);
        }
    };

    // Status config
    const statusConfig = {
        NEW: {
            color: 'red',
            label: 'NEW ALERT',
            gradient: 'from-red-600 to-orange-600'
        },
        IN_PROGRESS: {
            color: 'yellow',
            label: 'IN PROGRESS',
            gradient: 'from-yellow-600 to-orange-600'
        },
        RESOLVED: {
            color: 'green',
            label: 'RESOLVED',
            gradient: 'from-green-600 to-emerald-600'
        }
    };

    const status = statusConfig[incident.status as keyof typeof statusConfig];

    return (
        <div className="
      absolute top-4 right-4 w-full max-w-md
      bg-slate-900/95 backdrop-blur-xl border border-slate-700/50
      shadow-2xl rounded-2xl overflow-hidden z-[1000]
      animate-in slide-in-from-right-5 fade-in duration-300
      max-h-[calc(100vh-2rem)] flex flex-col
    ">

            {/* HEADER with gradient */}
            <div className={`
        relative p-5 border-b border-slate-700/50 
        bg-gradient-to-r ${status.gradient}
        overflow-hidden
      `}>
                {/* Animated background effect */}
                <div className="absolute inset-0 bg-grid-white/[0.05] bg-[size:20px_20px]"/>

                <div className="relative z-10 flex justify-between items-start">
                    <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                            <ShieldAlert className="text-white" size={24}/>
                            <span className="text-xs font-bold text-white/90 uppercase tracking-wider">
                {status.label}
              </span>
                        </div>
                        <h2 className="text-xl font-bold text-white mb-1">
                            {incident.detected_type.replace('_', ' ')}
                        </h2>
                        <div className="flex items-center gap-3 text-xs text-white/80">
              <span className="font-mono bg-white/10 px-2 py-0.5 rounded">
                #{incident.event_uid.slice(0, 8)}
              </span>
                            <span>{formatDistanceToNow(new Date(incident.timestamp), {addSuffix: true})}</span>
                        </div>
                    </div>

                    <button
                        onClick={() => setActiveIncidentId(null)}
                        className="p-2 hover:bg-white/10 rounded-lg transition-colors text-white/90 hover:text-white"
                    >
                        <X size={20}/>
                    </button>
                </div>
            </div>

            {/* TABS */}
            <div className="flex border-b border-slate-800 bg-slate-900/50 shrink-0">
                {[
                    {id: 'details', label: 'Details', icon: Activity},
                    {id: 'history', label: 'Timeline', icon: History}
                ].map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id as any)}
                        className={`
              flex-1 py-3.5 text-sm font-semibold transition-all relative
              ${activeTab === tab.id ? 'text-blue-400' : 'text-slate-400 hover:text-slate-200'}
            `}
                    >
            <span className="flex items-center justify-center gap-2">
              <tab.icon size={16}/>
                {tab.label}
            </span>
                        {activeTab === tab.id && (
                            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500"/>
                        )}
                    </button>
                ))}
            </div>

            {/* CONTENT */}
            <div className="flex-1 overflow-y-auto custom-scrollbar">
                {activeTab === 'details' ? (
                    <div className="p-5 space-y-6">
                        {/* Severity Indicator */}
                        <div className="flex items-center justify-between p-4 bg-slate-950 rounded-xl border border-slate-800">
                            <span className="text-sm font-medium text-slate-400">Severity Level</span>
                            <div className="flex items-center gap-2">
                                {Array.from({length: 5}).map((_, i) => (
                                    <div
                                        key={i}
                                        className={`h-2 w-2 rounded-full transition-all ${
                                            i < incident.severity
                                                ? 'bg-gradient-to-r from-red-500 to-orange-500 shadow-[0_0_6px_rgba(239,68,68,0.5)]'
                                                : 'bg-slate-700'
                                        }`}
                                    />
                                ))}
                                <span className="ml-2 text-sm font-bold text-red-500">{incident.severity}/5</span>
                            </div>
                        </div>

                        {/* User Card */}
                        <div>
                            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
                                Victim Information
                            </h3>
                            <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 p-4 rounded-xl border border-slate-700/50">
                                <div className="flex items-center gap-4">
                                    <div
                                        className="h-14 w-14 rounded-full bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center border-2 border-slate-600">
                                        <User size={24} className="text-slate-300"/>
                                    </div>
                                    <div className="flex-1">
                                        <div className="font-semibold text-white mb-1">
                                            {incident.user?.full_name || 'Unknown User'}
                                        </div>
                                        <a
                                            href={`tel:${incident.user?.phone_number}`}
                                            className="flex items-center gap-1.5 text-sm text-blue-400 hover:text-blue-300 transition-colors"
                                        >
                                            <Phone size={14}/>
                                            {incident.user?.phone_number}
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Info Grid */}
                        <div className="grid grid-cols-2 gap-3">
                            {/* Location */}
                            <div className="col-span-2 p-4 bg-slate-950 rounded-xl border border-slate-800">
                                <div className="flex items-start gap-3">
                                    <div className="p-2 bg-blue-500/10 rounded-lg">
                                        <MapPin size={18} className="text-blue-400"/>
                                    </div>
                                    <div className="flex-1">
                                        <div className="text-xs text-slate-500 mb-1">Coordinates</div>
                                        <div className="font-mono text-sm text-slate-200">
                                            {incident.lat.toFixed(6)}, {incident.lon.toFixed(6)}
                                        </div>
                                        <button className="mt-2 text-xs text-blue-400 hover:text-blue-300 transition-colors">
                                            Open in Maps →
                                        </button>
                                    </div>
                                </div>
                            </div>

                            {/* Device */}
                            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800">
                                <div className="flex items-start gap-2 mb-2">
                                    <Activity size={14} className="text-slate-500 mt-0.5"/>
                                    <div className="text-xs text-slate-500">Device</div>
                                </div>
                                <div className="text-sm font-medium text-slate-200 truncate">
                                    {incident.device?.model || 'N/A'}
                                </div>
                            </div>

                            {/* Battery */}
                            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800">
                                <div className="flex items-start gap-2 mb-2">
                                    <Battery size={14} className="text-slate-500 mt-0.5"/>
                                    <div className="text-xs text-slate-500">Battery</div>
                                </div>
                                <div className={`text-sm font-bold ${
                                    (incident.device?.battery_level || 0) < 20 ? 'text-red-400' : 'text-green-400'
                                }`}>
                                    {incident.device?.battery_level || '--'}%
                                </div>
                            </div>

                            {/* Time */}
                            <div className="col-span-2 p-4 bg-slate-950 rounded-xl border border-slate-800">
                                <div className="flex items-start gap-3">
                                    <div className="p-2 bg-purple-500/10 rounded-lg">
                                        <Clock size={18} className="text-purple-400"/>
                                    </div>
                                    <div className="flex-1">
                                        <div className="text-xs text-slate-500 mb-1">Reported At</div>
                                        <div className="text-sm text-slate-200">
                                            {format(new Date(incident.timestamp), 'MMM dd, yyyy HH:mm:ss')}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="pt-4 border-t border-slate-800 space-y-4">
                            {incident.status === 'NEW' && (
                                <button
                                    onClick={handleRespond}
                                    disabled={loading}
                                    className="w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold rounded-xl transition-all flex items-center justify-center gap-2 disabled:opacity-50 shadow-lg shadow-blue-900/20 hover:shadow-xl hover:shadow-blue-900/30 active:scale-[0.98]"
                                >
                                    {loading ? (
                                        <>
                                            <Loader2 size={20} className="animate-spin"/>
                                            Processing...
                                        </>
                                    ) : (
                                        <>
                                            <ShieldAlert size={20}/>
                                            ACCEPT & RESPOND
                                        </>
                                    )}
                                </button>
                            )}

                            {incident.status === 'IN_PROGRESS' && (
                                <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2">
                                    {/* Alert */}
                                    <div className="bg-yellow-500/10 border border-yellow-500/20 p-4 rounded-xl flex gap-3">
                                        <AlertCircle size={20} className="text-yellow-400 shrink-0 mt-0.5"/>
                                        <div className="text-sm text-yellow-200">
                                            <p className="font-semibold mb-1">Incident Active</p>
                                            <p className="text-xs text-yellow-300/80">
                                                Complete your report before closing this incident.
                                            </p>
                                        </div>
                                    </div>

                                    {/* Notes Input */}
                                    <div>
                                        <label className="block text-xs font-semibold text-slate-400 mb-2">
                                            Resolution Notes *
                                        </label>
                                        <textarea
                                            value={notes}
                                            onChange={(e) => setNotes(e.target.value)}
                                            placeholder="Describe the situation, actions taken, and outcome..."
                                            rows={4}
                                            className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-sm text-white placeholder-slate-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none resize-none transition-all"
                                        />
                                    </div>

                                    {/* Resolve Button */}
                                    <button
                                        onClick={handleResolve}
                                        disabled={loading || !notes.trim()}
                                        className="w-full py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-bold rounded-xl transition-all flex items-center justify-center gap-2 disabled:opacity-50 shadow-lg shadow-green-900/20 hover:shadow-xl hover:shadow-green-900/30 active:scale-[0.98]"
                                    >
                                        {loading ? (
                                            <>
                                                <Loader2 size={20} className="animate-spin"/>
                                                Saving...
                                            </>
                                        ) : (
                                            <>
                                                <CheckCircle size={20}/>
                                                MARK AS RESOLVED
                                            </>
                                        )}
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                ) : (
                    // HISTORY TAB
                    <div className="p-5">
                        {historyLoading ? (
                            <div className="space-y-4">
                                {Array.from({length: 3}).map((_, i) => (
                                    <div key={i} className="flex gap-4 animate-pulse">
                                        <div className="h-10 w-10 bg-slate-800 rounded-full"/>
                                        <div className="flex-1 space-y-2">
                                            <div className="h-4 bg-slate-800 rounded w-3/4"/>
                                            <div className="h-3 bg-slate-800 rounded w-1/2"/>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : history.length === 0 ? (
                            <div className="text-center py-12">
                                <History size={48} className="mx-auto text-slate-700 mb-4"/>
                                <p className="text-slate-500 text-sm">No activity recorded yet</p>
                            </div>
                        ) : (
                            <div className="space-y-4 relative">
                                {/* Timeline Line */}
                                <div className="absolute left-5 top-2 bottom-2 w-0.5 bg-gradient-to-b from-blue-500 via-purple-500 to-transparent"/>

                                {history.map((log, idx) => (
                                    <div key={log.id} className="relative pl-14 group">
                                        {/* Timeline Dot */}
                                        <div className={`
                      absolute left-0 top-1.5 w-10 h-10 rounded-full flex items-center justify-center z-10
                      ${log.action === 'CREATE' ? 'bg-red-500/20 border-2 border-red-500' :
                                            log.action === 'UPDATE' ? 'bg-blue-500/20 border-2 border-blue-500' :
                                                'bg-slate-700/20 border-2 border-slate-700'}
                    `}>
                                            {log.action === 'CREATE' ? <AlertCircle size={16}/> :
                                                log.action === 'UPDATE' ? <Activity size={16}/> :
                                                    <CheckCircle size={16}/>}
                                        </div>

                                        {/* Content */}
                                        <div
                                            className="bg-slate-950 border border-slate-800 rounded-xl p-4 group-hover:border-slate-700 transition-colors">
                                            <div className="flex items-start justify-between mb-2">
                                                <div>
                                                    <p className="text-sm font-semibold text-white">
                                                        {log.actor_name || 'System'}
                                                    </p>
                                                    <p className="text-xs text-slate-500 mt-0.5">
                                                        {log.action === 'CREATE' ? 'Created incident' :
                                                            log.action === 'UPDATE' ? 'Updated status' :
                                                                'Performed action'}
                                                    </p>
                                                </div>
                                                <span className="text-xs text-slate-600 font-mono">
                          {format(new Date(log.created_at), 'HH:mm')}
                        </span>
                                            </div>

                                            {/* Changes */}
                                            {log.changes && Object.keys(log.changes).length > 0 && (
                                                <div className="mt-3 pt-3 border-t border-slate-800/50 space-y-2">
                                                    {Object.entries(log.changes).map(([key, val]: any) => (
                                                        <div key={key} className="text-xs">
                                                            <span className="text-slate-500 font-mono">{key}:</span>
                                                            <div className="mt-1 flex items-center gap-2 flex-wrap">
                                <span className="px-2 py-1 bg-red-500/10 text-red-400 rounded border border-red-500/20 line-through">
                                  {String(val.old)}
                                </span>
                                                                <span className="text-slate-600">→</span>
                                                                <span
                                                                    className="px-2 py-1 bg-green-500/10 text-green-400 rounded border border-green-500/20 font-semibold">
                                  {String(val.new)}
                                </span>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}