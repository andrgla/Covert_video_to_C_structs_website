// frontend/tailwind.config.js

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        orbitron: ['Orbitron', 'sans-serif'],
      },
      colors: {
        // Your updated color palette
        'brand-background': '#242427',
        'brand-accent': '#395ce0',      
        'brand-header': '#7f95ef',     
        'brand-text': '#ffffff',        
        'brand-ui-bg': '#323237',       // New color for input fields/panels
        'brand-dark-light': '#4b5563', 
        'brand-dark': '#1f2937',       
      }
    },
  },
  plugins: [],
}