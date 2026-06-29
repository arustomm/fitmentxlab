import { notFound } from 'next/navigation'
import Image from 'next/image'
import Link from 'next/link'
import { getProductBySlug, getProductsByCategory } from '@/lib/db'
import { PriceTag } from '@/components/PriceTag'
import { AddToCartButton } from '@/components/AddToCartButton'
import { ProductCard } from '@/components/ProductCard'
import { ArrowLeft, Package, Truck, Shield } from 'lucide-react'

interface ProductPageProps {
  params: {
    slug: string
  }
}

export async function generateMetadata({ params }: ProductPageProps) {
  const product = await getProductBySlug(params.slug)
  
  if (!product) {
    return {
      title: 'Product Not Found - Fitment Labs',
    }
  }

  return {
    title: `${product.name} - ${product.brand} | Fitment Labs`,
    description: product.description,
    openGraph: {
      title: `${product.name} - ${product.brand}`,
      description: product.description,
      images: [product.imageUrl],
    },
  }
}

export default async function ProductPage({ params }: ProductPageProps) {
  const product = await getProductBySlug(params.slug)
  
  if (!product) {
    notFound()
  }

  const relatedProducts = await getProductsByCategory(product.category, 4)
  const otherProducts = relatedProducts.filter(p => p.id !== product.id).slice(0, 3)
  
  const specs = JSON.parse(product.specs)
  const isInStock = product.inventoryQty > 0
  const isLowStock = product.inventoryQty <= 5

  // Generate JSON-LD structured data
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.name,
    description: product.description,
    brand: {
      '@type': 'Brand',
      name: product.brand,
    },
    category: product.category,
    image: product.imageUrl,
    offers: {
      '@type': 'Offer',
      price: product.price,
      priceCurrency: 'USD',
      availability: isInStock ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock',
    },
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <nav className="flex items-center space-x-2 text-sm text-gray-600 mb-8">
          <Link href="/" className="hover:text-forest-green">Home</Link>
          <span>/</span>
          <Link href="/shop" className="hover:text-forest-green">Shop</Link>
          <span>/</span>
          <Link href={`/shop?category=${product.category}`} className="hover:text-forest-green">
            {product.category}
          </Link>
          <span>/</span>
          <span className="text-charcoal font-medium">{product.name}</span>
        </nav>

        {/* Back Button */}
        <Link
          href="/shop"
          className="inline-flex items-center text-forest-green hover:text-forest-green/80 mb-8 font-medium"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Shop
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Product Image */}
          <div className="space-y-4">
            <div className="relative aspect-square overflow-hidden rounded-lg bg-gray-100">
              <Image
                src={product.imageUrl}
                alt={product.name}
                fill
                className="object-cover"
                priority
              />
              
              {/* Badges */}
              <div className="absolute top-4 left-4 flex flex-col gap-2">
                {product.isFeatured && (
                  <span className="badge-featured">Featured</span>
                )}
                {!isInStock && (
                  <span className="badge bg-red-500 text-white">Out of Stock</span>
                )}
                {isInStock && isLowStock && (
                  <span className="badge bg-orange-500 text-white">Low Stock</span>
                )}
              </div>
            </div>
          </div>

          {/* Product Info */}
          <div className="space-y-6">
            {/* Brand and Category */}
            <div className="flex items-center gap-3">
              <span className="badge-category">{product.category}</span>
              <span className="text-gray-600">by {product.brand}</span>
            </div>

            {/* Product Name */}
            <h1 className="text-3xl lg:text-4xl font-bold text-charcoal leading-tight">
              {product.name}
            </h1>

            {/* Price */}
            <div className="space-y-2">
              <PriceTag 
                price={product.price} 
                compareAtPrice={product.compareAtPrice}
                className="text-2xl"
              />
            </div>

            {/* Description */}
            <p className="text-gray-700 text-lg leading-relaxed">
              {product.description}
            </p>

            {/* Stock Status */}
            <div className="flex items-center gap-2">
              <Package className="w-5 h-5 text-gray-500" />
              {isInStock ? (
                <span className="text-green-600 font-medium">
                  {product.inventoryQty} in stock
                </span>
              ) : (
                <span className="text-red-600 font-medium">
                  Out of stock
                </span>
              )}
            </div>

            {/* Add to Cart */}
            <div className="space-y-4">
              <AddToCartButton 
                product={product}
                disabled={!isInStock}
                className="w-full text-lg py-4"
              />
              
              {/* Features */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                <div className="flex items-center gap-2 text-gray-600">
                  <Truck className="w-4 h-4" />
                  Free shipping over $500
                </div>
                <div className="flex items-center gap-2 text-gray-600">
                  <Shield className="w-4 h-4" />
                  Manufacturer warranty
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Specifications */}
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-charcoal mb-6">Specifications</h2>
          <div className="card p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(specs).map(([key, value]) => (
                <div key={key} className="flex justify-between py-2 border-b border-gray-100 last:border-b-0">
                  <span className="font-medium text-charcoal capitalize">
                    {key.replace(/([A-Z])/g, ' $1').trim()}:
                  </span>
                  <span className="text-gray-700">{value as string}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Related Products */}
        {otherProducts.length > 0 && (
          <div className="mt-16">
            <h2 className="text-2xl font-bold text-charcoal mb-6">
              More {product.category}
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {otherProducts.map((relatedProduct) => (
                <ProductCard key={relatedProduct.id} product={relatedProduct} />
              ))}
            </div>
          </div>
        )}
      </div>
    </>
  )
}

