import type { Config } from "tailwindcss"

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Rethemed to the landing aesthetic: "navy" is now the black/ink scale
        // and "cyan" is now the bold sky-blue accent, so the whole app inherits
        // the landing look without touching every file.
        navy: { 900: "#05060a", 800: "#0b0e14", 700: "#11151d", 600: "#1b212c" },
        cyan: { 300: "#7cc7ff", 400: "#2ba8ff", 500: "#1f97f0", 600: "#0e8fe6" },
        amber: { 400: "#fbbf24", 500: "#f59e0b" },
        red: { 400: "#f87171", 500: "#ef4444" },
        // Landing/auth design system: black base + sky-blue accent
        ink: { DEFAULT: "#000000", 950: "#05060a", 900: "#080a0f", 850: "#0b0e14", 800: "#0f131b", 700: "#161b24" },
        // Bolder, more electric sky-blue accent
        sky: { 300: "#7cc7ff", 400: "#2ba8ff", 500: "#0e8fe6", 600: "#0a72bd" },
      },
      fontFamily: {
        display: ["var(--font-display)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      keyframes: {
        "reveal-up": { "0%": { opacity: "0", transform: "translateY(28px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        "marquee": { "0%": { transform: "translateX(0)" }, "100%": { transform: "translateX(-50%)" } },
        "ticker": { "0%": { transform: "translateY(0)" }, "100%": { transform: "translateY(-50%)" } },
        "pulse-glow": { "0%,100%": { opacity: "0.4" }, "50%": { opacity: "1" } },
        "float-slow": { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-10px)" } },
      },
      animation: {
        "marquee": "marquee 38s linear infinite",
        "ticker": "ticker 32s linear infinite",
        "pulse-glow": "pulse-glow 3.5s ease-in-out infinite",
        "float-slow": "float-slow 7s ease-in-out infinite",
      },
    },
  },
  plugins: [],
}
export default config
