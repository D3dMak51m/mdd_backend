// frontend/shared/ui/Sidebar.tsx
'use client';
import Link from 'next/link';
import {usePathname, useRouter} from 'next/navigation';
import {
    LayoutDashboard, Map, FileText, LogOut, Shield,
    Users, ChevronRight, Radio, Bell, Settings
} from 'lucide-react';
import {useIncidentStore} from '@/shared/stores/incident-store';

const menuItems = [
    {
        name: 'Live Monitor',
        href: '/live',
        icon: Map,
        description: 'Real-time incident tracking',
        badge: 'live'
    },
    {
        name: 'Analytics',
        href: '/dashboard',
        icon: LayoutDashboard,
        description: 'Statistics & insights'
    },
    {
        name: 'Audit Log',
        href: '/audit',
        icon: FileText,
        description: 'Activity history'
    },
];

export default function Sidebar() {
    const pathname = usePathname();
    const router = useRouter();
    const {onlineUsers, getSortedIncidents} = useIncidentStore();

    // Fix: Use status instead of resolved
    const activeIncidents = getSortedIncidents().filter(i => i.status !== 'RESOLVED');

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        router.push('/login');
    };

    return (
        <aside
            className="w-72 bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 border-r border-slate-800/50 flex flex-col h-screen shrink-0 shadow-2xl">

            {/* Logo & Brand */}
            <div className="p-6 border-b border-slate-800/50">
                <div className="flex items-center gap-3 mb-2">
                    <div className="relative">
                        <div className="absolute inset-0 bg-red-500 rounded-lg blur-xl opacity-30 animate-pulse"/>
                        <div
                            className="relative h-10 w-10 bg-gradient-to-br from-red-600 to-orange-600 rounded-lg flex items-center justify-center shadow-lg">
                            <Shield className="text-white" size={24}/>
                        </div>
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-white tracking-tight">MDD Control</h1>
                        <p className="text-xs text-slate-500">Dispatch System</p>
                    </div>
                </div>
            </div>

            {/* Status Card */}
            <div className="px-4 py-3 border-b border-slate-800/50">
                <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-4 border border-slate-700/50">
                    <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              System Status
            </span>
                        <div className="flex items-center gap-1.5">
                            <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]"/>
                            <span className="text-xs font-semibold text-green-400">Operational</span>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                        <div className="text-center">
                            <div className="text-2xl font-bold text-red-500 mb-1">
                                {activeIncidents.length}
                            </div>
                            <div className="text-[10px] text-slate-500 uppercase tracking-wide">Active</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-blue-500 mb-1">
                                {onlineUsers.length}
                            </div>
                            <div className="text-[10px] text-slate-500 uppercase tracking-wide">Online</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-2 overflow-y-auto custom-scrollbar">
                {menuItems.map((item) => {
                    const isActive = pathname.startsWith(item.href);

                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`
                group flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all duration-200
                ${isActive
                                ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-900/30'
                                : 'text-slate-400 hover:bg-slate-800/50 hover:text-white'
                            }
              `}
                        >
                            <div className={`
                p-2 rounded-lg transition-all
                ${isActive
                                ? 'bg-white/10'
                                : 'bg-slate-800 group-hover:bg-slate-700'
                            }
              `}>
                                <item.icon size={20}/>
                            </div>

                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                    <span className="font-semibold text-sm">{item.name}</span>
                                    {item.badge === 'live' && (
                                        <span
                                            className="flex items-center gap-1 px-1.5 py-0.5 bg-red-500/20 border border-red-500/30 rounded text-[10px] font-bold text-red-400 uppercase">
                      <Radio size={8} className="animate-pulse"/>
                      Live
                    </span>
                                    )}
                                </div>
                                <p className="text-xs opacity-70 truncate">
                                    {item.description}
                                </p>
                            </div>

                            <ChevronRight
                                size={16}
                                className={`
                  transition-transform
                  ${isActive ? 'translate-x-0 opacity-100' : '-translate-x-1 opacity-0 group-hover:translate-x-0 group-hover:opacity-100'}
                `}
                            />
                        </Link>
                    );
                })}
            </nav>

            {/* Team Section */}
            {onlineUsers.length > 0 && (
                <div className="px-4 py-4 border-t border-slate-800/50">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
                            <Users size={14}/>
                            Team Online
                        </h3>
                        <span className="px-2 py-0.5 bg-green-500/10 text-green-400 rounded-full text-[10px] font-bold border border-green-500/20">
              {onlineUsers.length}
            </span>
                    </div>

                    <div className="space-y-2 max-h-32 overflow-y-auto custom-scrollbar">
                        {onlineUsers.slice(0, 5).map(user => (
                            <div
                                key={user.id}
                                className="flex items-center gap-2.5 px-3 py-2 bg-slate-800/30 rounded-lg hover:bg-slate-800/50 transition-colors group"
                            >
                                <div className="relative">
                                    <div
                                        className="h-8 w-8 rounded-full bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center border-2 border-slate-700 group-hover:border-slate-600 transition-colors">
                    <span className="text-xs font-bold text-slate-300">
                      {user.full_name?.[0] || user.email?.[0] || 'D'}
                    </span>
                                    </div>
                                    <div
                                        className="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full bg-green-500 border-2 border-slate-900 shadow-[0_0_6px_rgba(34,197,94,0.5)]"/>
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium text-slate-200 truncate">
                                        {user.full_name || user.email || 'Dispatcher'}
                                    </p>
                                    <p className="text-xs text-slate-500">Active now</p>
                                </div>
                            </div>
                        ))}

                        {onlineUsers.length > 5 && (
                            <div className="text-center py-1">
                <span className="text-xs text-slate-600">
                  +{onlineUsers.length - 5} more
                </span>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* User Profile & Logout */}
            <div className="p-4 border-t border-slate-800/50 bg-slate-900/50">
                <div className="flex items-center gap-3 px-3 py-3 mb-3 bg-slate-800/50 rounded-xl border border-slate-700/50">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center shadow-lg">
                        <Shield size={20} className="text-white"/>
                    </div>
                    <div className="flex-1 overflow-hidden">
                        <p className="text-sm font-semibold text-white truncate">Dispatcher</p>
                        <p className="text-xs text-slate-500 truncate">Administrator</p>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                    <button
                        className="flex items-center justify-center gap-2 px-3 py-2.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-all text-sm">
                        <Settings size={16}/>
                    </button>

                    <button
                        onClick={handleLogout}
                        className="flex items-center justify-center gap-2 px-3 py-2.5 text-red-400 hover:text-white hover:bg-red-500/10 border border-transparent hover:border-red-500/20 rounded-lg transition-all text-sm"
                    >
                        <LogOut size={16}/>
                    </button>
                </div>
            </div>

            {/* Custom Scrollbar Styles */}
            <style jsx global>{`
                .custom-scrollbar::-webkit-scrollbar {
                    width: 4px;
                }

                .custom-scrollbar::-webkit-scrollbar-track {
                    background: transparent;
                }

                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background: #475569;
                    border-radius: 2px;
                }

                .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                    background: #64748b;
                }
            `}</style>
        </aside>
    );
}