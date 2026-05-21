'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  Play,
  Pause,
  Square,
  SkipForward,
  SkipBack,
  Volume2,
  VolumeX,
  Activity,
  Radio,
  Monitor,
  User,
  Cpu,
  Zap,
} from 'lucide-react';
import { fetchSessions, sendPlaybackCommand } from '@/utils/api';

interface PlaybackSession {
  Id: string;
  UserName: string;
  Client: string;
  DeviceName: string;
  NowPlayingItem?: {
    Id: string;
    Name: string;
    Type: string;
    RunTimeTicks?: number;
    ProductionYear?: number;
  };
  PlayState: {
    PositionTicks?: number;
    CanSeek: boolean;
    IsPaused: boolean;
    IsMuted: boolean;
    VolumeLevel: number;
    PlayMethod: string;
  };
}

export default function PlaybackPage() {
  const [sessions, setSessions] = useState<PlaybackSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);

  const loadSessions = useCallback(async () => {
    try {
      const data = await fetchSessions();
      setSessions(data as PlaybackSession[]);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load sessions');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSessions();

    let ws: WebSocket;
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

      ws.onopen = () => setWsConnected(true);
      ws.onclose = () => setWsConnected(false);
      ws.onerror = () => setWsConnected(false);
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.sessions) {
            setSessions(data.sessions);
          } else if (data.type === 'playstate') {
            setSessions((prev) =>
              prev.map((s) =>
                s.Id === data.sessionId
                  ? { ...s, PlayState: { ...s.PlayState, ...data.state } }
                  : s,
              ),
            );
          }
        } catch {
          // ignore parse errors
        }
      };
    } catch {
      // WebSocket not available
    }

    const poll = setInterval(loadSessions, 5000);

    return () => {
      clearInterval(poll);
      if (ws) ws.close();
    };
  }, [loadSessions]);

  const handleCommand = async (sessionId: string, command: string) => {
    try {
      await sendPlaybackCommand(sessionId, command);
      loadSessions();
    } catch {
      // silently fail
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Playback Dashboard</h2>
          <p className="mt-1 text-sm text-[#777790]">Live real-time session monitoring</p>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${
              wsConnected
                ? 'bg-green-500/10 text-green-400'
                : 'bg-red-500/10 text-red-400'
            }`}
          >
            <span className={`h-2 w-2 rounded-full ${wsConnected ? 'animate-pulse bg-green-400' : 'bg-red-400'}`} />
            {wsConnected ? 'WebSocket Live' : 'WebSocket Offline'}
          </span>
          <span className="text-xs text-[#666680]">{sessions.length} active session{sessions.length !== 1 ? 's' : ''}</span>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      {loading && (
        <div className="animate-pulse space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="card">
              <div className="space-y-3">
                <div className="h-5 w-48 rounded bg-jellyfin-surface-light" />
                <div className="h-2 w-full rounded-full bg-jellyfin-surface-light" />
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && sessions.length === 0 && (
        <div className="card flex flex-col items-center py-16">
          <Activity className="mb-3 h-10 w-10 text-[#444460]" />
          <p className="text-sm text-[#666680]">No active sessions</p>
          <p className="mt-1 text-xs text-[#555570]">Start playback from any Jellyfin client to see it here</p>
        </div>
      )}

      <div className="space-y-4">
        {sessions.map((session) => (
          <SessionCard
            key={session.Id}
            session={session}
            onCommand={(cmd) => handleCommand(session.Id, cmd)}
          />
        ))}
      </div>
    </div>
  );
}

function SessionCard({
  session,
  onCommand,
}: {
  session: PlaybackSession;
  onCommand: (command: string) => void;
}) {
  const item = session.NowPlayingItem;
  const pos = session.PlayState.PositionTicks || 0;
  const total = item?.RunTimeTicks || 1;
  const progress = Math.min((pos / total) * 100, 100);

  const formatTime = (ticks: number) => {
    const s = Math.floor(ticks / 10000000);
    const m = Math.floor(s / 60);
    const h = Math.floor(m / 60);
    return `${h}:${String(m % 60).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
  };

  return (
    <div className="card space-y-4">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-jellyfin-purple/30 to-jellyfin-blue/20">
            {session.PlayState.PlayMethod === 'Transcode' ? (
              <Cpu className="h-6 w-6 text-jellyfin-blue" />
            ) : (
              <Radio className="h-6 w-6 text-jellyfin-purple" />
            )}
          </div>
          <div>
            <h3 className="font-semibold text-white">
              {item?.Name || 'Nothing playing'}
            </h3>
            <p className="text-xs text-[#666680]">
              {item?.Type || '—'} {item?.ProductionYear ? `· ${item.ProductionYear}` : ''}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="badge badge-purple">
            <Monitor className="mr-1 h-3 w-3" />
            {session.Client}
          </span>
          <span className={`badge ${session.PlayState.PlayMethod === 'Transcode' ? 'badge-blue' : 'badge-purple'}`}>
            <Zap className="mr-1 h-3 w-3" />
            {session.PlayState.PlayMethod === 'Transcode' ? 'Transcoding' : 'Direct Play'}
          </span>
        </div>
      </div>

      {item && (
        <>
          <div>
            <div className="mb-1 h-2 w-full overflow-hidden rounded-full bg-jellyfin-surface-lighter">
              <div
                className="h-full rounded-full bg-gradient-to-r from-jellyfin-purple to-jellyfin-blue transition-all duration-1000"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="flex justify-between text-[11px] text-[#555570]">
              <span>{formatTime(pos)}</span>
              <span>{formatTime(total)}</span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs text-[#666680]">
              <User className="h-3.5 w-3.5" />
              {session.UserName}
              <span className="text-[#444460]">on</span>
              {session.DeviceName}
            </div>

            <div className="flex items-center gap-1.5">
              <button
                onClick={() => onCommand('previous')}
                className="rounded-lg p-1.5 text-[#666680] transition-colors hover:bg-jellyfin-surface-light hover:text-white"
              >
                <SkipBack className="h-4 w-4" />
              </button>
              <button
                onClick={() => onCommand(session.PlayState.IsPaused ? 'play' : 'pause')}
                className="rounded-xl bg-jellyfin-purple/20 p-2 text-jellyfin-purple-light transition-all hover:bg-jellyfin-purple/30 hover:shadow-lg hover:shadow-jellyfin-purple/20"
              >
                {session.PlayState.IsPaused ? (
                  <Play className="h-5 w-5 fill-current" />
                ) : (
                  <Pause className="h-5 w-5 fill-current" />
                )}
              </button>
              <button
                onClick={() => onCommand('next')}
                className="rounded-lg p-1.5 text-[#666680] transition-colors hover:bg-jellyfin-surface-light hover:text-white"
              >
                <SkipForward className="h-4 w-4" />
              </button>
              <button
                onClick={() => onCommand('stop')}
                className="rounded-lg p-1.5 text-[#666680] transition-colors hover:bg-red-500/20 hover:text-red-400"
              >
                <Square className="h-4 w-4 fill-current" />
              </button>
              <div className="ml-2 flex items-center gap-1 text-[#666680]">
                <button
                  onClick={() => onCommand(session.PlayState.IsMuted ? 'unmute' : 'mute')}
                  className="rounded-lg p-1.5 transition-colors hover:bg-jellyfin-surface-light hover:text-white"
                >
                  {session.PlayState.IsMuted ? (
                    <VolumeX className="h-4 w-4" />
                  ) : (
                    <Volume2 className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
