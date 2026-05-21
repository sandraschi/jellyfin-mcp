'use client';

import { useState, useEffect, useCallback } from 'react';
import { Tv, Clock, Radio, Disc, Calendar, Signal } from 'lucide-react';
import { fetchLiveTvChannels, fetchEpgGuide, fetchRecordings } from '@/utils/api';

export default function LiveTvPage() {
  const [channels, setChannels] = useState<any[]>([]);
  const [epg, setEpg] = useState<any[]>([]);
  const [recordings, setRecordings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<'channels' | 'epg' | 'recordings'>('channels');

  const load = useCallback(async () => {
    try {
      const [ch, ep, rec] = await Promise.all([
        fetchLiveTvChannels(),
        fetchEpgGuide(),
        fetchRecordings(),
      ]);
      setChannels(ch as any[]);
      setEpg(ep as any[]);
      setRecordings(rec as any[]);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load Live TV data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Live TV</h2>
          <p className="mt-1 text-sm text-[#777790]">Live television &amp; DVR management</p>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      <div className="flex items-center gap-1 rounded-lg border border-[#ffffff10] bg-jellyfin-surface p-1">
        <TabButton active={tab === 'channels'} onClick={() => setTab('channels')} icon={Radio} label={`Channels (${channels.length})`} />
        <TabButton active={tab === 'epg'} onClick={() => setTab('epg')} icon={Clock} label={`EPG Guide (${epg.length})`} />
        <TabButton active={tab === 'recordings'} onClick={() => setTab('recordings')} icon={Disc} label={`Recordings (${recordings.length})`} />
      </div>

      {loading && (
        <div className="animate-pulse space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="card">
              <div className="h-5 w-48 rounded bg-jellyfin-surface-light" />
            </div>
          ))}
        </div>
      )}

      {tab === 'channels' && !loading && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {channels.map((ch: any) => (
            <div key={ch.Id || ch.Name} className="card flex items-center gap-4 p-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-jellyfin-purple/20 to-jellyfin-blue/20">
                <Signal className="h-5 w-5 text-jellyfin-purple" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-white">{ch.Name}</p>
                <p className="text-xs text-[#666680]">{ch.Number ? `Ch. ${ch.Number}` : '—'}</p>
              </div>
            </div>
          ))}
          {channels.length === 0 && (
            <div className="card col-span-full flex flex-col items-center py-16">
              <Tv className="mb-3 h-10 w-10 text-[#444460]" />
              <p className="text-sm text-[#666680]">No channels configured</p>
              <p className="mt-1 text-xs text-[#555570]">Set up a tuner in the Jellyfin dashboard</p>
            </div>
          )}
        </div>
      )}

      {tab === 'epg' && !loading && (
        <div className="space-y-2">
          {epg.length > 0 ? (
            epg.map((program: any, i: number) => (
              <div key={program.Id || i} className="card flex items-center gap-4 p-4">
                <div className="flex-shrink-0 rounded-lg bg-jellyfin-surface-light p-2">
                  <Calendar className="h-4 w-4 text-jellyfin-purple" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-white">{program.Name}</p>
                  <p className="text-xs text-[#666680]">
                    {program.ChannelName}{program.StartTime ? ` · ${program.StartTime}` : ''}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <div className="card flex flex-col items-center py-16">
              <Clock className="mb-3 h-10 w-10 text-[#444460]" />
              <p className="text-sm text-[#666680]">No EPG data available</p>
            </div>
          )}
        </div>
      )}

      {tab === 'recordings' && !loading && (
        <div className="space-y-3">
          {recordings.map((rec: any) => (
            <div key={rec.Id || rec.Name} className="card flex items-center gap-4 p-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-red-500/10">
                <Disc className="h-5 w-5 text-red-400" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-white">{rec.Name}</p>
                <p className="text-xs text-[#666680]">
                  {rec.Channel} · {rec.StartDate} · {rec.Status || 'Completed'}
                </p>
              </div>
            </div>
          ))}
          {recordings.length === 0 && (
            <div className="card flex flex-col items-center py-16">
              <Disc className="mb-3 h-10 w-10 text-[#444460]" />
              <p className="text-sm text-[#666680]">No recordings</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function TabButton({
  active,
  onClick,
  icon: Icon,
  label,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
        active
          ? 'bg-jellyfin-purple/20 text-jellyfin-purple-light'
          : 'text-[#777790] hover:text-white'
      }`}
    >
      <Icon className="h-4 w-4" />
      {label}
    </button>
  );
}
