'use client';

import { useState, useCallback, useRef } from 'react';
import { Search, X, Film, Tv, Music, Image, BookOpen, Star } from 'lucide-react';
import { fetchSearch } from '@/utils/api';
import { jellyfinImageUrl, formatRuntime } from '@/utils/jellyfin-media';

const typeFilters = [
  { label: 'All', value: '' },
  { label: 'Movies', value: 'Movie' },
  { label: 'Series', value: 'Series' },
  { label: 'Music', value: 'MusicAlbum' },
  { label: 'Photos', value: 'Photo' },
  { label: 'Books', value: 'Book' },
];

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searched, setSearched] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSearch = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const data = await fetchSearch(query);
      const filtered = activeFilter
        ? (data as any[]).filter((item) => item.Type === activeFilter)
        : data;
      setResults(filtered as any[]);
      setSearched(true);
    } catch (err: any) {
      setError(err.message || 'Search failed');
    } finally {
      setLoading(false);
    }
  }, [query, activeFilter]);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Search</h2>
        <p className="mt-1 text-sm text-[#777790]">Search across all media libraries</p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[#666680]" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search movies, series, music..."
            className="input-field pl-11 pr-10 text-base"
          />
          {query && (
            <button
              type="button"
              onClick={() => { setQuery(''); setResults([]); setSearched(false); }}
              className="absolute right-3 top-1/2 -translate-y-1/2 rounded p-0.5 text-[#666680] hover:text-white"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
        <button type="submit" className="btn-primary px-6" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      <div className="flex items-center gap-2">
        {typeFilters.map((f) => (
          <button
            key={f.value}
            onClick={() => setActiveFilter(f.value)}
            className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
              activeFilter === f.value
                ? 'bg-jellyfin-purple/20 text-jellyfin-purple-light'
                : 'text-[#777790] hover:bg-jellyfin-surface hover:text-white'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      {loading && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="animate-pulse rounded-xl bg-jellyfin-surface p-4">
              <div className="flex gap-4">
                <div className="h-20 w-14 rounded-lg bg-jellyfin-surface-light" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-32 rounded bg-jellyfin-surface-light" />
                  <div className="h-3 w-20 rounded bg-jellyfin-surface-light" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {searched && !loading && results.length === 0 && (
        <div className="card flex flex-col items-center py-16">
          <Search className="mb-3 h-10 w-10 text-[#444460]" />
          <p className="text-sm text-[#666680]">No results found</p>
          <p className="mt-1 text-xs text-[#555570]">Try a different search term</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {results.map((item: any) => (
            <SearchResultCard key={item.Id} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}

function SearchResultCard({ item }: { item: any }) {
  const imageUrl = item.Id ? jellyfinImageUrl(item.Id, 'Primary', 0, { width: 200, quality: 70 }) : null;

  return (
    <div className="card glass-hover flex gap-4 p-4">
      <div className="h-20 w-14 flex-shrink-0 overflow-hidden rounded-lg bg-jellyfin-surface-light">
        {imageUrl ? (
          <img src={imageUrl} alt={item.Name} className="h-full w-full object-cover" loading="lazy" />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-jellyfin-purple/20 to-jellyfin-blue/20">
            <Film className="h-5 w-5 text-jellyfin-purple/40" />
          </div>
        )}
      </div>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-white">{item.Name}</p>
        <p className="text-xs text-[#666680]">
          {item.Type} {item.ProductionYear ? `· ${item.ProductionYear}` : ''}
        </p>
        {item.CommunityRating && (
          <div className="mt-1 flex items-center gap-1 text-xs">
            <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
            <span className="text-[#999]">{item.CommunityRating.toFixed(1)}</span>
          </div>
        )}
      </div>
    </div>
  );
}
