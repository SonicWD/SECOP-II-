import type { NextConfig } from "next";

const api = process.env.API_URL || "http://127.0.0.1:8000";
const staticExport = process.env.STATIC_EXPORT === "1";

const nextConfig: NextConfig = {
  ...(staticExport ? { output: "export" as const } : {}),
  async rewrites() {
    if (staticExport) return [];
    return [
      { source: "/api/:path*", destination: `${api}/api/:path*` },
      { source: "/docs", destination: `${api}/docs` },
      { source: "/docs/:path*", destination: `${api}/docs/:path*` },
      { source: "/openapi.json", destination: `${api}/openapi.json` },
    ];
  },
};

export default nextConfig;
