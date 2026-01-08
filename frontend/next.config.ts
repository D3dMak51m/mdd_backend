import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  output: "standalone", // Обязательно для Docker-образа, который мы описали
  basePath: "/ops",     // Обязательно, так как Nginx проксирует запросы с /ops на этот контейнер
};

export default nextConfig;