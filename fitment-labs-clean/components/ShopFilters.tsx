'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { CategoryChips } from './CategoryChips'
import { Filter, SortAsc } from 'lucide-react'

interface ShopFiltersProps {
  currentCategory: string
  currentSearch: string
  currentSort: string
}

export function ShopFilters({ currentCategory, currentSearch, currentSort }: ShopFiltersProps) {
  const router = useRouter()
  const searchParams = useSearchParams()

  const categories = ['all', 'Wheels', 'Tires', 'Suspension']
  
  const sortOptions = [
    { value: 'newest', label: 'Newest First' },
    { value: 'price-asc', label: 'Price: Low to High' },
    { value: 'price-desc', label: 'Price: High to Low' },
  ]

  const updateFilters = (updates: Record<string, string>) => {
    const params = new URLSearchParams(searchParams.toString())
    
    Object.entries(updates).forEach(([key, value]) => {
      if (value && value !== 'all') {
        params.set(key, value)
      } else {
        params.delete(key)
      }
    })

    // Reset to page 1 when filters change
    params.delete('page')
    
    router.push(`/shop?${params.toString()}`)
  }

  const handleCategoryChange = (category: string) => {
    updateFilters({ category })
  }

  const handleSortChange = (sortBy: string) => {
    updateFilters({ sortBy })
  }

  const clearFilters = () => {
    router.push('/shop')
  }

  const hasActiveFilters = currentCategory !== 'all' || currentSearch || currentSort !== 'newest'

  return (
    <div className="space-y-6">
      {/* Filter Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-charcoal flex items-center gap-2">
          <Filter className="w-5 h-5" />
          Filters
        </h3>
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="text-sm text-forest-green hover:text-forest-green/80 font-medium"
          >
            Clear All
          </button>
        )}
      </div>

      {/* Categories */}
      <div>
        <h4 className="font-medium text-charcoal mb-3">Category</h4>
        <CategoryChips
          categories={categories}
          selectedCategory={currentCategory}
          onCategoryChange={handleCategoryChange}
          className="flex-col items-start"
        />
      </div>

      {/* Sort */}
      <div>
        <h4 className="font-medium text-charcoal mb-3 flex items-center gap-2">
          <SortAsc className="w-4 h-4" />
          Sort By
        </h4>
        <select
          value={currentSort}
          onChange={(e) => handleSortChange(e.target.value)}
          className="w-full input-field"
        >
          {sortOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* Active Filters Summary */}
      {hasActiveFilters && (
        <div className="border-t pt-4">
          <h4 className="font-medium text-charcoal mb-3">Active Filters</h4>
          <div className="space-y-2 text-sm">
            {currentCategory !== 'all' && (
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Category:</span>
                <span className="font-medium">{currentCategory}</span>
              </div>
            )}
            {currentSearch && (
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Search:</span>
                <span className="font-medium">"{currentSearch}"</span>
              </div>
            )}
            {currentSort !== 'newest' && (
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Sort:</span>
                <span className="font-medium">
                  {sortOptions.find(opt => opt.value === currentSort)?.label}
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

