import { ProductCard } from './ProductCard'

interface Product {
  id: string
  slug: string
  name: string
  brand: string
  category: string
  description: string
  price: number
  compareAtPrice?: number | null
  imageUrl: string
  specs: string
  inventoryQty: number
  isFeatured: boolean
}

interface ProductGridProps {
  products: Product[]
  className?: string
}

export function ProductGrid({ products, className = '' }: ProductGridProps) {
  if (products.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
          <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2M4 13h2m13-8l-4 4m0 0l-4-4m4 4V3" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-charcoal mb-2">No products found</h3>
        <p className="text-gray-600 mb-4">
          Try adjusting your search or filter criteria to find what you're looking for.
        </p>
        <button
          onClick={() => window.location.href = '/shop'}
          className="btn-outline"
        >
          View All Products
        </button>
      </div>
    )
  }

  return (
    <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 ${className}`}>
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  )
}

