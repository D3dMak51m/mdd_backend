// frontend/app/(protected)/audit/page.tsx - УЛУЧШЕННАЯ ВЕРСИЯ
'use client';
import {useState} from 'react';
import {useQuery} from '@tanstack/react-query';
import {apiClient} from '@/shared/api/client';
import {format} from 'date-fns';
import {
    Search, Filter, Loader2, ChevronLeft, ChevronRight, X,
    FileText, Download, Calendar, User, Activity
} from 'lucide-react';

const fetchAuditLogs = async (params: any) => {
    const {data} = await apiClient.get('/audit/', {params});
    return data;
};

// Action Badge Component
const ActionBadge = ({action}: { action: string }) => {
    const configs: Record<string, { color: string; label: string }> = {
        LOGIN: {color: 'bg-green-500/10 text-green-400 border-green-500/20', label: 'Login'},
        UPDATE: {color: 'bg-blue-500/10 text-blue-400 border-blue-500/20', label: 'Update'},
        CREATE: {color: 'bg-purple-500/10 text-purple-400 border-purple-500/20', label: 'Create'},
        RESOLVE: {color: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20', label: 'Resolve'},
        DELETE: {color: 'bg-red-500/10 text-red-400 border-red-500/20', label: 'Delete'},
    };

    const config = configs[action] || {color: 'bg-slate-700 text-slate-300 border-slate-600', label: action};

    return (
        <span className={`px-2.5 py-1 rounded-lg text-xs font-bold uppercase tracking-wide border ${config.color}`}>
      {config.label}
    </span>
    );
};

// Change Details Component
const ChangeDetails = ({changes}: { changes: any }) => {
    if (!changes || Object.keys(changes).length === 0) {
        return <span className="text-slate-600">-</span>;
    }

    const entries = Object.entries(changes).slice(0, 3);

    return (
        <div className="space-y-1.5 text-xs">
            {entries.map(([key, val]: any) => (
                <div key={key} className="flex items-center gap-2 flex-wrap">
                    <span className="text-slate-500 font-mono">{key}:</span>
                    <span className="px-1.5 py-0.5 bg-red-500/10 text-red-400 rounded border border-red-500/20 line-through truncate max-w-[100px]">
            {String(val.old).slice(0, 20)}
          </span>
                    <span className="text-slate-600">→</span>
                    <span
                        className="px-1.5 py-0.5 bg-green-500/10 text-green-400 rounded border border-green-500/20 truncate max-w-[100px] font-semibold">
            {String(val.new).slice(0, 20)}
          </span>
                </div>
            ))}
            {Object.keys(changes).length > 3 && (
                <span className="text-slate-600 text-[10px]">
          +{Object.keys(changes).length - 3} more
        </span>
            )}
        </div>
    );
};

export default function AuditPage() {
    const [search, setSearch] = useState('');
    const [actionFilter, setActionFilter] = useState('');
    const [page, setPage] = useState(1);
    const [showFilters, setShowFilters] = useState(false);

    const {data, isLoading, isPlaceholderData} = useQuery({
        queryKey: ['audit_logs', page, search, actionFilter],
        queryFn: () => fetchAuditLogs({
            search: search || undefined,
            action: actionFilter || undefined,
            page: page,
            page_size: 20
        }),
        placeholderData: (previousData) => previousData,
    });

    const logs = data?.results || [];
    const totalCount = data?.count || 0;
    const totalPages = Math.ceil(totalCount / 20);

    const handleExport = () => {
        const csv = [
            ['Time', 'User', 'Action', 'Target Model', 'Target ID'].join(','),
            ...logs.map((log: any) => [
                format(new Date(log.created_at), 'yyyy-MM-dd HH:mm:ss'),
                log.actor_name || 'System',
                log.action,
                log.target_model,
                log.target_id
            ].join(','))
        ].join('\n');

        const blob = new Blob([csv], {type: 'text/csv'});
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `audit-log-${format(new Date(), 'yyyy-MM-dd')}.csv`;
        a.click();
    };

    return (
        <div className="p-6 md:p-8 h-full flex flex-col bg-slate-950">

            {/* Header */}
            <div className="flex flex-col md:flex-row md:justify-between md:items-end gap-4 mb-6">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
                        <div className="p-2 bg-gradient-to-br from-purple-600 to-pink-600 rounded-xl">
                            <FileText size={28} className="text-white"/>
                        </div>
                        Audit Log
                    </h1>
                    <p className="text-slate-400">Complete system activity history</p>
                </div>

                <div className="flex gap-3">
                    <button
                        onClick={handleExport}
                        disabled={logs.length === 0}
                        className="flex items-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Download size={16}/>
                        <span className="text-sm font-medium hidden sm:inline">Export</span>
                    </button>

                    <button
                        onClick={() => setShowFilters(!showFilters)}
                        className={`flex items-center gap-2 px-4 py-2.5 border rounded-xl transition-all ${
                            showFilters || actionFilter
                                ? 'bg-blue-600 border-blue-500 text-white'
                                : 'bg-slate-800 hover:bg-slate-700 border-slate-700 text-slate-300'
                        }`}
                    >
                        <Filter size={16}/>
                        <span className="text-sm font-medium hidden sm:inline">Filters</span>
                        {actionFilter && (
                            <span className="px-1.5 py-0.5 bg-white/20 rounded text-xs">1</span>
                        )}
                    </button>
                </div>
            </div>

            {/* Filters Section */}
            {showFilters && (
                <div className="mb-6 p-6 bg-slate-900 border border-slate-800 rounded-xl animate-in slide-in-from-top-2 fade-in">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="block text-xs font-semibold text-slate-400 mb-2">Search</label>
                            <div className="relative">
                                <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"/>
                                <input
                                    type="text"
                                    placeholder="ID, user name, phone..."
                                    value={search}
                                    onChange={(e) => {
                                        setSearch(e.target.value);
                                        setPage(1);
                                    }}
                                    className="w-full bg-slate-950 border border-slate-700 rounded-lg pl-9 pr-10 py-2.5 text-sm text-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                                />
                                {search && (
                                    <button
                                        onClick={() => {
                                            setSearch('');
                                            setPage(1);
                                        }}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white"
                                    >
                                        <X size={14}/>
                                    </button>
                                )}
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-semibold text-slate-400 mb-2">Action Type</label>
                            <div className="relative">
                                <Activity size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"/>
                                <select
                                    value={actionFilter}
                                    onChange={(e) => {
                                        setActionFilter(e.target.value);
                                        setPage(1);
                                    }}
                                    className="w-full bg-slate-950 border border-slate-700 rounded-lg pl-9 pr-4 py-2.5 text-sm text-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none appearance-none transition-all cursor-pointer"
                                >
                                    <option value="">All Actions</option>
                                    <option value="LOGIN">Login</option>
                                    <option value="UPDATE">Update</option>
                                    <option value="CREATE">Create</option>
                                    <option value="RESOLVE">Resolve</option>
                                    <option value="DELETE">Delete</option>
                                </select>
                            </div>
                        </div>

                        <div className="flex items-end">
                            <button
                                onClick={() => {
                                    setSearch('');
                                    setActionFilter('');
                                    setPage(1);
                                }}
                                className="w-full px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-all text-sm font-medium"
                            >
                                Clear Filters
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Table */}
            <div className="flex-1 bg-slate-900 rounded-xl border border-slate-800 overflow-hidden flex flex-col shadow-xl">
                <div className="overflow-x-auto flex-1">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-slate-950 border-b border-slate-800 sticky top-0 z-10">
                        <tr>
                            <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">
                                Time
                            </th>
                            <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">
                                User
                            </th>
                            <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">
                                Action
                            </th>
                            <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">
                                Target
                            </th>
                            <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">
                                Changes
                            </th>
                        </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800">
                        {isLoading ? (
                            Array.from({length: 5}).map((_, i) => (
                                <tr key={i} className="animate-pulse">
                                    <td className="px-6 py-4">
                                        <div className="h-4 bg-slate-800 rounded w-32"/>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="h-4 bg-slate-800 rounded w-24"/>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="h-6 bg-slate-800 rounded w-20"/>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="h-4 bg-slate-800 rounded w-32"/>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="h-4 bg-slate-800 rounded w-40"/>
                                    </td>
                                </tr>
                            ))
                        ) : logs.length === 0 ? (
                            <tr>
                                <td colSpan={5} className="px-6 py-16 text-center">
                                    <div className="flex flex-col items-center justify-center">
                                        <div className="p-4 bg-slate-800 rounded-full mb-4">
                                            <FileText size={32} className="text-slate-600"/>
                                        </div>
                                        <h3 className="text-lg font-semibold text-white mb-1">No logs found</h3>
                                        <p className="text-sm text-slate-500">Try adjusting your filters</p>
                                    </div>
                                </td>
                            </tr>
                        ) : (
                            logs.map((log: any) => (
                                <tr
                                    key={log.id}
                                    className="hover:bg-slate-800/30 transition-colors group"
                                >
                                    <td className="px-6 py-4 font-mono text-slate-400 whitespace-nowrap">
                                        <div className="flex flex-col">
                        <span className="text-sm font-semibold text-slate-300">
                          {format(new Date(log.created_at), 'MMM dd')}
                        </span>
                                            <span className="text-xs">
                          {format(new Date(log.created_at), 'HH:mm:ss')}
                        </span>
                                        </div>
                                    </td>

                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <div
                                                className="h-8 w-8 rounded-full bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center">
                                                <User size={14} className="text-slate-400"/>
                                            </div>
                                            <div>
                                                <div className="text-sm font-semibold text-white group-hover:text-blue-400 transition-colors">
                                                    {log.actor_name || 'System'}
                                                </div>
                                                {log.actor_phone && (
                                                    <div className="text-xs text-slate-500">{log.actor_phone}</div>
                                                )}
                                            </div>
                                        </div>
                                    </td>

                                    <td className="px-6 py-4">
                                        <ActionBadge action={log.action}/>
                                    </td>

                                    <td className="px-6 py-4">
                                        <div>
                                            <div className="text-sm text-slate-300 font-medium truncate max-w-xs">
                                                {log.target_model}
                                            </div>
                                            <div className="text-xs font-mono text-slate-600 truncate">
                                                #{log.target_id}
                                            </div>
                                        </div>
                                    </td>

                                    <td className="px-6 py-4">
                                        <ChangeDetails changes={log.changes}/>
                                    </td>
                                </tr>
                            ))
                        )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
                <div className="p-4 border-t border-slate-800 flex flex-col sm:flex-row justify-between items-center gap-4 bg-slate-950">
                    <div className="text-sm text-slate-500">
                        Showing <span className="font-semibold text-slate-300">{((page - 1) * 20) + 1}</span> to{' '}
                        <span className="font-semibold text-slate-300">
              {Math.min(page * 20, totalCount)}
            </span> of{' '}
                        <span className="font-semibold text-slate-300">{totalCount}</span> entries
                    </div>

                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setPage(p => Math.max(1, p - 1))}
                            disabled={page === 1 || isLoading}
                            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed text-slate-300 text-sm font-medium"
                        >
                            <ChevronLeft size={16}/>
                            <span className="hidden sm:inline">Previous</span>
                        </button>

                        <div className="flex items-center gap-1">
                            {Array.from({length: Math.min(5, totalPages)}).map((_, i) => {
                                const pageNum = page <= 3 ? i + 1 : page - 2 + i;
                                if (pageNum > totalPages) return null;

                                return (
                                    <button
                                        key={pageNum}
                                        onClick={() => setPage(pageNum)}
                                        className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                                            page === pageNum
                                                ? 'bg-blue-600 text-white'
                                                : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                                        }`}
                                    >
                                        {pageNum}
                                    </button>
                                );
                            })}
                        </div>

                        <button
                            onClick={() => setPage(p => (data?.next ? p + 1 : p))}
                            disabled={!data?.next || isLoading}
                            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed text-slate-300 text-sm font-medium"
                        >
                            <span className="hidden sm:inline">Next</span>
                            <ChevronRight size={16}/>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}