/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    appDir: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001',
    NEXT_PUBLIC_FGP_CORE_URL: process.env.NEXT_PUBLIC_FGP_CORE_URL || 'http://localhost:8000',
    NEXT_PUBLIC_EXTENSIONS_URL: process.env.NEXT_PUBLIC_EXTENSIONS_URL || 'http://localhost:8002',
    NEXT_PUBLIC_ABIS_URL: process.env.NEXT_PUBLIC_ABIS_URL || 'http://localhost:8003',
  },
  images: {
    domains: ['localhost', '127.0.0.1'],
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
      },
    ];
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }
    return config;
  },
};

module.exports = nextConfig;
