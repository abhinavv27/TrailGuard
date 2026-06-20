import type { Config } from "tailwindcss"

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: { 900: "#0a0e1a", 800: "#0f1422", 700: "#151b2e", 600: "#1c2440" },
        cyan: { 400: "#22d3ee", 500: "#06b6d4", 600: "#0891b2" },
        amber: { 400: "#fbbf24", 500: "#f59e0b" },
        red: { 400: "#f87171", 500: "#ef4444" },
      },
    },
  },
  plugins: [],
}
export default config
