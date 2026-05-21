import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        jellyfin: {
          purple: "#AA5CC3",
          "purple-dark": "#8B3FAF",
          "purple-light": "#C48FD8",
          blue: "#00A4DC",
          "blue-dark": "#0089B8",
          "blue-light": "#33C0E8",
          dark: "#101020",
          darker: "#0A0A14",
          surface: "#1A1A2E",
          "surface-light": "#252540",
          "surface-lighter": "#303050",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.4s ease-out",
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "glow": "glow 2s ease-in-out infinite alternate",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        glow: {
          "0%": { boxShadow: "0 0 5px rgba(170, 92, 195, 0.4)" },
          "100%": { boxShadow: "0 0 20px rgba(170, 92, 195, 0.7)" },
        },
      },
    },
  },
  plugins: [],
};
export default config;
