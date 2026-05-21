export function OverviewSkeleton() {
  return (
    <div className="animate-pulse space-y-8">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <div className="h-7 w-32 rounded-lg bg-jellyfin-surface-light" />
          <div className="h-4 w-48 rounded bg-jellyfin-surface-light" />
        </div>
        <div className="h-6 w-24 rounded-full bg-jellyfin-surface-light" />
      </div>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="card">
            <div className="flex items-center justify-between">
              <div className="h-3 w-16 rounded bg-jellyfin-surface-light" />
              <div className="h-8 w-8 rounded-lg bg-jellyfin-surface-light" />
            </div>
            <div className="mt-3 h-8 w-24 rounded bg-jellyfin-surface-light" />
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="card xl:col-span-2">
          <div className="mb-4 h-4 w-32 rounded bg-jellyfin-surface-light" />
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="rounded-lg bg-jellyfin-darker/50 p-4">
                <div className="mb-2 h-4 w-24 rounded bg-jellyfin-surface-light" />
                <div className="h-6 w-12 rounded bg-jellyfin-surface-light" />
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <div className="mb-4 h-4 w-28 rounded bg-jellyfin-surface-light" />
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex items-center gap-3 rounded-lg bg-jellyfin-darker/50 p-3">
                <div className="h-8 w-8 rounded-lg bg-jellyfin-surface-light" />
                <div className="flex-1 space-y-1">
                  <div className="h-3 w-32 rounded bg-jellyfin-surface-light" />
                  <div className="h-2 w-20 rounded bg-jellyfin-surface-light" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
