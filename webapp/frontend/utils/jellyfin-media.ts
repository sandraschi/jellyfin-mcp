import { API_BASE } from './api';

export function jellyfinImageUrl(
  itemId: string,
  imageType = 'Primary',
  imageIndex = 0,
  options?: { width?: number; height?: number; quality?: number },
): string {
  const base = `${API_BASE}/image/Items/${encodeURIComponent(itemId)}/Images/${imageType}/${imageIndex}`;
  if (!options) return base;
  const params = new URLSearchParams();
  if (options.width) params.set('width', String(options.width));
  if (options.height) params.set('height', String(options.height));
  if (options.quality) params.set('quality', String(options.quality));
  const qs = params.toString();
  return qs ? `${base}?${qs}` : base;
}

export function formatRuntime(ticks: number): string {
  const totalMinutes = Math.floor(ticks / 600000000);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`;
}

export function formatTicks(ticks: number): string {
  const totalSeconds = Math.floor(ticks / 10000000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

export function libraryTypeIcon(type: string): string {
  const map: Record<string, string> = {
    Movies: 'Film',
    Series: 'Tv',
    Music: 'Music',
    Photos: 'Image',
    Books: 'BookOpen',
    HomeVideos: 'Video',
    Mixed: 'FolderOpen',
  };
  return map[type] || 'Folder';
}

export function libraryTypeColor(type: string): string {
  const map: Record<string, string> = {
    Movies: 'bg-purple-500/20 text-purple-300',
    Series: 'bg-blue-500/20 text-blue-300',
    Music: 'bg-green-500/20 text-green-300',
    Photos: 'bg-yellow-500/20 text-yellow-300',
    Books: 'bg-orange-500/20 text-orange-300',
    HomeVideos: 'bg-pink-500/20 text-pink-300',
    Mixed: 'bg-gray-500/20 text-gray-300',
  };
  return map[type] || 'bg-gray-500/20 text-gray-300';
}
