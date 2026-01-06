'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '@/shared/api/analytics'; // Убедитесь, что метод getAuditLogs принимает params
import { format } from 'date-fns';
import { Search, Filter, Loader2, ChevronLeft, ChevronRight } from 'lucide-react';
import { apiClient } from '@/shared/api/client';

// Обновим API вызов прямо здесь или в analytics.ts
const fetchAuditLogs = async (params: any) => {
    const { data } = await apiClient.get('/audit/', { params });
    return data;
};

export default function AuditPage() {
  const [search, setSearch] = useState('');
  const [actionFilter, setActionFilter] = useState('');
  const [page, setPage] = useState(1);

  // React Query с зависимостями от фильтров
  const { data, isLoading, isPlaceholderData } = useQuery({
    queryKey: ['audit_logs', page, search, actionFilter],
    queryFn: () => fetchAuditLogs({
        search: search || undefined,
        action: actionFilter || undefined,
        page: page,
        page_size: 20 // Размер страницы
    }),
    placeholderData: (previousData) => previousData, // Плавный переход при пагинации
  });

  const logs = data?.results || [];
  const totalCount = data?.count || 0;
  const totalPages = Math.ceil(totalCount / 20);

  return (
    <div className="p-6 md:p-8 h-full flex flex-col">
      <div className="flex justify-between items-end mb-6">
        <div>
            <h1 className="text-2xl font-bold text-white">Журнал Аудита</h1>
            <p className="text-slate-400 text-sm mt-1">История действий пользователей и системы</p>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="bg-slate-900 p-4 rounded-xl border border-slate-800 mb-6 flex gap-4 flex-wrap">
        <div className="flex-1 relative min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
            <input
                type="text"
                placeholder="Поиск по ID, имени..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-sm text-white focus:border-blue-500 outline-none"
            />
        </div>
        <div className="relative w-48">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
            <select
                value={actionFilter}
                onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-sm text-white focus:border-blue-500 outline-none appearance-none"
            >
                <option value="">Все действия</option>
                <option value="LOGIN">Login</option>
                <option value="UPDATE">Update</option>
                <option value="CREATE">Create</option>
                <option value="RESOLVE">Resolve</option>
            </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900 rounded-xl border border-slate-800 flex-1 overflow-hidden flex flex-col">
        <div className="overflow-x-auto flex-1">
            <table className="w-full text-left text-sm text-slate-400">
            <thead className="bg-slate-950 text-slate-200 uppercase font-medium text-xs">
                <tr>
                <th className="px-6 py-4">Время</th>
                <th className="px-6 py-4">Пользователь</th>
                <th className="px-6 py-4">Действие</th>
                <th className="px-6 py-4">Объект</th>
                <th className="px-6 py-4">Изменения</th>
                </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
                {isLoading ? (
                    <tr>
                        <td colSpan={5} className="px-6 py-12 text-center">
                            <Loader2 className="animate-spin mx-auto mb-2" /> Загрузка...
                        </td>
                    </tr>
                ) : logs.length === 0 ? (
                    <tr>
                        <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                            Записей не найдено
                        </td>
                    </tr>
                ) : (
                    logs.map((log: any) => (
                    <tr key={log.id} className="hover:bg-slate-800/50 transition-colors">
                        <td className="px-6 py-4 font-mono whitespace-nowrap">
                        {format(new Date(log.created_at), 'dd MMM HH:mm')}
                        </td>
                        <td className="px-6 py-4">
                        <div className="text-white font-medium">{log.actor_name || 'System'}</div>
                        <div className="text-xs opacity-70">{log.actor_phone}</div>
                        </td>
                        <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wide ${
                            log.action === 'LOGIN' ? 'bg-green-500/10 text-green-500 border border-green-500/20' :
                            log.action === 'UPDATE' ? 'bg-blue-500/10 text-blue-500 border border-blue-500/20' :
                            log.action === 'RESOLVE' ? 'bg-purple-500/10 text-purple-500 border border-purple-500/20' :
                            'bg-slate-700 text-slate-300'
                        }`}>
                            {log.action}
                        </span>
                        </td>
                        <td className="px-6 py-4">
                        <div className="text-slate-300">{log.target_model}</div>
                        <div className="text-xs font-mono text-slate-600">#{log.target_id}</div>
                        </td>
                        <td className="px-6 py-4">
                        {log.changes && Object.keys(log.changes).length > 0 ? (
                            <div className="text-xs bg-slate-950 p-2 rounded border border-slate-800 max-w-xs overflow-hidden">
                                {Object.entries(log.changes).map(([key, val]: any) => (
                                    <div key={key} className="truncate">
                                        <span className="text-slate-500">{key}:</span>{' '}
                                        <span className="text-slate-300">{String(val.new).slice(0, 20)}</span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <span className="text-slate-700">-</span>
                        )}
                        </td>
                    </tr>
                    ))
                )}
            </tbody>
            </table>
        </div>

        {/* Pagination */}
        <div className="p-4 border-t border-slate-800 flex justify-between items-center bg-slate-950">
            <span className="text-xs text-slate-500">
                Страница {page} из {totalPages || 1}
            </span>
            <div className="flex gap-2">
                <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1 || isLoading}
                    className="p-2 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <ChevronLeft size={16} />
                </button>
                <button
                    onClick={() => setPage(p => (data?.next ? p + 1 : p))}
                    disabled={!data?.next || isLoading}
                    className="p-2 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <ChevronRight size={16} />
                </button>
            </div>
        </div>
      </div>
    </div>
  );
}