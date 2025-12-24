import React from 'react';
import Sidebar from '../components/Sidebar';
import MapWorkspace from '../components/MapWorkspace';

export default function Home() {
  return (
    <main className="flex h-screen w-full overflow-hidden bg-ops-bg text-white">
      <Sidebar />
      <MapWorkspace />
    </main>
  );
}