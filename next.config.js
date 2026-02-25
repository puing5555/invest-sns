/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  basePath: '/invest-sns',
  images: {
    unoptimized: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;