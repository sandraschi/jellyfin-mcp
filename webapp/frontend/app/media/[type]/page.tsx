import { MediaGrid } from './media-grid';

const MEDIA_TYPES = ['Movies', 'Series', 'Music', 'Photos', 'Books'];

export function generateStaticParams() {
  return MEDIA_TYPES.map((type) => ({ type }));
}

export default async function MediaPage({
  params,
}: {
  params: Promise<{ type: string }>;
}) {
  const { type } = await params;
  return <MediaGrid mediaType={type} />;
}
