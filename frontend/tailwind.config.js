/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: "#0F0F12",
        cardBg: "#18181F",
        borderDark: "#26262F",
        accentBlue: "#0071E3",
        textWhite: "#F5F5F7",
        textGray: "#86868B"
      }
    },
  },
  plugins: [],
}
