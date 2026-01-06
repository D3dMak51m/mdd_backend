'use client';

import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '@/shared/api/analytics';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
  ArcElement,
} from 'chart.js';
import { Line, Doughnut } from 'react-chartjs-2';
import { format } from 'date-fns';
import { Loader2, RefreshCw } from 'lucide-react';

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend
);

export default function DashboardPage() {
  // Используем useQuery вместо useEffect
  const { data: stats, isLoading, isError, refetch } = useQuery({
    queryKey: ['weekly_stats'],
    queryFn: analyticsApi.getWeeklySummary,
    refetchInterval: 1000 * 60 * 5, // Авто-обновление каждые 5 минут
  });

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center text-slate-500">
        <Loader2 className="animate-spin mr-2" /> Загрузка аналитики...
      </div>
    );
  }

  if (isError || !stats) {
    return (
      <div className="p-8 text-red-400">
        Ошибка загрузки данных. <button onClick={() => refetch()} className="underline">Попробовать снова</button>
      </div>
    );
  }

  // Подготовка данных для графиков
  const labels = stats.map(s => format(new Date(s.date), 'dd MMM'));

  const lineChartData = {
    labels,
    datasets: [
      {
        label: 'Всего инцидентов',
        data: stats.map(s => s.total_incidents),
        borderColor: '#ef4444', // red-500
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Решено',
        data: stats.map(s => s.resolved_count),
        borderColor: '#10b981', // emerald-500
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  // Агрегация типов угроз за неделю
  const typeDistribution: Record<string, number> = {};
  stats.forEach(day => {
    Object.entries(day.type_distribution || {}).forEach(([type, count]) => {
      typeDistribution[type] = (typeDistribution[type] || 0) + count;
    });
  });

  const doughnutData = {
    labels: Object.keys(typeDistribution),
    datasets: [
      {
        data: Object.values(typeDistribution),
        backgroundColor: ['#ef4444', '#f97316', '#3b82f6', '#a855f7'],
        borderWidth: 0,
      },
    ],
  };

  return (
    <div className="p-6 md:p-8 overflow-y-auto h-full custom-scrollbar">
      <div className="flex justify-between items-center mb-8">
        <div>
            <h1 className="text-2xl font-bold text-white">Аналитика</h1>
            <p className="text-slate-400 text-sm">Обзор за последние 7 дней</p>
        </div>
        <button
            onClick={() => refetch()}
            className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 transition-colors"
            title="Обновить данные"
        >
            <RefreshCw size={18} />
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* График 1: Динамика (Широкий) */}
        <div className="lg:col-span-2 bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-sm">
          <h2 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-6">Динамика инцидентов</h2>
          <div className="h-72">
            <Line
                options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                    },
                    plugins: { legend: { labels: { color: '#cbd5e1' } } }
                }}
                data={lineChartData}
            />
          </div>
        </div>

        {/* График 2: Типы (Узкий) */}
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-sm">
          <h2 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-6">Типы угроз</h2>
          <div className="h-64 flex items-center justify-center">
            {Object.keys(typeDistribution).length > 0 ? (
                <Doughnut
                    options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { position: 'bottom', labels: { color: '#cbd5e1' } } }
                    }}
                    data={doughnutData}
                />
            ) : (
                <div className="text-slate-600 text-sm">Нет данных</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}