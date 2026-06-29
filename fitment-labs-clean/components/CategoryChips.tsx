'use client'

interface CategoryChipsProps {
  categories: string[]
  selectedCategory: string
  onCategoryChange: (category: string) => void
  className?: string
}

export function CategoryChips({ 
  categories, 
  selectedCategory, 
  onCategoryChange, 
  className = '' 
}: CategoryChipsProps) {
  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {categories.map((category) => (
        <button
          key={category}
          onClick={() => onCategoryChange(category)}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
            selectedCategory === category
              ? 'bg-forest-green text-white shadow-md'
              : 'bg-gray-100 text-charcoal hover:bg-gray-200'
          }`}
        >
          {category === 'all' ? 'All Products' : category}
        </button>
      ))}
    </div>
  )
}

