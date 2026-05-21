import {
  Activity,
  Server,
  Library,
  Film,
  Tv,
  Music,
  Image,
  Clock,
  RefreshCw,
  ScanLine,
  Database,
} from 'lucide-react';
import { fetchSystemInfo, fetchLibraries, fetchRecentActivity, fetchSessions } from '@/utils/api';

export async function OverviewDashboard() {
  let systemInfo = null;
  let libraries: unknown[] = [];
  let activity: unknown[] = [];
  let sessions: unknown[] = [];
  let error: string | null = null;

  try {
    [systemInfo, libraries, activity, sessions] = await Promise.all([
      fetchSystemInfo().catch(() => null),
      fetchLibraries().catch(() => []),
      fetchRecentActivity().catch(() => []),
      fetchSessions().catch(() => []),
    ]);
  } catch {
    error = 'Failed to load dashboard data';
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Overview</h2>
          <p className="mt-1 text-sm text-[#777790]">jellyfin-mcp server dashboard</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 rounded-full bg-green-500/10 px-3 py-1 text-xs font-medium text-green-400">
            <span className="h-2 w-2 rounded-full bg-green-400" />
            Connected
          </span>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Libraries"
          value={libraries.length}
          icon={Library}
          accent="purple"
        />
        <StatCard
          label="Active Sessions"
          value={sessions.length}
          icon={Activity}
          accent="green"
        />
        <StatCard
          label="Total Items"
          value={libraries.reduce((sum: number, l: any) => sum + (l.itemCount || 0), 0)}
          icon={Database}
          accent="blue"
        />
        <StatCard
          label="Server Version"
          value={systemInfo?.Version || '—'}
          icon={Server}
          accent="amber"
          isText
        />
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="card xl:col-span-2">
          <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
            <Library className="h-4 w-4 text-jellyfin-purple" />
            Media Libraries
          </h3>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {(libraries as any[]).map((lib: any) => (
              <LibraryCard key={lib.id || lib.name} library={lib} />
            ))}
            {libraries.length === 0 && (
              <p className="col-span-2 py-8 text-center text-sm text-[#666680]">
                No libraries configured
              </p>
            )}
          </div>
        </div>

        <div className="card">
          <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
            <Clock className="h-4 w-4 text-jellyfin-purple" />
            Recent Activity
          </h3>
          <div className="space-y-3">
            {(activity as any[]).slice(0, 8).map((a: any, i: number) => (
              <div
                key={a.id || i}
                className="flex items-center gap-3 rounded-lg border border-[#ffffff08] bg-jellyfin-darker/50 p-3"
              >
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-jellyfin-surface-light">
                  <ActivityIcon type={a.type} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-xs font-medium text-white">{a.title}</p>
                  <p className="text-[11px] text-[#666680]">{a.timestamp}</p>
                </div>
              </div>
            ))}
            {activity.length === 0 && (
              <p className="py-8 text-center text-xs text-[#666680]">No recent activity</p>
            )}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <form action={async () => { 'use server'; await fetch('http://127.0.0.1:10934/api/libraries/scan', { method: 'POST' }); }}>
          <button
            type="submit"
            className="btn-secondary inline-flex items-center gap-2 text-sm"
          >
            <ScanLine className="h-4 w-4" />
            Scan All Libraries
          </button>
        </form>
        <form action={async () => { 'use server'; await fetch('http://127.0.0.1:10934/api/libraries/refresh-metadata', { method: 'POST' }); }}>
          <button
            type="submit"
            className="btn-secondary inline-flex items-center gap-2 text-sm"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh Metadata
          </button>
        </form>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  icon: Icon,
  accent,
  isText,
}: {
  label: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  accent: 'purple' | 'green' | 'blue' | 'amber';
  isText?: boolean;
}) {
  const accentColors = {
    purple: 'bg-jellyfin-purple/15 text-jellyfin-purple border-jellyfin-purple/10',
    green: 'bg-green-500/15 text-green-400 border-green-500/10',
    blue: 'bg-jellyfin-blue/15 text-jellyfin-blue border-jellyfin-blue/10',
    amber: 'bg-amber-500/15 text-amber-400 border-amber-500/10',
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-wider text-[#666680]">{label}</p>
        <div className={`flex h-8 w-8 items-center justify-center rounded-lg border ${accentColors[accent]}`}>
          <Icon className="h-4 w-4" />
        </div>
      </div>
      <p className={`mt-3 text-2xl font-bold tracking-tight ${isText ? 'text-sm' : 'text-white'}`}>
        {value}
      </p>
    </div>
  );
}

function LibraryCard({ library }: { library: any }) {
  const typeStyles: Record<string, string> = {
    Movies: 'bg-jellyfin-purple/15 text-jellyfin-purple-light',
    Series: 'bg-jellyfin-blue/15 text-jellyfin-blue-light',
    Music: 'bg-green-500/15 text-green-400',
    Photos: 'bg-yellow-500/15 text-yellow-400',
    Books: 'bg-orange-500/15 text-orange-400',
    HomeVideos: 'bg-pink-500/15 text-pink-400',
  };

  const typeIcons: Record<string, React.ReactNode> = {
    Movies: <Film className="h-3.5 w-3.5" />,
    Series: <Tv className="h-3.5 w-3.5" />,
    Music: <Music className="h-3.5 w-3.5" />,
    Photos: <Image className="h-3.5 w-3.5" />,
  };

  const style = typeStyles[library.type] || typeStyles.Movies;

  return (
    <div className="rounded-lg border border-[#ffffff08] bg-jellyfin-darker/50 p-4 transition-colors hover:border-jellyfin-purple/20">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-white">{library.name}</p>
        <span className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-[11px] font-medium ${style}`}>
          {typeIcons[library.type]}
          {library.type}
        </span>
      </div>
      <p className="mt-2 text-2xl font-bold text-white">{library.itemCount ?? '—'}</p>
      <p className="text-[11px] text-[#666680]">items</p>
    </div>
  );
}

function ActivityIcon({ type }: { type: string }) {
  const icons: Record<string, React.ReactNode> = {
    scan: <ScanLine className="h-4 w-4 text-jellyfin-purple" />,
    play: <Activity className="h-4 w-4 text-green-400" />,
    add: <Database className="h-4 w-4 text-jellyfin-blue" />,
    update: <RefreshCw className="h-4 w-4 text-amber-400" />,
  };
  return <>{icons[type] || <Clock className="h-4 w-4 text-[#666680]" />}</>;
}
