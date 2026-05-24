# Strava Dashboard Frontend

Modern Next.js dashboard for visualizing Strava activities with dark theme.

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Chart library
- **Supabase** - Database client
- **Lucide React** - Icon library

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp ../.env.example .env.local
# Edit .env.local with your Supabase credentials
```

### Development

```bash
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

### Build

```bash
npm run build
npm start
```

## Features

- 🎨 Dark theme with modern design
- 📊 Activity statistics overview
- 🏃 Activity type breakdown
- 📈 Distance and time charts
- 📱 Responsive design
- ⚡ Fast performance with Next.js

## Environment Variables

```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_KEY=your_supabase_key
```

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Main dashboard page
│   └── globals.css         # Global styles
├── components/             # Reusable components
├── lib/
│   └── supabase.ts         # Supabase client
└── public/                 # Static assets
```