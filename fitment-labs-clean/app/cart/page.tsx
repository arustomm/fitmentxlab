'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { QuantityInput } from '@/components/QuantityInput'
import { PriceTag } from '@/components/PriceTag'
import { Trash2, ShoppingBag, ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'

interface CartItem {
  id: string
  slug: string
  name: string
  brand: string
  price: number
  imageUrl: string
  quantity: number
  maxQuantity: number
}

export default function CartPage() {
  const [cartItems, setCartItems] = useState<CartItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isCheckingOut, setIsCheckingOut] = useState(false)

  useEffect(() => {
    loadCart()
  }, [])

  const loadCart = () => {
    try {
      const cart = JSON.parse(localStorage.getItem('cart') || '[]')
      setCartItems(cart)
    } catch (error) {
      console.error('Error loading cart:', error)
      setCartItems([])
    } finally {
      setIsLoading(false)
    }
  }

  const updateCart = (newCart: CartItem[]) => {
    setCartItems(newCart)
    localStorage.setItem('cart', JSON.stringify(newCart))
    window.dispatchEvent(new Event('cartUpdated'))
  }

  const updateQuantity = (itemId: string, newQuantity: number) => {
    const updatedCart = cartItems.map(item => {
      if (item.id === itemId) {
        if (newQuantity > item.maxQuantity) {
          toast.error(`Only ${item.maxQuantity} items available`)
          return item
        }
        return { ...item, quantity: newQuantity }
      }
      return item
    })
    updateCart(updatedCart)
  }

  const removeItem = (itemId: string) => {
    const updatedCart = cartItems.filter(item => item.id !== itemId)
    updateCart(updatedCart)
    toast.success('Item removed from cart')
  }

  const clearCart = () => {
    updateCart([])
    toast.success('Cart cleared')
  }

  const subtotal = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0)
  const shipping = subtotal >= 500 ? 0 : 49.99
  const tax = subtotal * 0.08 // 8% tax
  const total = subtotal + shipping + tax

  const handleCheckout = async () => {
    if (cartItems.length === 0) return

    setIsCheckingOut(true)

    try {
      const response = await fetch('/api/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ items: cartItems }),
      })

      const data = await response.json()

      if (response.ok && data.url) {
        window.location.href = data.url
      } else {
        throw new Error(data.error || 'Checkout failed')
      }
    } catch (error) {
      console.error('Checkout error:', error)
      toast.error('Checkout failed. Please try again.')
    } finally {
      setIsCheckingOut(false)
    }
  }

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (cartItems.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <ShoppingBag className="w-24 h-24 text-gray-300 mx-auto mb-6" />
          <h1 className="text-3xl font-bold text-charcoal mb-4">Your cart is empty</h1>
          <p className="text-gray-600 mb-8">
            Looks like you haven't added any items to your cart yet.
          </p>
          <Link href="/shop" className="btn-primary inline-flex items-center">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Continue Shopping
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-charcoal">Shopping Cart</h1>
        <button
          onClick={clearCart}
          className="text-red-600 hover:text-red-700 text-sm font-medium"
        >
          Clear Cart
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cart Items */}
        <div className="lg:col-span-2 space-y-4">
          {cartItems.map((item) => (
            <div key={item.id} className="card p-4">
              <div className="flex items-center space-x-4">
                {/* Product Image */}
                <Link href={`/product/${item.slug}`} className="flex-shrink-0">
                  <Image
                    src={item.imageUrl}
                    alt={item.name}
                    width={80}
                    height={80}
                    className="rounded-lg object-cover"
                  />
                </Link>

                {/* Product Info */}
                <div className="flex-1 min-w-0">
                  <Link
                    href={`/product/${item.slug}`}
                    className="text-sm text-gray-600 hover:text-forest-green"
                  >
                    {item.brand}
                  </Link>
                  <h3 className="font-semibold text-charcoal hover:text-forest-green">
                    <Link href={`/product/${item.slug}`}>
                      {item.name}
                    </Link>
                  </h3>
                  <PriceTag price={item.price} className="mt-1" />
                </div>

                {/* Quantity Controls */}
                <div className="flex items-center space-x-4">
                  <QuantityInput
                    value={item.quantity}
                    onChange={(quantity) => updateQuantity(item.id, quantity)}
                    min={1}
                    max={item.maxQuantity}
                  />
                  
                  <button
                    onClick={() => removeItem(item.id)}
                    className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                {/* Item Total */}
                <div className="text-right">
                  <p className="font-semibold text-charcoal">
                    ${(item.price * item.quantity).toFixed(2)}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <div className="card p-6 sticky top-8">
            <h2 className="text-xl font-semibold text-charcoal mb-4">Order Summary</h2>
            
            <div className="space-y-3 mb-6">
              <div className="flex justify-between">
                <span className="text-gray-600">Subtotal</span>
                <span className="font-medium">${subtotal.toFixed(2)}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-600">Shipping</span>
                <span className="font-medium">
                  {shipping === 0 ? 'Free' : `$${shipping.toFixed(2)}`}
                </span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-600">Tax</span>
                <span className="font-medium">${tax.toFixed(2)}</span>
              </div>
              
              <div className="border-t pt-3">
                <div className="flex justify-between">
                  <span className="text-lg font-semibold text-charcoal">Total</span>
                  <span className="text-lg font-semibold text-charcoal">
                    ${total.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>

            {shipping > 0 && (
              <div className="bg-blue-50 p-3 rounded-lg mb-4">
                <p className="text-sm text-blue-700">
                  Add ${(500 - subtotal).toFixed(2)} more for free shipping!
                </p>
              </div>
            )}

            <button
              onClick={handleCheckout}
              disabled={isCheckingOut}
              className="btn-primary w-full mb-3"
            >
              {isCheckingOut ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Processing...
                </>
              ) : (
                'Pay Now - Checkout'
              )}
            </button>

            <div className="text-center mb-4">
              <span className="text-gray-500 text-sm">or</span>
            </div>

            <Link
              href="/financing"
              className="btn-outline w-full text-center inline-block mb-4 bg-accent-orange text-white hover:bg-accent-red border-accent-orange hover:border-accent-red"
            >
              Apply for Financing
            </Link>

            <Link
              href="/shop"
              className="btn-outline w-full text-center inline-block"
            >
              Continue Shopping
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

