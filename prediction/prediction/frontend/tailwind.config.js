/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Poppins', 'sans-serif'],
      },
      colors: {
        'brand': '#2563eb',
        'brand-dark': '#1d4ed8',
        'brand-light': '#dbeafe',
        'surface': '#ffffff',
        'surface-alt': '#f9fafb',
        'surface-hover': '#f3f4f6',
        'border-subtle': '#e5e7eb',
        'border-muted': '#f3f4f6',
        'text-primary': '#111827',
        'text-secondary': '#6b7280',
        'text-muted': '#9ca3af',
        'health-success': '#22c55e',
        'health-warning': '#f59e0b',
        'health-danger': '#ef4444',
      },
      animation: {
        'fade-in': 'fadeIn 0.6s ease-out forwards',
        'slide-up': 'slideUp 0.6s ease-out forwards',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        }
      },
      boxShadow: {
        'card': '0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03)',
        'card-hover': '0 4px 16px rgba(0,0,0,0.06), 0 12px 40px rgba(0,0,0,0.04)',
        'nav': '0 1px 2px rgba(0,0,0,0.04)',
        'btn': '0 1px 2px rgba(37,99,235,0.1), 0 4px 12px rgba(37,99,235,0.15)',
        'btn-hover': '0 4px 16px rgba(37,99,235,0.2), 0 8px 24px rgba(37,99,235,0.15)',
      }
    },
  },
  plugins: [],
}
