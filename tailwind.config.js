/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Plus Jakarta Sans", "Segoe UI", "sans-serif"],
      },
      colors: {
        ink: "#172033",
        ocean: "#115e8c",
        mint: "#0f9f7a",
        signal: "#f59e0b",
        danger: "#dc2626",
      },
      boxShadow: {
        soft: "0 18px 45px rgba(23, 32, 51, 0.08)",
      },
    },
  },
  plugins: [],
};
