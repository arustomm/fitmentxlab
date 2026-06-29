'use client'

import { useState } from 'react'
import { ShoppingCart, Plus } from 'lucide-react'
import toast from 'react-hot-toast'

interface Product {
  id: string
  slug: string
  name: string
  brand: string
  price: number
  imageUrl: string
  inventoryQty: number
}

interface AddToCartButtonProps {
  product: Product
  quantity?: number
  disabled?: boolean
  className?: string
}

export function AddToCartButton({ 
  product, 
  quantity = 1, 
  disabled = false, 
  className = '' 
}: AddToCartButtonProps) {
  const [isAdding, setIsAdding] = useState(false)

  const addToCart = async () => {
    if (disabled || isAdding) return

    setIsAdding(true)

    try {
      // Get existing cart
      const existingCart = JSON.parse(localStorage.getItem('cart') || '[]')
      
      // Check if product already exists in cart
      const existingItemIndex = existingCart.findIndex((item: any) => item.id === product.id)
      
      if (existingItemIndex >= 0) {
        // Update quantity
        const newQuantity = existingCart[existingItemIndex].quantity + quantity
        
        // Check inventory
        if (newQuantity > product.inventoryQty) {
          toast.error(`Only ${product.inventoryQty} items available`)
          return
        }
        
        existingCart[existingItemIndex].quantity = newQuantity
      } else {
        // Add new item
        if (quantity > product.inventoryQty) {
          toast.error(`Only ${product.inventoryQty} items available`)
          return
        }
        
        existingCart.push({
          id: product.id,
          slug: product.slug,
          name: product.name,
          brand: product.brand,
          price: product.price,
          imageUrl: product.imageUrl,
          quantity: quantity,
          maxQuantity: product.inventoryQty,
        })
      }

      // Save to localStorage
      localStorage.setItem('cart', JSON.stringify(existingCart))
      
      // Dispatch custom event to update cart count
      window.dispatchEvent(new Event('cartUpdated'))
      
      toast.success(`${product.name} added to cart!`)
    } catch (error) {
      toast.error('Failed to add item to cart')
      console.error('Add to cart error:', error)
    } finally {
      setIsAdding(false)
    }
  }

  return (
    <button
      onClick={addToCart}
      disabled={disabled || isAdding}
      className={`btn-primary flex items-center justify-center gap-2 ${className}`}
    >
      {isAdding ? (
        <>
          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          Adding...
        </>
      ) : (
        <>
          <ShoppingCart className="w-4 h-4" />
          Add to Cart
        </>
      )}
    </button>
  )
}

