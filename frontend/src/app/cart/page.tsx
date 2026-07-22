'use client'

import Link from 'next/link'
import Image from 'next/image'
import { useCart } from '@/context/CartContext'

export default function CartPage() {
  const { items, totalPrice, updateQty, removeItem } = useCart()

  if (items.length === 0) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-24 text-center">
        <div className="text-6xl mb-6">🛒</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-3">Votre panier est vide</h1>
        <p className="text-gray-500 mb-8">Découvrez nos t-shirts personnalisés et ajoutez-les à votre panier.</p>
        <Link
          href="/products"
          className="inline-flex items-center justify-center bg-indigo-600 text-white font-semibold px-8 py-3 rounded-xl hover:bg-indigo-700 transition-colors"
        >
          Voir les produits
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Mon panier</h1>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Items list */}
        <div className="flex-1 space-y-4">
          {items.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-2xl border border-gray-100 p-5 flex gap-4"
            >
              {/* Image */}
              <div className="w-20 h-20 rounded-xl bg-gray-100 flex-shrink-0 flex items-center justify-center text-3xl overflow-hidden relative">
                {item.image ? (
                  <Image src={item.image} alt={item.name} fill className="object-cover" />
                ) : (
                  '👕'
                )}
              </div>

              {/* Details */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="font-semibold text-gray-900 leading-tight">{item.name}</p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {[item.color, item.size].filter(Boolean).join(' · ')}
                    </p>
                  </div>
                  <p className="font-bold text-gray-900 whitespace-nowrap">
                    {((item.price * item.quantity) / 100).toFixed(2)} €
                  </p>
                </div>

                <div className="flex items-center justify-between mt-3">
                  {/* Qty controls */}
                  <div className="flex items-center border border-gray-200 rounded-xl overflow-hidden">
                    <button
                      onClick={() => updateQty(item.id, item.quantity - 1)}
                      className="w-9 h-9 flex items-center justify-center text-gray-600 hover:bg-gray-50 transition-colors font-medium"
                      aria-label="Diminuer"
                    >
                      −
                    </button>
                    <span className="w-9 h-9 flex items-center justify-center text-sm font-medium text-gray-900">
                      {item.quantity}
                    </span>
                    <button
                      onClick={() => updateQty(item.id, item.quantity + 1)}
                      className="w-9 h-9 flex items-center justify-center text-gray-600 hover:bg-gray-50 transition-colors font-medium"
                      aria-label="Augmenter"
                    >
                      +
                    </button>
                  </div>

                  <button
                    onClick={() => removeItem(item.id)}
                    className="text-xs text-red-500 hover:text-red-700 transition-colors font-medium"
                  >
                    Supprimer
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Order summary */}
        <div className="lg:w-80 flex-shrink-0">
          <div className="bg-white rounded-2xl border border-gray-100 p-6 sticky top-24">
            <h2 className="font-semibold text-gray-900 text-lg mb-5">Récapitulatif</h2>

            <div className="space-y-3 mb-5">
              {items.map((item) => (
                <div key={item.id} className="flex justify-between text-sm">
                  <span className="text-gray-600 truncate mr-2">
                    {item.name}{item.size ? ` (${item.size})` : ''} ×{item.quantity}
                  </span>
                  <span className="text-gray-900 font-medium whitespace-nowrap">
                    {((item.price * item.quantity) / 100).toFixed(2)} €
                  </span>
                </div>
              ))}
            </div>

            <div className="border-t border-gray-100 pt-4 mb-6">
              <div className="flex justify-between font-semibold text-gray-900">
                <span>Sous-total</span>
                <span>{(totalPrice / 100).toFixed(2)} €</span>
              </div>
              <p className="text-xs text-gray-400 mt-1">
                Livraison calculée à l'étape suivante
              </p>
            </div>

            <Link
              href="/checkout"
              className="block w-full text-center bg-indigo-600 text-white font-semibold py-3 rounded-xl hover:bg-indigo-700 transition-colors"
            >
              Passer la commande →
            </Link>
            <Link
              href="/products"
              className="block w-full text-center text-gray-500 text-sm mt-3 hover:text-gray-700 transition-colors"
            >
              Continuer les achats
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
