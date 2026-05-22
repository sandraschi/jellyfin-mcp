'use client';

import { useEffect, useState } from 'react';
import { fetchLibraries } from '@/utils/api';
import { libraryTypeColor } from '@/utils/jellyfin-media';
import {
  Film,
  Tv,
  Music,
  Image,
  BookOpen,
  Video,
  FolderOpen,
  CheckCircle,
  Clock,
} from 'lucide-react';

export function LibraryList() {
  const [libraries, setLibraries] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchLibraries()
      .then(setLibraries)
      .catch(() => setError('Failed to load libraries'));
  }, []);

  const typeIcons: Record<string, React.ComponentType<{ className?: string }>> = {
    Movies: Film,
    Series: Tv,
    Music,
    Photos: Image,
    Books: BookOpen,
    HomeVideos: Video,
    Mixed: FolderOpen,
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Media Libraries</h2>
          <p className="mt-1 text-sm text-[#777790]">{libraries.length} libraries configured</p>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {libraries.map((lib: any) => {
          const Icon = typeIcons[lib.type] || FolderOpen;
          return (
            <div
              key={lib.id || lib.name}
              className="card group flex flex-col gap-4"
            >
              <div className="flex items-start justify-between">
                <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${libraryTypeColor(lib.type)}`}>
                  <Icon className="h-6 w-6" />
                </div>
                <span className={`badge ${libraryTypeColor(lib.type).split(' ')[0]} ${libraryTypeColor(lib.type).split(' ')[1]}`}>
                  {lib.type}
                </span>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">{lib.name}</h3>
                <p className="mt-1 text-3xl font-bold text-white">{lib.itemCount ?? '—'}</p>
                <p className="text-xs text-[#666680]">items in library</p>
              </div>
              <div className="flex items-center gap-2 border-t border-[#ffffff08] pt-3">
                {lib.lastScanStatus === 'completed' ? (
                  <CheckCircle className="h-3.5 w-3.5 text-green-400" />
                ) : (
                  <Clock className="h-3.5 w-3.5 text-amber-400" />
                )}
                <span className="text-[11px] text-[#666680]">
                  {lib.lastScanStatus === 'completed' ? 'Last scan complete' : lib.lastScanStatus || 'Not scanned'}
                </span>
              </div>
            </div>
          );
        })}
        {libraries.length === 0 && (
          <div className="card col-span-full flex flex-col items-center py-16">
            <FolderOpen className="mb-3 h-10 w-10 text-[#444460]" />
            <p className="text-sm text-[#666680]">No media libraries found</p>
            <p className="mt-1 text-xs text-[#555570]">Add libraries through the Jellyfin dashboard</p>
          </div>
        )}
      </div>
    </div>
  );
}
