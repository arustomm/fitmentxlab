'use client'

import { useState, useEffect } from 'react'

export function PromoBanner() {
  const [isVisible, setIsVisible] = useState(true)

  if (!isVisible) return null

  return (
    <div className="bg-chili-red text-white py-2 px-4 relative overflow-hidden sticky top-16 z-40">
      <div className="flex items-center justify-center">
        <div className="animate-marquee whitespace-nowrap text-sm font-bold tracking-wide">
          ENJOY 0% APR FINANCING OR AS LOW AS $1 INITIAL LEASE PAYMENT - UPGRADE NOW, PAY LATER
        </div>
        <button
          onClick={() => setIsVisible(false)}
          className="absolute right-4 top-1/2 transform -translate-y-1/2 text-white hover:text-gray-200 transition-colors"
          aria-label="Close banner"
        >
          ×
        </button>
      </div>
      
      <style jsx>{`
        @keyframes marquee {
          0% {
            transform: translateX(100%);
          }
          100% {
            transform: translateX(-100%);
          }
        }
        
        .animate-marquee {
          animation: marquee 20s linear infinite;
        }
        
        @media (max-width: 768px) {
          .animate-marquee {
            animation: marquee 15s linear infinite;
          }
        }
      `}</style>
    </div>
  )
}

