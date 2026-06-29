interface PriceTagProps {
  price: number
  compareAtPrice?: number | null
  className?: string
}

export function PriceTag({ price, compareAtPrice, className = '' }: PriceTagProps) {
  const hasDiscount = compareAtPrice && compareAtPrice > price
  const discountPercentage = hasDiscount 
    ? Math.round(((compareAtPrice - price) / compareAtPrice) * 100)
    : 0

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className="price-tag">
        ${price.toFixed(2)}
      </span>
      
      {hasDiscount && (
        <>
          <span className="price-compare">
            ${compareAtPrice.toFixed(2)}
          </span>
          <span className="text-xs bg-red-100 text-red-600 px-2 py-1 rounded-full font-medium">
            -{discountPercentage}%
          </span>
        </>
      )}
    </div>
  )
}

