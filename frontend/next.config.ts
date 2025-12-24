import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  output: "standalone", // Критически важно для Docker
  basePath: "/ops",     // Чтобы приложение открывалось по адресу /ops
};

export default nextConfig;