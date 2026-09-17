import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: { ink: "#081114", cyan: "#7ce8f2", coral: "#ff8b78" },
    },
  },
  plugins: [],
};

export default config;