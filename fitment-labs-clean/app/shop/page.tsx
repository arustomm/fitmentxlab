import { Suspense } from 'react'
import { getProducts } from '@/lib/db'
import { ProductCard } from '@/components/ProductCard'
import { ShopFilters } from '@/components/ShopFilters'
import { ProductGrid } from '@/components/ProductGrid'

export const metadata = {
  title: 'Shop - Fitment Labs',
  description: 'Browse our complete selection of wheels, tires, and suspension components.',
}

interface ShopPageProps {
  searchParams: {
    category?: string
    search?: string
    sortBy?: 'price-asc' | 'price-desc' | 'newest'
    page?: string
  }
}

export default async function ShopPage({ searchParams }: ShopPageProps) {
  const category = searchParams.category || 'all'
  const search = searchParams.search || ''
  const sortBy = searchParams.sortBy || 'newest'
  const page = parseInt(searchParams.page || '1')

  const products = await getProducts({
    category: category === 'all' ? undefined : category,
    search: search || undefined,
    sortBy,
  })

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-charcoal mb-2">
          {category === 'all' ? 'All Products' : category}
        </h1>
        <p className="text-gray-600">
          {search && `Search results for "${search}" • `}
          {products.length} product{products.length !== 1 ? 's' : ''} found
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1">
          <Suspense fallback={<div>Loading filters...</div>}>
            <ShopFilters 
              currentCategory={category}
              currentSearch={search}
              currentSort={sortBy}
            />
          </Suspense>
        </div>

        {/* Products Grid */}
        <div className="lg:col-span-3">
          <Suspense fallback={<ProductGridSkeleton />}>
            <ProductGrid products={products} />
          </Suspense>
        </div>
      </div>
    </div>
  )
}

function ProductGridSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: 9 }).map((_, i) => (
        <div key={i} className="card animate-pulse">
          <div className="h-48 bg-gray-200 rounded-t-lg" />
          <div className="p-4 space-y-3">
            <div className="h-4 bg-gray-200 rounded w-3/4" />
            <div className="h-6 bg-gray-200 rounded w-full" />
            <div className="h-4 bg-gray-200 rounded w-5/6" />
            <div className="h-8 bg-gray-200 rounded w-1/2" />
            <div className="h-10 bg-gray-200 rounded w-full" />
          </div>
        </div>
      ))}
    </div>
  )
}

