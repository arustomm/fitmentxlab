'use client'

import Link from 'next/link'
import Image from 'next/image'
import { useState, useEffect } from 'react'
import { ShoppingCart, Search, Menu, X } from 'lucide-react'
import { useRouter } from 'next/navigation'

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [cartItemCount, setCartItemCount] = useState(0)
  const [searchQuery, setSearchQuery] = useState('')
  const router = useRouter()

  // Update cart count from localStorage
  useEffect(() => {
    const updateCartCount = () => {
      const cart = JSON.parse(localStorage.getItem('cart') || '[]')
      const count = cart.reduce((total: number, item: any) => total + item.quantity, 0)
      setCartItemCount(count)
    }

    updateCartCount()
    
    // Listen for cart updates
    window.addEventListener('cartUpdated', updateCartCount)
    return () => window.removeEventListener('cartUpdated', updateCartCount)
  }, [])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      router.push(`/shop?search=${encodeURIComponent(searchQuery.trim())}`)
      setSearchQuery('')
    }
  }

  const navLinks = [
    { href: '/' as const, label: 'Home' },
    { href: '/shop' as const, label: 'Shop' },
    { href: '/shop?category=Wheels' as const, label: 'Wheels' },
    { href: '/shop?category=Tires' as const, label: 'Tires' },
    { href: '/shop?category=Suspension' as const, label: 'Suspension' },
    { href: '/financing' as const, label: 'Financing' },
    { href: '/about' as const, label: 'About' },
    { href: '/contact' as const, label: 'Contact' },
  ]

  return (
    <header className="bg-dark-surface shadow-dramatic sticky top-0 z-50 border-b border-dark-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center group">
            <div className="relative">
              <Image
                src="/images/fitment-lab-logo.png"
                alt="Fitment Lab"
                width={120}
                height={40}
                className="h-10 w-auto object-contain group-hover:opacity-80 transition-opacity duration-300"
                priority
              />
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="nav-link"
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Search and Cart */}
          <div className="flex items-center space-x-4">
            {/* Search Form */}
            <form onSubmit={handleSearch} className="hidden sm:flex items-center">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search products..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-64 pl-10 pr-4 py-2 bg-dark-card border border-dark-border text-dark-text placeholder-dark-text-secondary rounded-lg focus:ring-2 focus:ring-forest-green focus:border-forest-green outline-none transition-all duration-300"
                />
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-dark-text-secondary w-4 h-4" />
              </div>
            </form>

            {/* Cart */}
            <Link href="/cart" className="relative p-2 text-dark-text hover:text-forest-green transition-colors group">
              <ShoppingCart className="w-6 h-6 group-hover:drop-shadow-lg" />
              {cartItemCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-forest-green text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium shadow-glow animate-pulse">
                  {cartItemCount}
                </span>
              )}
            </Link>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 text-dark-text hover:text-forest-green transition-colors"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Search */}
        <div className="sm:hidden pb-4">
          <form onSubmit={handleSearch} className="flex items-center">
            <div className="relative w-full">
              <input
                type="text"
                placeholder="Search products..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-dark-card border border-dark-border text-dark-text placeholder-dark-text-secondary rounded-lg focus:ring-2 focus:ring-forest-green focus:border-forest-green outline-none transition-all duration-300"
              />
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-dark-text-secondary w-4 h-4" />
            </div>
          </form>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-dark-card border-t border-dark-border shadow-dramatic">
          <nav className="px-4 py-4 space-y-2">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setIsMenuOpen(false)}
                className="block py-2 text-dark-text hover:text-forest-green transition-colors font-medium border-b border-dark-border last:border-b-0"
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  )
}

