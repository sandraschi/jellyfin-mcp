import { Suspense } from 'react';
import { LibraryList } from './library-list';
import { OverviewSkeleton } from '@/app/overview-skeleton';

export const dynamic = 'force-dynamic';

export default function LibrariesPage() {
  return (
    <Suspense fallback={<OverviewSkeleton />}>
      <LibraryList />
    </Suspense>
  );
}
