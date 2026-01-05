'use client';

import { useEffect, useState } from 'react';
import { analyticsApi, AuditLog } from '@/shared/api/analytics';
import { format } from 'date-fns';

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);

  useEffect(() => {
    analyticsApi.getAuditLogs().then(setLogs);
  }, []);

  return (
    <div className="p-8 overflow-y-auto h-full">
      <h1 className="text-2xl font-bold mb-6">System Audit Log</h1>

      <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
        <table className="w-full text-left text-sm text-slate-400">
          <thead className="bg-slate-800 text-slate-200 uppercase font-medium">
            <tr>
              <th className="px-6 py-4">Time</th>
              <th className="px-6 py-4">Actor</th>
              <th className="px-6 py-4">Action</th>
              <th className="px-6 py-4">Target</th>
              <th className="px-6 py-4">Changes</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {logs.map((log) => (
              <tr key={log.id} className="hover:bg-slate-800/50">
                <td className="px-6 py-4 font-mono">
                  {format(new Date(log.created_at), 'dd MMM HH:mm:ss')}
                </td>
                <td className="px-6 py-4">
                  <div className="text-white">{log.actor_name || 'System'}</div>
                  <div className="text-xs">{log.actor_phone}</div>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${
                    log.action === 'LOGIN' ? 'bg-green-500/10 text-green-500' :
                    log.action === 'UPDATE' ? 'bg-blue-500/10 text-blue-500' :
                    'bg-slate-700 text-slate-300'
                  }`}>
                    {log.action}
                  </span>
                </td>
                <td className="px-6 py-4">
                  {log.target_model} <br/>
                  <span className="text-xs font-mono text-slate-500">ID: {log.target_id}</span>
                </td>
                <td className="px-6 py-4">
                  <pre className="text-xs bg-slate-950 p-2 rounded max-w-xs overflow-x-auto">
                    {JSON.stringify(log.changes, null, 2)}
                  </pre>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}