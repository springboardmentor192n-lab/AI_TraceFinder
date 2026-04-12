/** @type {import('next').NextConfig} */
module.exports = {
  reactStrictMode: true,
  trailingSlash: true,
  async rewrites() {
    return [
      { source: '/api/:path*/', destination: 'http://localhost:8000/api/:path*/' },
      { source: '/api/:path*',  destination: 'http://localhost:8000/api/:path*/' },
    ]
  },
}
