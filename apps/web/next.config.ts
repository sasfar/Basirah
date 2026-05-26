import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  // API requests are handled by nginx reverse proxy
  // Client-side: browser → nginx → basirah-api
  // Server-side: Next.js → basirah-api (Docker network)
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://basirah-api:8080/api/:path*',
      },
    ];
  },
};

export default nextConfig;
