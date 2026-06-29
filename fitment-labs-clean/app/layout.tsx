import type { Metadata } from 'next'
import { Inter, Roboto } from 'next/font/google'
import './globals.css'
import { Header } from '@/components/Header'
import { Footer } from '@/components/Footer'
import { PromoBanner } from '@/components/PromoBanner'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })
const roboto = Roboto({ 
  weight: ['300', '400', '500', '700', '900'],
  subsets: ['latin'],
  variable: '--font-roboto'
})

export const metadata: Metadata = {
  title: 'Fitment Labs - Premium Wheels, Tires & Suspension',
  description: 'Discover high-performance wheels, tires, and suspension components for your vehicle. Bold, modern, performance-driven automotive parts.',
  keywords: 'wheels, tires, suspension, automotive, performance, KG1 Forged, JTX, American Force, Toyo, Nitto, Rough Country, BDS, McGaughys',
  openGraph: {
    title: 'Fitment Labs - Premium Wheels, Tires & Suspension',
    description: 'Discover high-performance wheels, tires, and suspension components for your vehicle.',
    type: 'website',
    url: process.env.NEXT_PUBLIC_SITE_URL,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${roboto.className} ${roboto.variable} bg-dark-bg text-dark-text`}>
        <div className="min-h-screen flex flex-col">
          <Header />
          <PromoBanner />
          <main className="flex-1">
            {children}
          </main>
          <Footer />
        </div>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#2A2A2A',
              color: '#E5E5E5',
              border: '1px solid #3A3A3A',
            },
            success: {
              style: {
                background: '#304529',
                color: '#E5E5E5',
              },
            },
            error: {
              style: {
                background: '#DC2626',
                color: '#E5E5E5',
              },
            },
          }}
        />
      </body>
    </html>
  )
}

