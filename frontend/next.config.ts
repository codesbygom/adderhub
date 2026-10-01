import type { NextConfig } from "next";

const backend = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  // DRF routes end in a slash; keep them so requests aren't redirected.
  trailingSlash: true,
  // The browser only talks to Next; API calls and uploaded images are proxied
  // to Django, so the backend needs no CORS setup.
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${backend}/api/:path*/` },
      { source: "/media/:path*", destination: `${backend}/media/:path*` },
    ];
  },
};

export default nextConfig;
