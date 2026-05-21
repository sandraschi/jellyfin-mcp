'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  Brain,
  Search,
  RefreshCw,
  Database,
  FileText,
  Loader2,
  Sparkles,
  BarChart3,
} from 'lucide-react';
import { fetchRagStatus, syncRag, searchRag } from '@/utils/api';

interface RagStatus {
  status: string;
  documentCount?: number;
  lastSync?: string;
}

export default function RagPage() {
  const [status, setStatus] = useState<RagStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await fetchRagStatus();
      setStatus(data as RagStatus);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load RAG status');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await syncRag();
      await load();
    } catch (err: any) {
      setError(err.message || 'Sync failed');
    } finally {
      setSyncing(false);
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) return;
    setSearching(true);
    setError(null);
    try {
      const data = await searchRag(query);
      const d = data as any;
      setResults(d.results || d || []);
    } catch (err: any) {
      setError(err.message || 'RAG search failed');
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">RAG Search</h2>
          <p className="mt-1 text-sm text-[#777790]">Semantic search across your media library</p>
        </div>
        <button
          onClick={handleSync}
          disabled={syncing}
          className="btn-primary inline-flex items-center gap-2 text-sm"
        >
          {syncing ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4" />
          )}
          {syncing ? 'Syncing...' : 'Sync Index'}
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-jellyfin-purple/15">
              <Database className="h-5 w-5 text-jellyfin-purple" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{status?.documentCount ?? '—'}</p>
              <p className="text-xs text-[#666680]">Documents</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-green-500/15">
              <BarChart3 className="h-5 w-5 text-green-400" />
            </div>
            <div>
              <p className="text-lg font-semibold text-white capitalize">{status?.status || 'Unknown'}</p>
              <p className="text-xs text-[#666680]">Status</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-jellyfin-blue/15">
              <FileText className="h-5 w-5 text-jellyfin-blue" />
            </div>
            <div>
              <p className="text-sm font-medium text-white">
                {status?.lastSync || 'Never'}
              </p>
              <p className="text-xs text-[#666680]">Last Sync</p>
            </div>
          </div>
        </div>
      </div>

      <div className="card space-y-4">
        <h3 className="flex items-center gap-2 text-sm font-semibold text-white">
          <Brain className="h-4 w-4 text-jellyfin-purple" />
          Semantic Search
        </h3>
        <div className="flex gap-3">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search using natural language... e.g. 'dark sci-fi movies with great soundtracks'"
            className="input-field flex-1"
          />
          <button
            onClick={handleSearch}
            disabled={searching || !query.trim()}
            className="btn-primary inline-flex items-center gap-2"
          >
            {searching ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Search className="h-4 w-4" />
            )}
            Search
          </button>
        </div>
      </div>

      {results.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-sm text-[#777790]">
            <Sparkles className="h-4 w-4 text-jellyfin-purple" />
            {results.length} result{results.length !== 1 ? 's' : ''}
          </div>
          {results.map((result: any, i: number) => (
            <div key={result.id || i} className="card flex gap-4">
              <div className="flex-shrink-0">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-jellyfin-purple/15">
                  <FileText className="h-5 w-5 text-jellyfin-purple" />
                </div>
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-white">{result.title || result.Name || `Result ${i + 1}`}</p>
                <p className="mt-1 text-xs text-[#777790] line-clamp-3">
                  {result.content || result.text || result.description || ''}
                </p>
                {(result.score || result.metadata?.score) && (
                  <div className="mt-2 flex items-center gap-2">
                    <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-jellyfin-surface-lighter">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-jellyfin-purple to-jellyfin-blue"
                        style={{ width: `${((result.score || result.metadata?.score) * 100).toFixed(0)}%` }}
                      />
                    </div>
                    <span className="text-[11px] text-[#666680]">
                      {((result.score || result.metadata?.score) * 100).toFixed(1)}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {searching && (
        <div className="animate-pulse space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="card">
              <div className="flex gap-4">
                <div className="h-10 w-10 rounded-lg bg-jellyfin-surface-light" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-48 rounded bg-jellyfin-surface-light" />
                  <div className="h-3 w-full rounded bg-jellyfin-surface-light" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
