/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Dark theme color palette
        'dark-bg': '#0A0A0A',
        'dark-surface': '#1A1A1A',
        'dark-card': '#2A2A2A',
        'dark-border': '#3A3A3A',
        'dark-text': '#E5E5E5',
        'dark-text-secondary': '#B0B0B0',
        
        // Brand colors - Updated to Chili Red
        'forest-green': '#CD1C18',
        'forest-green-light': '#E53E3A',
        'forest-green-dark': '#A01612',
        'chili-red': '#CD1C18',
        'chili-red-light': '#E53E3A',
        'chili-red-dark': '#A01612',
        
        // Accent colors for dark theme
        'accent-gold': '#D4AF37',
        'accent-silver': '#C0C0C0',
        'accent-orange': '#FF6B35',
        'accent-red': '#DC2626',
        
        // Legacy colors for compatibility
        'charcoal': '#2D2D2D',
        'dark-gray': '#1A1A1A',
        'light-gray': '#F5F5F5',
        'steel-blue': '#4A5568',
        'off-white': '#FAFAFA',
        'sand': '#C2B280',
        'black': '#000000',
      },
      fontFamily: {
        sans: ['var(--font-roboto)', 'Roboto', 'system-ui', 'sans-serif'],
        roboto: ['var(--font-roboto)', 'Roboto', 'sans-serif'],
        display: ['var(--font-roboto)', 'Roboto', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'hero': ['4rem', { lineHeight: '1.1', fontWeight: '800' }],
        'display': ['3rem', { lineHeight: '1.2', fontWeight: '700' }],
      },
      backgroundImage: {
        'gradient-dark': 'linear-gradient(135deg, #0A0A0A 0%, #1A1A1A 100%)',
        'gradient-forest': 'linear-gradient(135deg, #304529 0%, #1F2E1A 100%)',
        'gradient-overlay': 'linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9))',
        'gradient-card': 'linear-gradient(135deg, #2A2A2A 0%, #1A1A1A 100%)',
      },
      boxShadow: {
        'dramatic': '0 25px 50px -12px rgba(0, 0, 0, 0.8)',
        'card-hover': '0 20px 40px -12px rgba(0, 0, 0, 0.6)',
        'glow': '0 0 20px rgba(48, 69, 41, 0.5)',
        'glow-gold': '0 0 20px rgba(212, 175, 55, 0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.6s ease-out',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite alternate',
        'marquee': 'marquee 20s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        glowPulse: {
          '0%': { boxShadow: '0 0 20px rgba(48, 69, 41, 0.5)' },
          '100%': { boxShadow: '0 0 30px rgba(48, 69, 41, 0.8)' },
        },
        marquee: {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(-100%)' },
        },
      },
    },
  },
  plugins: [],
}

