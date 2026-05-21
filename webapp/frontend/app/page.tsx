import { Suspense } from 'react';
import { OverviewDashboard } from './overview-dashboard';
import { OverviewSkeleton } from './overview-skeleton';

export const dynamic = 'force-dynamic';

export default function HomePage() {
  return (
    <Suspense fallback={<OverviewSkeleton />}>
      <OverviewDashboard />
    </Suspense>
  );
}
