// frontend/app/(protected)/dashboard/page.tsx
'use client';
import {useQuery} from '@tanstack/react-query';
import {analyticsApi} from '@/shared/api/analytics';
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
    Filler,
} from 'chart.js';
import {Line, Doughnut} from 'react-chartjs-2';
import {format} from 'date-fns';
import {
    Loader2, RefreshCw, TrendingUp, TrendingDown, AlertTriangle,
    Activity, CheckCircle, Clock, PieChart
} from 'lucide-react';

ChartJS.register(
    CategoryScale, LinearScale, PointElement, LineElement,
    BarElement, ArcElement, Title, Tooltip, Legend, Filler
);

// KPI Card Component with proper typing
type ColorVariant = 'blue' | 'red' | 'green' | 'purple' | 'yellow';

interface KPICardProps {
    title: string;
    value: string | number;
    trend?: number;
    trendValue?: string;
    icon: React.ComponentType<{ size?: number; className?: string }>;
    color?: ColorVariant;
    loading?: boolean;
}

const KPICard = ({
                     title,
                     value,
                     trend,
                     trendValue,
                     icon: Icon,
                     color = 'blue',
                     loading = false
                 }: KPICardProps) => {
    const colors: Record<ColorVariant, string> = {
        blue: 'from-blue-600 to-cyan-600',
        red: 'from-red-600 to-orange-600',
        green: 'from-green-600 to-emerald-600',
        purple: 'from-purple-600 to-pink-600',
        yellow: 'from-yellow-600 to-orange-600'
    };

    const iconColors: Record<ColorVariant, string> = {
        blue: 'text-blue-400',
        red: 'text-red-400',
        green: 'text-green-400',
        purple: 'text-purple-400',
        yellow: 'text-yellow-400'
    };

    return (
        <div
            className="relative overflow-hidden bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all duration-300 group">
            {/* Background Gradient */}
            <div
                className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${colors[color]} opacity-10 rounded-full blur-3xl group-hover:opacity-20 transition-opacity`}/>

            <div className="relative z-10">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                    <div className={`p-3 bg-gradient-to-br ${colors[color]} rounded-xl shadow-lg`}>
                        <Icon size={24} className="text-white"/>
                    </div>

                    {trend !== undefined && (
                        <div className={`flex items-center gap-1 text-xs font-bold ${
                            trend > 0 ? 'text-green-400' : trend < 0 ? 'text-red-400' : 'text-slate-500'
                        }`}>
                            {trend > 0 ? (
                                <TrendingUp size={14}/>
                            ) : trend < 0 ? (
                                <TrendingDown size={14}/>
                            ) : null}
                            {trendValue || `${Math.abs(trend)}%`}
                        </div>
                    )}
                </div>

                {/* Value */}
                <div className="mb-2">
                    {loading ? (
                        <div className="h-10 bg-slate-800 rounded animate-pulse w-24"/>
                    ) : (
                        <div className="text-4xl font-bold text-white">
                            {value}
                        </div>
                    )}
                </div>

                {/* Title */}
                <div className="text-sm text-slate-400 font-medium">
                    {title}
                </div>
            </div>
        </div>
    );
};

// Chart Card Component
interface ChartCardProps {
    title: string;
    children: React.ReactNode;
    className?: string;
}

const ChartCard = ({title, children, className = ''}: ChartCardProps) => (
    <div className={`bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all ${className}`}>
        <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
            <div className="h-1 w-1 rounded-full bg-blue-500"/>
            {title}
        </h3>
        {children}
    </div>
);

export default function DashboardPage() {
    const {data: stats, isLoading, isError, refetch, isFetching} = useQuery({
        queryKey: ['weekly_stats'],
        queryFn: analyticsApi.getWeeklySummary,
        refetchInterval: 1000 * 60 * 5,
    });

    if (isLoading) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="text-center">
                    <Loader2 className="animate-spin mx-auto mb-4 text-blue-500" size={48}/>
                    <p className="text-slate-400">Loading analytics...</p>
                </div>
            </div>
        );
    }

    if (isError || !stats) {
        return (
            <div className="p-8 text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-red-500/10 rounded-full mb-4">
                    <AlertTriangle className="text-red-500" size={32}/>
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Failed to load data</h3>
                <p className="text-slate-400 mb-4">There was an error loading the analytics</p>
                <button
                    onClick={() => refetch()}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
                >
                    Try Again
                </button>
            </div>
        );
    }

    // Calculate KPIs
    const totalIncidents = stats.reduce((sum, s) => sum + s.total_incidents, 0);
    const totalResolved = stats.reduce((sum, s) => sum + s.resolved_count, 0);
    const avgResponseTime = stats.reduce((sum, s) => sum + s.avg_response_time_seconds, 0) / stats.length;
    const todayIncidents = stats[stats.length - 1]?.total_incidents || 0;

    // Type distribution
    const typeDistribution: Record<string, number> = {};
    stats.forEach(day => {
        Object.entries(day.type_distribution || {}).forEach(([type, count]) => {
            typeDistribution[type] = (typeDistribution[type] || 0) + count;
        });
    });

    // Chart data
    const labels = stats.map(s => format(new Date(s.date), 'MMM dd'));

    const lineChartData = {
        labels,
        datasets: [
            {
                label: 'Total Incidents',
                data: stats.map(s => s.total_incidents),
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 6,
                pointHoverRadius: 8,
                pointBackgroundColor: '#ef4444',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
            },
            {
                label: 'Resolved',
                data: stats.map(s => s.resolved_count),
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 6,
                pointHoverRadius: 8,
                pointBackgroundColor: '#10b981',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
            },
        ],
    };

    const lineChartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top' as const,
                labels: {
                    color: '#cbd5e1',
                    usePointStyle: true,
                    padding: 20,
                    font: {
                        size: 12,
                        weight: 600 as const  // Fix: use const assertion
                    }
                }
            },
            tooltip: {
                backgroundColor: '#1e293b',
                titleColor: '#fff',
                bodyColor: '#cbd5e1',
                borderColor: '#334155',
                borderWidth: 1,
                padding: 12,
                displayColors: true,
                callbacks: {
                    label: (context: any) => {
                        return `${context.dataset.label}: ${context.parsed.y}`;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {color: '#1e293b', drawBorder: false},
                ticks: {
                    color: '#94a3b8',
                    font: {size: 11},
                    padding: 8
                },
                border: {display: false}
            },
            x: {
                grid: {display: false, drawBorder: false},
                ticks: {
                    color: '#94a3b8',
                    font: {size: 11},
                    padding: 8
                },
                border: {display: false}
            }
        },
        interaction: {
            intersect: false,
            mode: 'index' as const,
        }
    };

    const doughnutData = {
        labels: Object.keys(typeDistribution),
        datasets: [
            {
                data: Object.values(typeDistribution),
                backgroundColor: [
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(251, 146, 60, 0.8)',
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(168, 85, 247, 0.8)',
                    'rgba(236, 72, 153, 0.8)',
                ],
                borderColor: [
                    '#ef4444',
                    '#fb923c',
                    '#3b82f6',
                    '#a855f7',
                    '#ec4899',
                ],
                borderWidth: 2,
                hoverOffset: 10,
            },
        ],
    };

    const doughnutOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right' as const,
                labels: {
                    color: '#cbd5e1',
                    usePointStyle: true,
                    padding: 15,
                    font: {size: 12}
                }
            },
            tooltip: {
                backgroundColor: '#1e293b',
                titleColor: '#fff',
                bodyColor: '#cbd5e1',
                borderColor: '#334155',
                borderWidth: 1,
                padding: 12,
            }
        },
        cutout: '70%',
    };

    return (
        <div className="p-6 md:p-8 overflow-y-auto h-full custom-scrollbar bg-slate-950">
            <div className="max-w-7xl mx-auto space-y-8">

                {/* Header */}
                <div className="flex justify-between items-end">
                    <div>
                        <h1 className="text-3xl font-bold text-white mb-2">Analytics Dashboard</h1>
                        <p className="text-slate-400">Last 7 days overview</p>
                    </div>
                    <button
                        onClick={() => refetch()}
                        disabled={isFetching}
                        className="flex items-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 rounded-xl transition-all disabled:opacity-50"
                    >
                        <RefreshCw size={16} className={isFetching ? 'animate-spin' : ''}/>
                        <span className="text-sm font-medium">Refresh</span>
                    </button>
                </div>

                {/* KPI Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <KPICard
                        title="Total Incidents"
                        value={totalIncidents}
                        icon={Activity}
                        color="red"
                        trend={todayIncidents > 0 ? 5 : 0}
                    />
                    <KPICard
                        title="Resolved Cases"
                        value={totalResolved}
                        icon={CheckCircle}
                        color="green"
                        trend={totalResolved > 0 ? 8 : 0}
                    />
                    <KPICard
                        title="Avg Response Time"
                        value={`${Math.round(avgResponseTime / 60)}m`}
                        icon={Clock}
                        color="blue"
                        trend={-2}
                    />
                    <KPICard
                        title="Today's Incidents"
                        value={todayIncidents}
                        icon={AlertTriangle}
                        color="yellow"
                        trendValue="Today"
                    />
                </div>

                {/* Charts Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    {/* Line Chart */}
                    <ChartCard title="Incident Timeline" className="lg:col-span-2">
                        <div className="h-80">
                            <Line options={lineChartOptions} data={lineChartData}/>
                        </div>
                    </ChartCard>

                    {/* Doughnut Chart */}
                    <ChartCard title="Incident Types">
                        <div className="h-80 flex items-center justify-center">
                            {Object.keys(typeDistribution).length > 0 ? (
                                <Doughnut options={doughnutOptions} data={doughnutData}/>
                            ) : (
                                <div className="text-center text-slate-500">
                                    <PieChart size={48} className="mx-auto mb-2 opacity-50"/>
                                    <p className="text-sm">No data available</p>
                                </div>
                            )}
                        </div>
                    </ChartCard>
                </div>

                {/* Stats Table */}
                <ChartCard title="Daily Breakdown">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm">
                            <thead className="text-xs text-slate-400 uppercase border-b border-slate-800">
                            <tr>
                                <th className="px-4 py-3 font-semibold">Date</th>
                                <th className="px-4 py-3 font-semibold text-right">Incidents</th>
                                <th className="px-4 py-3 font-semibold text-right">Resolved</th>
                                <th className="px-4 py-3 font-semibold text-right">Response Time</th>
                                <th className="px-4 py-3 font-semibold text-right">Resolution %</th>
                            </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800">
                            {stats.slice().reverse().map((stat) => {
                                const resolutionRate = stat.total_incidents > 0
                                    ? ((stat.resolved_count / stat.total_incidents) * 100).toFixed(0)
                                    : 0;

                                return (
                                    <tr key={stat.date} className="hover:bg-slate-800/30 transition-colors">
                                        <td className="px-4 py-3 text-slate-300 font-medium">
                                            {format(new Date(stat.date), 'MMM dd, yyyy')}
                                        </td>
                                        <td className="px-4 py-3 text-right text-red-400 font-semibold">
                                            {stat.total_incidents}
                                        </td>
                                        <td className="px-4 py-3 text-right text-green-400 font-semibold">
                                            {stat.resolved_count}
                                        </td>
                                        <td className="px-4 py-3 text-right text-blue-400 font-mono">
                                            {Math.round(stat.avg_response_time_seconds / 60)}m
                                        </td>
                                        <td className="px-4 py-3 text-right">
                        <span className={`inline-flex px-2 py-1 rounded-full text-xs font-bold ${
                            Number(resolutionRate) >= 80 ? 'bg-green-500/10 text-green-400' :
                                Number(resolutionRate) >= 50 ? 'bg-yellow-500/10 text-yellow-400' :
                                    'bg-red-500/10 text-red-400'
                        }`}>
                          {resolutionRate}%
                        </span>
                                        </td>
                                    </tr>
                                );
                            })}
                            </tbody>
                        </table>
                    </div>
                </ChartCard>
            </div>

            <style jsx global>{`
                .custom-scrollbar::-webkit-scrollbar {
                    width: 8px;
                    height: 8px;
                }

                .custom-scrollbar::-webkit-scrollbar-track {
                    background: #0f172a;
                }

                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background: #475569;
                    border-radius: 4px;
                }

                .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                    background: #64748b;
                }
            `}</style>
        </div>
    );
}