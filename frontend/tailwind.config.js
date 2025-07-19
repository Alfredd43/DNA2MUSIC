/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: '#101014',
          900: '#09090d',
          800: '#18181c',
        },
        primary: {
          50: '#e0f2ff',
          500: '#2563eb', // toned-down blue
          600: '#1d4ed8',
          700: '#1e40af',
        },
        dna: {
          50: '#e0ffe6',
          500: '#06b6d4', // toned-down cyan
          600: '#0891b2',
          700: '#0e7490',
        },
        accent: {
          500: '#4ade80', // soft green
          600: '#22c55e',
        },
        card: '#18181c',
        border: '#23232a',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
      }
    },
  },
  plugins: [],
} 