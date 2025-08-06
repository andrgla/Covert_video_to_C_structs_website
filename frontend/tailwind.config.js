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
        mono: ['Space Mono', 'monospace'], // Add this line
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
        'brand-input': '#525863',       // Much brighter for input fields
        'brand-button': '#5170ff',
        'brand-success': '#91d16c',     // Matcha green for active states #91d16c
        'brand-success-hover': '#76a859', // Darker matcha green for hover
        // Custom gradient colors
        'gradient-purple': '#8c52ff',
        'gradient-orange': '#ff914d',       
      },
      backgroundImage: {
        'gradient-button': '#5170ff',
      }
    },
  },
  plugins: [],
}