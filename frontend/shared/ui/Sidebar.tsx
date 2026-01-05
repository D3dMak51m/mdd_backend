'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { LayoutDashboard, Map, FileText, LogOut, Shield } from 'lucide-react';

const menuItems = [
  { name: 'Live Monitor', href: '/live', icon: Map },
  { name: 'Analytics', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Audit Log', href: '/audit', icon: FileText },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    router.push('/login');
  };

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col h-screen shrink-0">
      <div className="p-6 flex items-center gap-3 border-b border-slate-800">
        <div className="h-8 w-8 bg-red-600 rounded flex items-center justify-center text-white font-bold">
          M
        </div>
        <span className="text-xl font-bold text-white tracking-tight">MDD Ops</span>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <item.icon size={20} />
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <div className="flex items-center gap-3 px-4 py-3 mb-2">
          <div className="h-8 w-8 rounded-full bg-slate-700 flex items-center justify-center text-slate-300">
            <Shield size={16} />
          </div>
          <div className="overflow-hidden">
            <p className="text-sm font-medium text-white truncate">Dispatcher</p>
            <p className="text-xs text-slate-500 truncate">Admin Role</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors text-sm"
        >
          <LogOut size={18} />
          Sign Out
        </button>
      </div>
    </aside>
  );
}