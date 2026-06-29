import Image from 'next/image'
import Link from 'next/link'
import { getFeaturedProducts } from '@/lib/db'
import { ProductCard } from '@/components/ProductCard'
import { FitmentFilter } from '@/components/FitmentFilter'
import { ArrowRight, Zap, Shield, Truck } from 'lucide-react'

export const metadata = {
  title: 'Fitment Labs - Premium Wheels, Tires & Suspension',
  description: 'Discover high-performance wheels, tires, and suspension components. Bold, modern, performance-driven automotive parts.',
}

export default async function HomePage() {
  const featuredProducts = await getFeaturedProducts(8)

  const categories = [
    {
      name: 'Wheels',
      description: 'Premium forged and flow-formed wheels',
      image: '/images/products/kg1-victor.jpg',
      href: '/shop?category=Wheels' as const,
    },
    {
      name: 'Tires',
      description: 'High-performance and all-terrain tires',
      image: '/images/products/nitto-ridge-grappler-tire.png',
      href: '/shop?category=Tires' as const,
    },
    {
      name: 'Suspension',
      description: 'Lift kits and performance suspension',
      image: '/images/products/bds-suspension-lift-kit.png',
      href: '/shop?category=Suspension' as const,
    },
  ]

  const features = [
    {
      icon: Zap,
      title: 'Performance Driven',
      description: 'Every product is selected for maximum performance and reliability.',
    },
    {
      icon: Shield,
      title: 'Quality Guaranteed',
      description: 'All products come with manufacturer warranties and our quality promise.',
    },
    {
      icon: Truck,
      title: 'Fast Shipping',
      description: 'Free shipping on orders over $500. Most items ship within 24 hours.',
    },
  ]

  return (
    <div>
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Background Image */}
        <div className="absolute inset-0 z-0">
          <Image
            src="/images/hero-truck.png"
            alt="Custom Lifted Truck with Premium Wheels"
            fill
            className="object-cover object-center"
            priority
          />
          <div className="absolute inset-0 bg-gradient-overlay"></div>
        </div>

        {/* Content */}
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight text-white drop-shadow-2xl">
              Performance
              <span className="block text-accent-gold">Redefined</span>
            </h1>
            <p className="text-xl lg:text-2xl mb-8 text-white drop-shadow-lg max-w-3xl mx-auto">
              Discover premium wheels, tires, and suspension components that deliver 
              uncompromising performance and bold style.
            </p>
          </div>

          {/* Fitment Filter */}
          <div className="mb-12">
            <FitmentFilter />
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/shop" className="btn-primary inline-flex items-center justify-center text-lg px-8 py-4">
              Shop Now
              <ArrowRight className="ml-2 w-6 h-6" />
            </Link>
            <Link href="/about" className="btn-outline border-white text-white hover:bg-white hover:text-dark-bg text-lg px-8 py-4">
              Learn More
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-forest-green text-white rounded-full mb-4">
                  <feature.icon className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-semibold text-charcoal mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl lg:text-4xl font-bold text-charcoal mb-4">
              Shop by Category
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Find the perfect components for your build from our curated selection 
              of premium automotive parts.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {categories.map((category) => (
              <Link
                key={category.name}
                href={category.href}
                className="group card overflow-hidden hover:shadow-xl transition-all duration-300"
              >
                <div className="relative h-64 overflow-hidden">
                  <Image
                    src={category.image}
                    alt={category.name}
                    fill
                    className="object-cover group-hover:scale-110 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-40 group-hover:bg-opacity-30 transition-all duration-300" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center text-white">
                      <h3 className="text-2xl font-bold mb-2">{category.name}</h3>
                      <p className="text-gray-200">{category.description}</p>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl lg:text-4xl font-bold text-charcoal mb-4">
              Featured Products
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Hand-picked products that represent the best in performance, 
              quality, and style.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {featuredProducts.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>

          <div className="text-center">
            <Link href="/shop" className="btn-primary inline-flex items-center">
              View All Products
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}

