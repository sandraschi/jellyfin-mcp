import Link from 'next/link';
import { fetchMedia } from '@/utils/api';
import { jellyfinImageUrl, formatRuntime } from '@/utils/jellyfin-media';
import { Star } from 'lucide-react';

const mediaTypes = ['Movies', 'Series', 'Music', 'Photos', 'Books'];

interface Props {
  mediaType: string;
  searchParams?: { sort?: string; library?: string };
}

export async function MediaGrid({ mediaType }: Props) {
  let data: { Items: any[]; TotalRecordCount: number } = { Items: [], TotalRecordCount: 0 };
  let error: string | null = null;

  try {
    data = await fetchMedia(mediaType);
  } catch {
    error = `Failed to load ${mediaType}`;
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">{mediaType}</h2>
          <p className="mt-1 text-sm text-[#777790]">{data.TotalRecordCount} items</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex rounded-lg border border-[#ffffff10] bg-jellyfin-surface p-0.5">
            {mediaTypes.map((t) => (
              <Link
                key={t}
                href={`/media/${t}`}
                className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                  t === mediaType
                    ? 'bg-jellyfin-purple/20 text-jellyfin-purple-light'
                    : 'text-[#777790] hover:text-white'
                }`}
              >
                {t}
              </Link>
            ))}
          </div>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
        {data.Items.map((item: any) => (
          <MediaCard key={item.Id} item={item} />
        ))}
        {data.Items.length === 0 && (
          <div className="card col-span-full flex flex-col items-center py-16">
            <p className="text-sm text-[#666680]">No {mediaType.toLowerCase()} found</p>
          </div>
        )}
      </div>
    </div>
  );
}

function MediaCard({ item }: { item: any }) {
  const imageUrl = item.Id ? jellyfinImageUrl(item.Id, 'Primary', 0, { width: 400, quality: 80 }) : null;
  const fallbackGradient = 'from-jellyfin-purple/30 to-jellyfin-blue/20';

  return (
    <div className="group cursor-pointer rounded-xl transition-all duration-300 hover:scale-[1.03] hover:shadow-xl hover:shadow-jellyfin-purple/10">
      <div className="relative aspect-[2/3] overflow-hidden rounded-xl border border-[#ffffff08] bg-jellyfin-surface">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={item.Name}
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
            loading="lazy"
          />
        ) : (
          <div className={`flex h-full w-full items-center justify-center bg-gradient-to-br ${fallbackGradient}`}>
            <span className="text-4xl font-bold text-white/20">
              {item.Name?.charAt(0)?.toUpperCase() || '?'}
            </span>
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
        <div className="absolute bottom-0 left-0 right-0 translate-y-full p-4 transition-transform duration-300 group-hover:translate-y-0">
          <p className="text-sm font-medium text-white line-clamp-2">{item.Name}</p>
          <div className="mt-1 flex items-center gap-2 text-[11px] text-[#aaa]">
            {item.ProductionYear && <span>{item.ProductionYear}</span>}
            {item.CommunityRating && (
              <span className="flex items-center gap-0.5">
                <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
                {item.CommunityRating.toFixed(1)}
              </span>
            )}
          </div>
        </div>
      </div>
      <p className="mt-2 truncate text-sm font-medium text-white">{item.Name}</p>
      <p className="text-xs text-[#666680]">
        {item.ProductionYear || ''}
        {item.RunTimeTicks ? ` • ${formatRuntime(item.RunTimeTicks)}` : ''}
      </p>
    </div>
  );
}
