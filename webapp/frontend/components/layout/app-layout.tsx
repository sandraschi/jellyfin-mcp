'use client';

import { Sidebar } from './sidebar';

export function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="ml-64 flex-1">
        <div className="min-h-screen animate-fade-in p-8">{children}</div>
      </main>
    </div>
  );
}
