/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: { unoptimized: true },
};

if (process.env.NODE_ENV === 'development') {
  nextConfig.rewrites = async () => [
    { source: '/api/:path*', destination: 'http://127.0.0.1:10934/api/:path*' },
    { source: '/image/:path*', destination: 'http://127.0.0.1:10934/image/:path*' },
    { source: '/ws', destination: 'http://127.0.0.1:10934/ws' },
    { source: '/health', destination: 'http://127.0.0.1:10934/health' },
  ];
}

module.exports = nextConfig;
