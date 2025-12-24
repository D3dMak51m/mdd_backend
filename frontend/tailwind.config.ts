import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}", // Мы создадим эту папку
  ],
  theme: {
    extend: {
      colors: {
        // Добавим семантические цвета для статусов
        ops: {
          bg: '#0f172a',      // Slate 900
          panel: '#1e293b',   // Slate 800
          border: '#334155',  // Slate 700
          alert: '#ef4444',   // Red 500
          warning: '#f59e0b', // Amber 500
          success: '#10b981', // Emerald 500
        }
      },
    },
  },
  plugins: [],
};
export default config;