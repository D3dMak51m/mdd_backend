'use client';

import { useEffect, useState } from 'react';
import { analyticsApi, DailyStats } from '@/shared/api/analytics';
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
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import { format } from 'date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function DashboardPage() {
  const [stats, setStats] = useState<DailyStats[]>([]);

  useEffect(() => {
    analyticsApi.getWeeklySummary().then(setStats);
  }, []);

  if (stats.length === 0) return <div className="p-8">Loading stats...</div>;

  const labels = stats.map(s => format(new Date(s.date), 'dd MMM'));

  const lineChartData = {
    labels,
    datasets: [
      {
        label: 'Total Incidents',
        data: stats.map(s => s.total_incidents),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.5)',
      },
      {
        label: 'Resolved',
        data: stats.map(s => s.resolved_count),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.5)',
      },
    ],
  };

  const barChartData = {
    labels,
    datasets: [
      {
        label: 'Avg Response Time (sec)',
        data: stats.map(s => s.avg_response_time_seconds),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
      },
    ],
  };

  return (
    <div className="p-8 overflow-y-auto h-full">
      <h1 className="text-2xl font-bold mb-6">Analytics Dashboard (Last 7 Days)</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800">
          <h2 className="text-lg font-semibold mb-4">Incident Dynamics</h2>
          <Line options={{ responsive: true }} data={lineChartData} />
        </div>

        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800">
          <h2 className="text-lg font-semibold mb-4">Response Performance</h2>
          <Bar options={{ responsive: true }} data={barChartData} />
        </div>
      </div>
    </div>
  );
}