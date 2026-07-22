import Link from 'next/link'

const features = [
  {
    icon: '🎨',
    title: 'Design sur mesure',
    description: "Téléchargez votre logo ou design et nous l'imprimons avec une qualité professionnelle.",
  },
  {
    icon: '🚀',
    title: 'Livraison express',
    description: "Fabrication et expédition depuis l'UE. Livraison en France en 1–3 jours ouvrés.",
  },
  {
    icon: '💶',
    title: 'Prix transparents',
    description: 'À partir de 27€/pièce en B2C. Tarifs dégressifs B2B dès 10 pièces.',
  },
  {
    icon: '🌱',
    title: 'Éco-responsable',
    description: 'Coton bio GOTS certifié. Impression à la demande, zéro stock gaspillé.',
  },
]

const steps = [
  { step: '01', title: 'Choisissez votre t-shirt', description: 'Couleur, taille, matière — tout est personnalisable.' },
  { step: '02', title: 'Ajoutez votre design', description: 'Téléchargez votre fichier ou contactez notre équipe créative.' },
  { step: '03', title: 'Payez en toute sécurité', description: 'Paiement par carte via Stripe. 3D Secure inclus.' },
  { step: '04', title: 'Recevez en France', description: 'Votre commande arrive chez vous en 1–3 jours ouvrés.' },
]

export default function HomePage() {
  return (
    <div className="flex flex-col">
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-indigo-900 via-indigo-800 to-purple-900 text-white">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 left-10 w-72 h-72 rounded-full bg-white blur-3xl" />
          <div className="absolute bottom-10 right-10 w-96 h-96 rounded-full bg-purple-300 blur-3xl" />
        </div>
        <div className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-36 text-center">
          <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-1.5 text-sm font-medium mb-6 border border-white/20">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            Livraison EU — 1 à 3 jours en France
          </div>
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight leading-tight mb-6">
            Vos t-shirts personnalisés,{' '}
            <span className="text-indigo-300">livrés en France</span>
          </h1>
          <p className="max-w-2xl mx-auto text-lg sm:text-xl text-indigo-100 leading-relaxed mb-10">
            Impression haute qualité sur t-shirts en coton bio. Commande à l'unité ou en gros.
            Idéal pour les entreprises, événements et créateurs.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/products"
              className="inline-flex items-center justify-center gap-2 bg-white text-indigo-900 font-bold text-lg px-8 py-4 rounded-2xl hover:bg-indigo-50 transition-colors shadow-xl"
            >
              Commander maintenant →
            </Link>
            <Link
              href="#comment-ca-marche"
              className="inline-flex items-center justify-center gap-2 border border-white/30 text-white font-medium text-lg px-8 py-4 rounded-2xl hover:bg-white/10 transition-colors"
            >
              Comment ça marche
            </Link>
          </div>
          <p className="mt-6 text-indigo-200 text-sm">
            ✓ Sans minimum de commande &nbsp;·&nbsp; ✓ Paiement sécurisé &nbsp;·&nbsp; ✓ Retours acceptés 30 jours
          </p>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-gray-900 mb-3">Pourquoi choisir H&amp;V Shirts ?</h2>
            <p className="text-gray-500 text-lg max-w-xl mx-auto">
              Qualité européenne, prix compétitifs, délais rapides.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((f) => (
              <div
                key={f.title}
                className="flex flex-col items-center text-center p-6 rounded-2xl border border-gray-100 hover:border-indigo-200 hover:shadow-md transition-all"
              >
                <span className="text-4xl mb-4">{f.icon}</span>
                <h3 className="font-semibold text-gray-900 text-lg mb-2">{f.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="comment-ca-marche" className="py-20 bg-gray-50">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-gray-900 mb-3">Comment ça marche ?</h2>
            <p className="text-gray-500 text-lg">4 étapes simples pour recevoir vos t-shirts.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((s, i) => (
              <div key={s.step} className="relative flex flex-col items-center text-center">
                {i < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-8 left-1/2 w-full h-px bg-indigo-200" />
                )}
                <div className="relative z-10 w-16 h-16 rounded-2xl bg-indigo-600 text-white font-extrabold text-xl flex items-center justify-center mb-4 shadow-lg">
                  {s.step}
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{s.title}</h3>
                <p className="text-gray-500 text-sm">{s.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA banner */}
      <section className="bg-indigo-600 py-16">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Prêt à créer votre t-shirt ?</h2>
          <p className="text-indigo-100 text-lg mb-8">
            Plus de 500 clients satisfaits en France. Rejoignez-nous dès aujourd'hui.
          </p>
          <Link
            href="/products"
            className="inline-flex items-center justify-center bg-white text-indigo-700 font-bold text-lg px-10 py-4 rounded-2xl hover:bg-indigo-50 transition-colors shadow-xl"
          >
            Voir les produits
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between gap-8">
            <div>
              <span className="text-white font-bold text-xl">H&amp;V<span className="text-indigo-400">Shirts</span></span>
              <p className="mt-2 text-sm max-w-xs">
                T-shirts personnalisés imprimés en Europe, livrés en France.
              </p>
            </div>
            <div className="flex flex-col sm:flex-row gap-8 text-sm">
              <div>
                <p className="text-white font-medium mb-2">Navigation</p>
                <ul className="space-y-1">
                  <li><Link href="/" className="hover:text-white transition-colors">Accueil</Link></li>
                  <li><Link href="/products" className="hover:text-white transition-colors">Produits</Link></li>
                  <li><Link href="/cart" className="hover:text-white transition-colors">Panier</Link></li>
                </ul>
              </div>
              <div>
                <p className="text-white font-medium mb-2">Compte</p>
                <ul className="space-y-1">
                  <li><Link href="/login" className="hover:text-white transition-colors">Connexion</Link></li>
                  <li><Link href="/register" className="hover:text-white transition-colors">Inscription</Link></li>
                </ul>
              </div>
              <div>
                <p className="text-white font-medium mb-2">Contact</p>
                <ul className="space-y-1">
                  <li>contact@hvshirts.fr</li>
                  <li>Lun–Ven 9h–18h</li>
                </ul>
              </div>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-10 pt-6 text-center text-xs">
            © {new Date().getFullYear()} H&amp;V Shirts. Tous droits réservés. Paiements sécurisés par Stripe.
          </div>
        </div>
      </footer>
    </div>
  )
}
