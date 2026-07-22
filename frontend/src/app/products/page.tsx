'use client'

import { useEffect, useState } from 'react'
import Image from 'next/image'
import toast from 'react-hot-toast'
import { api, Product } from '@/lib/api'
import { useCart } from '@/context/CartContext'

const SIZES = ['S', 'M', 'L', 'XL', 'XXL']

const PLACEHOLDER_PRODUCTS: Product[] = [
  {
    id: '1',
    name: 'T-Shirt Classique Blanc',
    description: 'T-shirt en coton bio 100% GOTS, coupe regular, impression DTG haute résolution.',
    price: 2700,
    images: [],
    colors: ['Blanc', 'Noir', 'Gris'],
    sizes: ['S', 'M', 'L', 'XL', 'XXL'],
    inStock: true,
  },
  {
    id: '2',
    name: 'T-Shirt Premium Noir',
    description: 'T-shirt premium en coton peigné, toucher doux, idéal pour l\'impression graphique.',
    price: 3200,
    images: [],
    colors: ['Noir', 'Marine', 'Bordeaux'],
    sizes: ['S', 'M', 'L', 'XL', 'XXL'],
    inStock: true,
  },
  {
    id: '3',
    name: 'T-Shirt Business Pack',
    description: 'Pack entreprise, tarif dégressif. Parfait pour uniformes et événements.',
    price: 1900,
    images: [],
    colors: ['Blanc', 'Noir', 'Bleu ciel', 'Gris'],
    sizes: ['S', 'M', 'L', 'XL', 'XXL'],
    inStock: true,
  },
  {
    id: '4',
    name: 'T-Shirt Oversize Vintage',
    description: 'Coupe oversize tendance, effet vintage délavé. Parfait pour streetwear.',
    price: 2950,
    images: [],
    colors: ['Beige', 'Lavande', 'Terracotta'],
    sizes: ['S', 'M', 'L', 'XL'],
    inStock: true,
  },
  {
    id: '5',
    name: 'T-Shirt Enfant',
    description: 'Doux et résistant, certifié Oeko-Tex. Impression lavable à 60°.',
    price: 1800,
    images: [],
    colors: ['Blanc', 'Rouge', 'Bleu', 'Jaune'],
    sizes: ['S', 'M', 'L'],
    inStock: true,
  },
  {
    id: '6',
    name: 'Polo Personnalisé',
    description: 'Polo piqué qualité professionnelle, col côtelé, impression broderie ou DTG.',
    price: 3500,
    images: [],
    colors: ['Blanc', 'Noir', 'Marine', 'Rouge'],
    sizes: ['S', 'M', 'L', 'XL', 'XXL'],
    inStock: true,
  },
]

const COLOR_SWATCHES: Record<string, string> = {
  Blanc: '#FFFFFF',
  Noir: '#111827',
  Gris: '#9CA3AF',
  Marine: '#1E3A5F',
  Bordeaux: '#7F1D1D',
  'Bleu ciel': '#93C5FD',
  Beige: '#D9C5A0',
  Lavande: '#C4B5FD',
  Terracotta: '#C2714F',
  Rouge: '#DC2626',
  Bleu: '#2563EB',
  Jaune: '#FBBF24',
}

