const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    appDir: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001',
    NEXT_PUBLIC_DEVICE_BRIDGE_URL:
      process.env.NEXT_PUBLIC_DEVICE_BRIDGE_URL || 'http://127.0.0.1:8765',
    NEXT_PUBLIC_FGP_CORE_URL: process.env.NEXT_PUBLIC_FGP_CORE_URL || 'http://localhost:8000',
    NEXT_PUBLIC_EXTENSIONS_URL: process.env.NEXT_PUBLIC_EXTENSIONS_URL || 'http://localhost:8002',
    NEXT_PUBLIC_ABIS_URL: process.env.NEXT_PUBLIC_ABIS_URL || 'http://localhost:8003',
    NEXT_PUBLIC_FINGERPRINT_URL: process.env.NEXT_PUBLIC_FINGERPRINT_URL || 'http://localhost:8010',
    NEXT_PUBLIC_ICAO_FACE_SERVICE_URL:
      process.env.NEXT_PUBLIC_ICAO_FACE_SERVICE_URL || 'http://127.0.0.1:50270',
    NEXT_PUBLIC_RH_API_URL: process.env.NEXT_PUBLIC_RH_API_URL || 'http://localhost:8100',
    NEXT_PUBLIC_GUICHET_INTERNAL_API_KEY:
      process.env.NEXT_PUBLIC_GUICHET_INTERNAL_API_KEY || 'fgp_guichet_internal_dev',
  },
  images: {
    domains: ['localhost', '127.0.0.1'],
    unoptimized: true,
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [{ key: 'Permissions-Policy', value: 'camera=(self), microphone=()' }],
      },
    ];
  },
  async rewrites() {
    const bridge =
      process.env.DEVICE_BRIDGE_INTERNAL_URL ||
      process.env.NEXT_PUBLIC_DEVICE_BRIDGE_URL ||
      'http://127.0.0.1:8765';
    const api =
      process.env.ENROLLMENT_GATEWAY_INTERNAL_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      'http://localhost:8001';
    const icao =
      process.env.NEXT_PUBLIC_ICAO_FACE_SERVICE_URL || 'http://127.0.0.1:50270';
    const icaoLocal =
      icao.includes('127.0.0.1') ? icao.replace('127.0.0.1', 'localhost') : icao;
    return {
      beforeFiles: [
        {
          source: '/bridge-proxy/:path*',
          destination: `${bridge}/:path*`,
        },
        {
          source: '/icao-proxy/:path*',
          destination: `${icaoLocal}/:path*`,
        },
      ],
      afterFiles: [
        {
          // Ne pas intercepter la route Next pages/api/icao-health.ts
          source: '/api/:path((?!icao-health|rh).*)',
          destination: `${api}/api/:path*`,
        },
      ],
    };
  },
  webpack: (config, { isServer }) => {
    config.resolve.alias['@'] = path.resolve(__dirname, 'src');
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
