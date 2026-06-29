'use client'

import { useEffect, useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { CheckCircle, Package, Truck, Mail } from 'lucide-react'

function SuccessContent() {
  const searchParams = useSearchParams()
  const sessionId = searchParams.get('session_id')
  const [orderItems, setOrderItems] = useState<any[]>([])

  useEffect(() => {
    // Clear the cart after successful checkout
    localStorage.removeItem('cart')
    window.dispatchEvent(new Event('cartUpdated'))

    // Get order items from localStorage if available (for mock checkout)
    const cart = JSON.parse(localStorage.getItem('cart') || '[]')
    if (cart.length > 0) {
      setOrderItems(cart)
      localStorage.removeItem('cart')
    }
  }, [])

  const orderNumber = sessionId ? sessionId.slice(-8).toUpperCase() : 'FL' + Date.now().toString().slice(-6)

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center">
        {/* Success Icon */}
        <div className="flex justify-center mb-6">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
        </div>

        {/* Success Message */}
        <h1 className="text-3xl lg:text-4xl font-bold text-charcoal mb-4">
          Order Confirmed!
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Thank you for your purchase. Your order has been successfully placed.
        </p>

        {/* Order Details */}
        <div className="card p-6 mb-8 text-left">
          <h2 className="text-xl font-semibold text-charcoal mb-4">Order Details</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            <div>
              <p className="text-sm text-gray-600">Order Number</p>
              <p className="font-semibold text-charcoal">{orderNumber}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Order Date</p>
              <p className="font-semibold text-charcoal">
                {new Date().toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </p>
            </div>
          </div>

          {sessionId && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Session ID</p>
              <p className="font-mono text-sm text-charcoal break-all">{sessionId}</p>
            </div>
          )}
        </div>

        {/* What's Next */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Mail className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="font-semibold text-charcoal mb-2">Confirmation Email</h3>
            <p className="text-sm text-gray-600">
              You'll receive an order confirmation email shortly with all the details.
            </p>
          </div>

          <div className="text-center">
            <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Package className="w-6 h-6 text-orange-600" />
            </div>
            <h3 className="font-semibold text-charcoal mb-2">Processing</h3>
            <p className="text-sm text-gray-600">
              Your order will be processed and prepared for shipment within 1-2 business days.
            </p>
          </div>

          <div className="text-center">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Truck className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="font-semibold text-charcoal mb-2">Shipping</h3>
            <p className="text-sm text-gray-600">
              You'll receive tracking information once your order ships.
            </p>
          </div>
        </div>

        {/* Contact Info */}
        <div className="bg-forest-green text-white p-6 rounded-lg mb-8">
          <h3 className="font-semibold mb-2">Need Help?</h3>
          <p className="mb-4">
            If you have any questions about your order, don't hesitate to contact us.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="mailto:info@fitmentlabs.com" className="hover:underline">
              📧 info@fitmentlabs.com
            </a>
            <a href="tel:+15551234567" className="hover:underline">
              📞 (555) 123-4567
            </a>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/shop" className="btn-primary">
            Continue Shopping
          </Link>
          <Link href="/" className="btn-outline">
            Back to Home
          </Link>
        </div>

        {/* Test Card Info */}
        <div className="mt-12 p-6 bg-gray-50 rounded-lg text-left">
          <h3 className="font-semibold text-charcoal mb-3">Test Mode Information</h3>
          <p className="text-sm text-gray-600 mb-4">
            This is a demo store running in test mode. No real payments were processed.
          </p>
          <div className="text-xs text-gray-500 space-y-1">
            <p><strong>Test Cards for Development:</strong></p>
            <p>• Success: 4242 4242 4242 4242 (any future expiry, any CVC, any ZIP)</p>
            <p>• Decline: 4000 0000 0000 9995</p>
            <p>• Insufficient funds: 4000 0000 0000 9999</p>
            <p>• Requires 3D Secure: 4000 0025 0000 3155</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function SuccessPage() {
  return (
    <Suspense fallback={
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <div className="animate-pulse">
            <div className="w-20 h-20 bg-gray-200 rounded-full mx-auto mb-6"></div>
            <div className="h-8 bg-gray-200 rounded w-64 mx-auto mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-96 mx-auto mb-8"></div>
          </div>
        </div>
      </div>
    }>
      <SuccessContent />
    </Suspense>
  )
}

