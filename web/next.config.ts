import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { hostname: "i.redd.it" },
      { hostname: "i.imgur.com" },
      { hostname: "preview.redd.it" },
      { hostname: "external-preview.redd.it" },
      { hostname: "b.thumbs.redditmedia.com" },
    ],
  },
};

export default nextConfig;
