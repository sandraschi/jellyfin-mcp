import { OverviewSkeleton } from './overview-skeleton';

// Next.js App Router: this file automatically wraps page.tsx in a Suspense boundary
// at the framework level, which handles streaming SSR + hydration correctly.
export default function Loading() {
  return <OverviewSkeleton />;
}
