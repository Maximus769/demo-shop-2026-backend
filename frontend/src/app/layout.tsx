import type { Metadata } from 'next'
import { Geist } from 'next/font/google'
import './globals.css'
import { CartProvider } from '@/context/CartContext'
import Header from '@/components/Header'
import { Toaster } from 'react-hot-toast'

const geist = Geist({
  subsets: ['latin'],
  variable: '--font-geist',
})

export const metadata: Metadata = {
  title: 'H&V Shirts — T-shirts personnalisés livrés en France',
  description:
    'Créez vos t-shirts personnalisés avec impression de qualité. Livraison rapide en France en 1–3 jours. Prix à partir de 27€.',
  keywords: ['t-shirt personnalisé', 'impression t-shirt', 'France', 'custom t-shirt'],
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className={`${geist.variable} h-full`}>
      <body className="min-h-full flex flex-col bg-gray-50 font-sans antialiased">
        <CartProvider>
          <Header />
          <main className="flex-1">{children}</main>
          <Toaster
            position="bottom-right"
            toastOptions={{
              duration: 3000,
              style: { fontFamily: 'var(--font-geist, sans-serif)' },
            }}
          />
        </CartProvider>
      </body>
    </html>
  )
}
