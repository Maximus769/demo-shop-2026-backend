'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useCart } from '@/context/CartContext'
import { api } from '@/lib/api'

export default function CheckoutPage() {
  const router = useRouter()
  const { items, totalPrice, clearCart } = useCart()

  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (items.length === 0) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-24 text-center">
        <div className="text-5xl mb-4">🛒</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-3">Panier vide</h1>
        <Link href="/products" className="text-indigo-600 hover:underline">
          Voir les produits
        </Link>
      </div>
    )
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const origin = window.location.origin

      const session = await api.payments.createCheckoutSession({
        email,
        items: items.map((i) => ({
          productId: i.id,
          name: i.name,
          price: i.price,
          quantity: i.quantity,
          size: i.size ?? '',
          color: i.color ?? '',
        })),
        successUrl: `${origin}/success?ref={CHECKOUT_SESSION_ID}`,
        cancelUrl: `${origin}/checkout`,
      })

      sessionStorage.setItem(
        'lastOrder',
        JSON.stringify({ email, items, total: totalPrice })
      )
      clearCart()

      if (session.url) {
        window.location.href = session.url
      } else {
        router.push('/success')
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Une erreur est survenue. Veuillez réessayer.'
      )
      setLoading(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <Link href="/cart" className="text-sm text-indigo-600 hover:underline">
          ← Retour au panier
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mt-3">Paiement</h1>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Checkout form */}
        <div className="flex-1">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email */}
            <div className="bg-white rounded-2xl border border-gray-100 p-6">
              <h2 className="font-semibold text-gray-900 mb-4">Coordonnées</h2>
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1.5">
                  Email pour la confirmation de commande
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="vous@exemple.fr"
                  className="w-full rounded-xl border border-gray-200 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                />
              </div>
            </div>

            {/* Payment info */}
            <div className="bg-white rounded-2xl border border-gray-100 p-6">
              <h2 className="font-semibold text-gray-900 mb-2">Paiement sécurisé</h2>
              <p className="text-sm text-gray-500 mb-4">
                Vous serez redirigé vers Stripe pour compléter votre paiement en toute sécurité.
                Tous les moyens de paiement européens sont acceptés (Visa, Mastercard, CB).
              </p>
              <div className="flex items-center gap-3 text-xs text-gray-400">
                <span className="flex items-center gap-1">🔒 SSL chiffré</span>
                <span>·</span>
                <span>3D Secure inclus</span>
                <span>·</span>
                <span>PCI-DSS conforme</span>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-5 py-4">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 text-white font-bold py-4 rounded-2xl text-lg hover:bg-indigo-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                  Redirection vers Stripe…
                </>
              ) : (
                <>🔒 Payer {(totalPrice / 100).toFixed(2)} €</>
              )}
            </button>
          </form>
        </div>

        {/* Order summary */}
        <div className="lg:w-80 flex-shrink-0">
          <div className="bg-white rounded-2xl border border-gray-100 p-6">
            <h2 className="font-semibold text-gray-900 text-lg mb-5">
              Commande ({items.reduce((s, i) => s + i.quantity, 0)} articles)
            </h2>

            <div className="space-y-4 mb-5">
              {items.map((item) => (
                <div key={item.id} className="flex items-start gap-3">
                  <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center text-2xl flex-shrink-0">
                    👕
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 leading-tight truncate">
                      {item.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {[item.color, item.size].filter(Boolean).join(' · ')} · Qté {item.quantity}
                    </p>
                  </div>
                  <p className="text-sm font-medium text-gray-900 whitespace-nowrap">
                    {((item.price * item.quantity) / 100).toFixed(2)} €
                  </p>
                </div>
              ))}
            </div>

            <div className="border-t border-gray-100 pt-4 space-y-2">
              <div className="flex justify-between text-sm text-gray-600">
                <span>Sous-total</span>
                <span>{(totalPrice / 100).toFixed(2)} €</span>
              </div>
              <div className="flex justify-between text-sm text-gray-600">
                <span>Livraison</span>
                <span className="text-green-600 font-medium">Calculée par Stripe</span>
              </div>
              <div className="flex justify-between font-bold text-gray-900 text-base pt-2 border-t border-gray-100">
                <span>Total</span>
                <span>{(totalPrice / 100).toFixed(2)} €</span>
              </div>
            </div>

            <div className="mt-4 bg-indigo-50 rounded-xl p-3 text-xs text-indigo-700">
              📦 Livraison estimée en France : 1–3 jours ouvrés
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
