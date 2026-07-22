'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { CartItem } from '@/context/CartContext'

type LastOrder = {
  email: string
  items: CartItem[]
  total: number
}

export default function SuccessPage() {
  const searchParams = useSearchParams()
  const ref = searchParams.get('ref') ?? searchParams.get('session_id') ?? 'HV-XXXXX'

  const [order, setOrder] = useState<LastOrder | null>(null)

  useEffect(() => {
    try {
      const stored = sessionStorage.getItem('lastOrder')
      if (stored) {
        setOrder(JSON.parse(stored) as LastOrder)
        sessionStorage.removeItem('lastOrder')
      }
    } catch {
      // ignore
    }
  }, [])

  const deliveryDate = new Date()
  deliveryDate.setDate(deliveryDate.getDate() + 3)
  const formattedDate = deliveryDate.toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  })

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-16">
      <div className="w-full max-w-lg">
        {/* Success card */}
        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 text-center">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg
              className="w-10 h-10 text-green-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>

          <h1 className="text-2xl font-bold text-gray-900 mb-2">Commande confirmée !</h1>
          <p className="text-gray-500 mb-6">
            Merci pour votre commande. Un email de confirmation a été envoyé
            {order?.email ? ` à ${order.email}` : ''}.
          </p>

          {/* Order ref */}
          <div className="bg-gray-50 rounded-2xl p-4 mb-6">
            <p className="text-xs text-gray-400 mb-1">Référence de commande</p>
            <p className="font-mono font-bold text-gray-800 text-sm break-all">{ref}</p>
          </div>

          {/* Items ordered */}
          {order && order.items.length > 0 && (
            <div className="text-left mb-6">
              <p className="text-sm font-medium text-gray-700 mb-3">Articles commandés</p>
              <div className="space-y-2">
                {order.items.map((item) => (
                  <div key={item.id} className="flex justify-between items-center text-sm">
                    <div>
                      <span className="text-gray-800 font-medium">{item.name}</span>
                      {(item.size ?? item.color) && (
                        <span className="text-gray-400 text-xs ml-2">
                          {[item.color, item.size].filter(Boolean).join(' · ')}
                        </span>
                      )}
                      <span className="text-gray-400 text-xs ml-1">×{item.quantity}</span>
                    </div>
                    <span className="text-gray-700 font-medium whitespace-nowrap">
                      {((item.price * item.quantity) / 100).toFixed(2)} €
                    </span>
                  </div>
                ))}
              </div>
              <div className="border-t border-gray-100 mt-3 pt-3 flex justify-between font-semibold text-gray-900">
                <span>Total payé</span>
                <span>{(order.total / 100).toFixed(2)} €</span>
              </div>
            </div>
          )}

          {/* Delivery estimate */}
          <div className="bg-indigo-50 rounded-2xl p-4 mb-8 text-left">
            <div className="flex items-center gap-3">
              <span className="text-2xl">📦</span>
              <div>
                <p className="text-sm font-semibold text-indigo-900">Livraison estimée</p>
                <p className="text-sm text-indigo-700 capitalize">{formattedDate}</p>
                <p className="text-xs text-indigo-500 mt-0.5">Expédition depuis l'UE via Gelato</p>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <Link
              href="/products"
              className="flex-1 text-center bg-indigo-600 text-white font-semibold py-3 rounded-xl hover:bg-indigo-700 transition-colors"
            >
              Continuer mes achats
            </Link>
            <Link
              href="/"
              className="flex-1 text-center border border-gray-200 text-gray-700 font-medium py-3 rounded-xl hover:bg-gray-50 transition-colors"
            >
              Retour à l'accueil
            </Link>
          </div>
        </div>

        <p className="text-center text-xs text-gray-400 mt-6">
          Des questions ? Contactez-nous à{' '}
          <a href="mailto:contact@hvshirts.fr" className="text-indigo-500 hover:underline">
            contact@hvshirts.fr
          </a>
        </p>
      </div>
    </div>
  )
}
