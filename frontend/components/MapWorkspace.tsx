import React from 'react';

export default function MapWorkspace() {
  return (
    <div className="flex-1 relative bg-slate-950 flex items-center justify-center">
      {/* Сетка для эффекта карты */}
      <div className="absolute inset-0 opacity-10"
           style={{
             backgroundImage: 'linear-gradient(#334155 1px, transparent 1px), linear-gradient(90deg, #334155 1px, transparent 1px)',
             backgroundSize: '40px 40px'
           }}>
      </div>

      <div className="z-10 text-center">
        <h1 className="text-3xl font-bold text-slate-600">MAP WORKSPACE</h1>
        <p className="text-slate-500">Waiting for GPS signal...</p>
      </div>
    </div>
  );
}