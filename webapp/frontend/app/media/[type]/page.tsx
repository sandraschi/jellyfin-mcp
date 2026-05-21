import { Suspense } from 'react';
import { MediaGrid } from './media-grid';
import { MediaSkeleton } from './media-skeleton';

export const dynamic = 'force-dynamic';

export default async function MediaPage({ params }: { params: Promise<{ type: string }> }) {
  const { type } = await params;
  return (
    <Suspense fallback={<MediaSkeleton />}>
      <MediaGrid mediaType={type} />
    </Suspense>
  );
}
