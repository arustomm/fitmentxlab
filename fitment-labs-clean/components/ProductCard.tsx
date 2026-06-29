import Link from 'next/link'
import Image from 'next/image'
import { PriceTag } from './PriceTag'
import { AddToCartButton } from './AddToCartButton'

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

interface ProductCardProps {
  product: Product
  className?: string
}

export function ProductCard({ product, className = '' }: ProductCardProps) {
  const isInStock = product.inventoryQty > 0
  const isLowStock = product.inventoryQty <= 5

  return (
    <div className={`card group ${className}`}>
      <div className="relative overflow-hidden rounded-t-lg">
        <Link href={`/product/${product.slug}`}>
          <Image
            src={product.imageUrl}
            alt={product.name}
            width={400}
            height={300}
            className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
          />
        </Link>
        
        {/* Badges */}
        <div className="absolute top-3 left-3 flex flex-col gap-2">
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

        {/* Category Badge */}
        <div className="absolute top-3 right-3">
          <span className="badge-category">{product.category}</span>
        </div>
      </div>

      <div className="p-4">
        {/* Brand */}
        <p className="text-sm text-gray-600 mb-1">{product.brand}</p>
        
        {/* Product Name */}
        <Link href={`/product/${product.slug}`}>
          <h3 className="font-semibold text-lg text-charcoal group-hover:text-forest-green transition-colors duration-200 mb-2 line-clamp-2">
            {product.name}
          </h3>
        </Link>

        {/* Description */}
        <p className="text-gray-600 text-sm mb-3 line-clamp-2">
          {product.description}
        </p>

        {/* Price */}
        <div className="mb-4">
          <PriceTag 
            price={product.price} 
            compareAtPrice={product.compareAtPrice} 
          />
        </div>

        {/* Stock Info */}
        <div className="mb-4">
          {isInStock ? (
            <p className="text-sm text-green-600">
              {product.inventoryQty} in stock
            </p>
          ) : (
            <p className="text-sm text-red-600">
              Out of stock
            </p>
          )}
        </div>

        {/* Add to Cart */}
        <AddToCartButton 
          product={product}
          disabled={!isInStock}
          className="w-full"
        />
      </div>
    </div>
  )
}