export default function ProductsPage() {
  const { addItem } = useCart()
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedSizes, setSelectedSizes] = useState<Record<string, string>>({})
  const [selectedColors, setSelectedColors] = useState<Record<string, string>>({})
  const [filterSize, setFilterSize] = useState<string>('')

  useEffect(() => {
    api.products
      .list()
      .then(setProducts)
      .catch(() => setProducts(PLACEHOLDER_PRODUCTS))
      .finally(() => setLoading(false))
  }, [])

  function handleAddToCart(product: Product) {
    const size = selectedSizes[product.id]
    const color = selectedColors[product.id]

    if (!size) {
      toast.error('Veuillez choisir une taille.')
      return
    }
    if (!color) {
      toast.error('Veuillez choisir une couleur.')
      return
    }

    addItem({
      id: `${product.id}-${size}-${color}`,
      name: product.name,
      price: product.price,
      quantity: 1,
      size,
      color,
      image: product.images[0],
    })
    toast.success(`${product.name} ajouté au panier !`)
  }

  const displayed = filterSize
    ? products.filter((p) => p.sizes.includes(filterSize))
    : products

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Nos t-shirts</h1>
        <p className="text-gray-500">Personnalisez et commandez en quelques clics.</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2 mb-8">
        <span className="text-sm font-medium text-gray-600 self-center mr-2">Taille :</span>
        <button
          onClick={() => setFilterSize('')}
          className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-colors ${
            filterSize === ''
              ? 'bg-indigo-600 text-white border-indigo-600'
              : 'bg-white text-gray-700 border-gray-200 hover:border-indigo-300'
          }`}
        >
          Toutes
        </button>
        {SIZES.map((s) => (
          <button
            key={s}
            onClick={() => setFilterSize(s)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-colors ${
              filterSize === s
                ? 'bg-indigo-600 text-white border-indigo-600'
                : 'bg-white text-gray-700 border-gray-200 hover:border-indigo-300'
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white rounded-2xl border border-gray-100 p-4 animate-pulse">
              <div className="bg-gray-200 rounded-xl h-56 mb-4" />
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
              <div className="h-3 bg-gray-200 rounded w-1/2 mb-4" />
              <div className="h-10 bg-gray-200 rounded-xl" />
            </div>
          ))}
        </div>
      ) : displayed.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <p className="text-xl">Aucun produit disponible dans cette taille.</p>
          <button
            onClick={() => setFilterSize('')}
            className="mt-4 text-indigo-600 font-medium hover:underline"
          >
            Voir tous les produits
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {displayed.map((product) => (
            <div
              key={product.id}
              className="bg-white rounded-2xl border border-gray-100 overflow-hidden hover:shadow-md transition-shadow flex flex-col"
            >
              {/* Product image */}
              <div className="relative bg-gray-100 h-56 flex items-center justify-center text-6xl">
                {product.images[0] ? (
                  <Image
                    src={product.images[0]}
                    alt={product.name}
                    fill
                    className="object-cover"
                  />
                ) : (
                  <span>👕</span>
                )}
              </div>

              <div className="p-5 flex flex-col flex-1">
                <div className="flex items-start justify-between mb-2">
                  <h2 className="font-semibold text-gray-900 leading-tight">{product.name}</h2>
                  <span className="font-bold text-indigo-600 whitespace-nowrap ml-2">
                    {(product.price / 100).toFixed(2)} €
                  </span>
                </div>
                <p className="text-xs text-gray-500 leading-relaxed mb-4 flex-1">
                  {product.description}
                </p>

                {/* Color selector */}
                <div className="mb-3">
                  <p className="text-xs font-medium text-gray-600 mb-1.5">
                    Couleur{selectedColors[product.id] ? ` : ${selectedColors[product.id]}` : ''}
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {product.colors.map((color) => (
                      <button
                        key={color}
                        title={color}
                        onClick={() => setSelectedColors((prev) => ({ ...prev, [product.id]: color }))}
                        className={`w-7 h-7 rounded-full border-2 transition-transform hover:scale-110 ${
                          selectedColors[product.id] === color
                            ? 'border-indigo-600 scale-110'
                            : 'border-transparent'
                        }`}
                        style={{
                          backgroundColor: COLOR_SWATCHES[color] ?? '#E5E7EB',
                          boxShadow: color === 'Blanc' ? 'inset 0 0 0 1px #D1D5DB' : undefined,
                        }}
                      />
                    ))}
                  </div>
                </div>

                {/* Size selector */}
                <div className="mb-4">
                  <p className="text-xs font-medium text-gray-600 mb-1.5">Taille</p>
                  <div className="flex flex-wrap gap-1.5">
                    {product.sizes.map((size) => (
                      <button
                        key={size}
                        onClick={() => setSelectedSizes((prev) => ({ ...prev, [product.id]: size }))}
                        className={`px-3 py-1 text-xs font-medium rounded-lg border transition-colors ${
                          selectedSizes[product.id] === size
                            ? 'bg-indigo-600 text-white border-indigo-600'
                            : 'bg-white text-gray-700 border-gray-200 hover:border-indigo-300'
                        }`}
                      >
                        {size}
                      </button>
                    ))}
                  </div>
                </div>

                <button
                  onClick={() => handleAddToCart(product)}
                  disabled={!product.inStock}
                  className="w-full bg-indigo-600 text-white font-semibold py-2.5 rounded-xl hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-sm"
                >
                  {product.inStock ? 'Ajouter au panier' : 'Rupture de stock'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
