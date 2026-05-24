import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0f172a',
        foreground: '#f8fafc',
        card: '#1e293b',
        'card-hover': '#334155',
        border: '#334155',
        primary: '#3b82f6',
        'primary-hover': '#2563eb',
      },
    },
  },
  plugins: [],
}
export default config