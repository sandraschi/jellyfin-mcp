export function MediaSkeleton() {
  return (
    <div className="animate-pulse space-y-8">
      <div className="space-y-2">
        <div className="h-7 w-32 rounded-lg bg-jellyfin-surface-light" />
        <div className="h-4 w-24 rounded bg-jellyfin-surface-light" />
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
        {[...Array(12)].map((_, i) => (
          <div key={i} className="space-y-2">
            <div className="aspect-[2/3] rounded-xl bg-jellyfin-surface-light" />
            <div className="h-3 w-24 rounded bg-jellyfin-surface-light" />
            <div className="h-2 w-16 rounded bg-jellyfin-surface-light" />
          </div>
        ))}
      </div>
    </div>
  );
}
