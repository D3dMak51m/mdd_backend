// frontend/app/(protected)/live/page.tsx
'use client';
import dynamic from 'next/dynamic';
import {useEffect, useState} from 'react';
import {
    Radio, AlertTriangle, User, Battery, MapPin, CheckCircle,
    Search, X, Filter, Menu, ChevronLeft, Settings, Bell
} from 'lucide-react';
import {useOpsSocket} from '@/features/realtime/use-socket';
import {useIncidentStore} from '@/shared/stores/incident-store';
import {incidentApi} from '@/shared/api/incidents';
import IncidentDetailsPanel from '@/features/incidents/IncidentDetailsPanel';

const LiveMap = dynamic(() => import('@/features/map/LiveMap'), {
    ssr: false,
    loading: () => (
        <div className="h-full w-full flex items-center justify-center bg-slate-900">
            <div className="text-center">
                <div className="relative inline-block">
                    <div className="absolute inset-0 bg-blue-500 rounded-full blur-xl opacity-30 animate-pulse"/>
                    <MapPin className="relative text-blue-500 animate-bounce" size={48}/>
                </div>
                <p className="text-slate-400 mt-4 font-medium">Loading map...</p>
            </div>
        </div>
    ),
});

export default function LivePage() {
    const {readyState} = useOpsSocket();
    const {
        getSortedIncidents,
        setActiveIncidentId,
        activeIncidentId,
        setIncidents
    } = useIncidentStore();

    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [filterStatus, setFilterStatus] = useState<string>('all');
    const [loading, setLoading] = useState(true);

    const incidents = getSortedIncidents();

    // Фильтрация
    const filteredIncidents = incidents.filter(incident => {
        const matchesSearch =
            incident.user?.full_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
            incident.user?.phone_number?.includes(searchQuery);

        const matchesFilter =
            filterStatus === 'all' || incident.status === filterStatus;

        return matchesSearch && matchesFilter;
    });

    // Загрузка данных
    useEffect(() => {
        const fetchActive = async () => {
            try {
                const data = await incidentApi.getActive();
                setIncidents(data);
            } catch (e) {
                console.error("Failed to fetch initial incidents", e);
            } finally {
                setLoading(false);
            }
        };
        fetchActive();
    }, [setIncidents]);

    return (
        <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">

            {/* SIDEBAR - COLLAPSIBLE */}
            <aside className={`
        ${sidebarOpen ? 'w-96' : 'w-0'} 
        border-r border-slate-800 flex flex-col z-20 
        bg-slate-900/95 backdrop-blur-xl shadow-2xl h-full
        transition-all duration-300 ease-in-out
        ${sidebarOpen ? '' : 'overflow-hidden'}
      `}>

                {/* Header */}
                <header className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900 shrink-0">
                    <div className="flex items-center gap-3">
                        <div className={`
              h-3 w-3 rounded-full transition-all duration-300
              ${readyState === 1
                            ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)] animate-pulse'
                            : 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]'
                        }
            `}/>
                        <span className="font-bold tracking-wider text-sm">
              LIVE MONITOR
            </span>
                    </div>

                    <div className="flex items-center gap-2">
                        <button
                            className="p-2 hover:bg-slate-800 rounded-lg transition-colors relative"
                            title="Notifications"
                        >
                            <Bell size={18}/>
                            {incidents.length > 0 && (
                                <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full"/>
                            )}
                        </button>
                        <button
                            onClick={() => setSidebarOpen(false)}
                            className="lg:hidden p-2 hover:bg-slate-800 rounded-lg transition-colors"
                        >
                            <X size={18}/>
                        </button>
                    </div>
                </header>

                {/* Search & Filters */}
                <div className="p-4 space-y-3 border-b border-slate-800 bg-slate-900/50 shrink-0">
                    {/* Search */}
                    <div className="relative">
                        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"/>
                        <input
                            type="text"
                            placeholder="Search incidents..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full bg-slate-950 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                        />
                        {searchQuery && (
                            <button
                                onClick={() => setSearchQuery('')}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white"
                            >
                                <X size={14}/>
                            </button>
                        )}
                    </div>

                    {/* Filter Tabs */}
                    <div className="flex gap-2">
                        {[
                            {value: 'all', label: 'All', count: incidents.length},
                            {value: 'NEW', label: 'New', count: incidents.filter(i => i.status === 'NEW').length},
                            {value: 'IN_PROGRESS', label: 'Active', count: incidents.filter(i => i.status === 'IN_PROGRESS').length}
                        ].map(filter => (
                            <button
                                key={filter.value}
                                onClick={() => setFilterStatus(filter.value)}
                                className={`
                  flex-1 px-3 py-2 rounded-lg text-xs font-semibold transition-all duration-200
                  ${filterStatus === filter.value
                                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20'
                                    : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-200'
                                }
                `}
                            >
                                {filter.label}
                                {filter.count > 0 && (
                                    <span className="ml-1.5 px-1.5 py-0.5 rounded-full bg-white/10 text-[10px]">
                    {filter.count}
                  </span>
                                )}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Incidents List */}
                <div className="flex-1 overflow-y-auto p-3 space-y-2 custom-scrollbar">
                    {loading ? (
                        // Loading Skeletons
                        Array.from({length: 3}).map((_, i) => (
                            <div key={i} className="p-4 rounded-lg bg-slate-800/50 animate-pulse">
                                <div className="flex justify-between mb-3">
                                    <div className="h-4 bg-slate-700 rounded w-24"/>
                                    <div className="h-4 bg-slate-700 rounded w-12"/>
                                </div>
                                <div className="flex items-center gap-3 mb-3">
                                    <div className="h-8 w-8 bg-slate-700 rounded-full"/>
                                    <div className="flex-1 space-y-2">
                                        <div className="h-3 bg-slate-700 rounded w-3/4"/>
                                        <div className="h-3 bg-slate-700 rounded w-1/2"/>
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : filteredIncidents.length === 0 ? (
                        // Empty State
                        <div className="h-full flex flex-col items-center justify-center text-center py-12">
                            <div className="h-16 w-16 rounded-full bg-slate-800 flex items-center justify-center mb-4">
                                <CheckCircle size={32} className="text-emerald-600"/>
                            </div>
                            <h3 className="text-sm font-semibold text-white mb-1">
                                {searchQuery ? 'No matches found' : 'All clear!'}
                            </h3>
                            <p className="text-xs text-slate-500">
                                {searchQuery ? 'Try adjusting your search' : 'No active incidents at the moment'}
                            </p>
                        </div>
                    ) : (
                        // Incidents Cards
                        filteredIncidents.map((incident) => (
                            <button
                                key={incident.event_uid}
                                onClick={() => setActiveIncidentId(incident.event_uid)}
                                className={`
                  w-full text-left p-4 rounded-xl border transition-all duration-200 group
                  hover:scale-[1.02] active:scale-[0.98]
                  ${activeIncidentId === incident.event_uid
                                    ? 'bg-gradient-to-br from-blue-600/10 to-purple-600/10 border-blue-500 shadow-lg shadow-blue-900/20 ring-2 ring-blue-500/20'
                                    : 'bg-slate-900 border-slate-800 hover:border-slate-600 hover:shadow-md'
                                }
                `}
                            >
                                {/* Status Bar */}
                                <div className={`
                  absolute left-0 top-0 bottom-0 w-1 rounded-l-xl transition-all duration-300
                  ${incident.status === 'NEW'
                                    ? 'bg-gradient-to-b from-red-500 to-orange-500'
                                    : 'bg-gradient-to-b from-yellow-500 to-orange-500'
                                }
                `}/>

                                {/* Header */}
                                <div className="flex justify-between items-start mb-3">
                  <span className={`
                    inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wide border transition-all
                    ${incident.status === 'NEW'
                      ? 'bg-red-500/10 text-red-400 border-red-500/20 group-hover:bg-red-500/20'
                      : 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20 group-hover:bg-yellow-500/20'
                  }
                  `}>
                    <AlertTriangle size={10}/>
                      {incident.detected_type.replace('_', ' ')}
                  </span>
                                    <span className="text-xs text-slate-500 font-mono">
                    {new Date(incident.timestamp).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}
                  </span>
                                </div>

                                {/* User Info */}
                                <div className="flex items-center gap-3 mb-3">
                                    <div
                                        className="h-9 w-9 rounded-full bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center border border-slate-700 group-hover:border-slate-600 transition-colors">
                                        <User size={16} className="text-slate-400"/>
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="font-medium text-sm text-white truncate">
                                            {incident.user?.full_name || 'Unknown'}
                                        </div>
                                        <div className="text-xs text-slate-500 truncate">
                                            {incident.user?.phone_number}
                                        </div>
                                    </div>
                                </div>

                                {/* Footer Stats */}
                                <div className="flex items-center justify-between text-xs pt-3 border-t border-slate-800/50">
                                    <div className="flex items-center gap-1.5" title="Battery Level">
                                        <Battery
                                            size={12}
                                            className={incident.device?.battery_level < 20 ? 'text-red-500' : 'text-green-500'}
                                        />
                                        <span className="text-slate-400">{incident.device?.battery_level || '--'}%</span>
                                    </div>

                                    <div className="flex items-center gap-1.5" title="Location">
                                        <MapPin size={12} className="text-slate-500"/>
                                        <span className="text-slate-500 font-mono text-[10px]">
                      {incident.lat.toFixed(3)}, {incident.lon.toFixed(3)}
                    </span>
                                    </div>

                                    {/* Severity Indicator */}
                                    <div className="flex gap-0.5" title={`Severity: ${incident.severity}/5`}>
                                        {Array.from({length: 5}).map((_, i) => (
                                            <div
                                                key={i}
                                                className={`h-1 w-1 rounded-full ${
                                                    i < incident.severity ? 'bg-red-500' : 'bg-slate-700'
                                                }`}
                                            />
                                        ))}
                                    </div>
                                </div>
                            </button>
                        ))
                    )}
                </div>

                {/* Footer Stats */}
                <div className="p-4 border-t border-slate-800 bg-slate-900/50 shrink-0">
                    <div className="grid grid-cols-3 gap-3 text-center">
                        <div>
                            <div className="text-2xl font-bold text-red-500">
                                {incidents.filter(i => i.status === 'NEW').length}
                            </div>
                            <div className="text-xs text-slate-500 uppercase">New</div>
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-yellow-500">
                                {incidents.filter(i => i.status === 'IN_PROGRESS').length}
                            </div>
                            <div className="text-xs text-slate-500 uppercase">Active</div>
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-blue-500">
                                {incidents.length}
                            </div>
                            <div className="text-xs text-slate-500 uppercase">Total</div>
                        </div>
                    </div>
                </div>
            </aside>

            {/* MAP AREA */}
            <main className="flex-1 relative bg-slate-950">
                {/* Floating Toolbar */}
                <div className="absolute top-4 left-4 z-10 flex gap-2">
                    {!sidebarOpen && (
                        <button
                            onClick={() => setSidebarOpen(true)}
                            className="p-3 bg-slate-900/95 backdrop-blur-xl border border-slate-800 rounded-xl shadow-2xl hover:bg-slate-800 transition-all text-white"
                            title="Open Sidebar"
                        >
                            <Menu size={20}/>
                        </button>
                    )}
                </div>

                <LiveMap/>

                {/* Details Panel (slides in from right) */}
                <IncidentDetailsPanel/>

                {/* Map Styles */}
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
                        border-radius: 12px;
                        border: 1px solid #334155;
                    }

                    .custom-popup .leaflet-popup-tip {
                        background: #1e293b;
                    }

                    .custom-scrollbar::-webkit-scrollbar {
                        width: 6px;
                    }

                    .custom-scrollbar::-webkit-scrollbar-track {
                        background: #1e293b;
                    }

                    .custom-scrollbar::-webkit-scrollbar-thumb {
                        background: #475569;
                        border-radius: 3px;
                    }

                    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                        background: #64748b;
                    }
                `}</style>
            </main>
        </div>
    );
}