'use client'

import { useState } from 'react'
import { ChevronDown } from 'lucide-react'

interface FitmentData {
  year: string
  make: string
  model: string
  trimLevel: string
  drive: string
}

export function FitmentFilter() {
  const [fitmentData, setFitmentData] = useState<FitmentData>({
    year: '',
    make: '',
    model: '',
    trimLevel: '',
    drive: ''
  })

  // Sample data - in a real app, this would come from an API
  const years = Array.from({ length: 30 }, (_, i) => (2024 - i).toString())
  
  const makes = [
    'Acura', 'Audi', 'BMW', 'Cadillac', 'Chevrolet', 'Chrysler', 'Dodge', 
    'Ford', 'GMC', 'Honda', 'Hyundai', 'Infiniti', 'Jeep', 'Kia', 'Lexus',
    'Lincoln', 'Mazda', 'Mercedes-Benz', 'Mitsubishi', 'Nissan', 'Ram',
    'Subaru', 'Tesla', 'Toyota', 'Volkswagen', 'Volvo'
  ]

  const models = fitmentData.make ? [
    'Model S', 'Model 3', 'Model X', 'Model Y', 'Civic', 'Accord', 'CR-V',
    'Pilot', 'F-150', 'Mustang', 'Explorer', 'Silverado', 'Tahoe', 'Camaro',
    'Corvette', 'Wrangler', 'Grand Cherokee', 'Cherokee', 'Compass'
  ] : []

  const trimLevels = fitmentData.model ? [
    'Base', 'LX', 'EX', 'EX-L', 'Touring', 'Sport', 'Limited', 'Premium',
    'Luxury', 'Performance', 'Hybrid', 'Electric'
  ] : []

  const driveTypes = [
    'FWD', 'RWD', 'AWD', '4WD'
  ]

  const handleInputChange = (field: keyof FitmentData, value: string) => {
    setFitmentData(prev => ({
      ...prev,
      [field]: value,
      // Reset dependent fields when parent changes
      ...(field === 'make' && { model: '', trimLevel: '' }),
      ...(field === 'model' && { trimLevel: '' })
    }))
  }

  const handleShopNow = () => {
    // In a real app, this would filter products based on fitment
    const params = new URLSearchParams()
    Object.entries(fitmentData).forEach(([key, value]) => {
      if (value) params.set(key, value)
    })
    
    window.location.href = `/shop?${params.toString()}`
  }

  const isComplete = Object.values(fitmentData).every(value => value !== '')

  return (
    <div className="bg-gradient-overlay rounded-2xl p-8 backdrop-blur-sm border border-dark-border shadow-dramatic">
      <div className="text-center mb-6">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-2">
          FIND WHAT FITS YOUR RIDE
        </h2>
        <p className="text-accent-gold text-lg font-semibold">
          CAR WHEELS, TIRES, SUSPENSION & MORE
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
        {/* Year */}
        <div className="relative">
          <select
            value={fitmentData.year}
            onChange={(e) => handleInputChange('year', e.target.value)}
            className="w-full bg-white text-dark-bg font-medium py-3 px-4 pr-10 rounded-lg appearance-none focus:outline-none focus:ring-2 focus:ring-forest-green cursor-pointer"
          >
            <option value="">YEAR</option>
            {years.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-bg pointer-events-none" />
        </div>

        {/* Make */}
        <div className="relative">
          <select
            value={fitmentData.make}
            onChange={(e) => handleInputChange('make', e.target.value)}
            className="w-full bg-white text-dark-bg font-medium py-3 px-4 pr-10 rounded-lg appearance-none focus:outline-none focus:ring-2 focus:ring-forest-green cursor-pointer"
            disabled={!fitmentData.year}
          >
            <option value="">MAKE</option>
            {makes.map(make => (
              <option key={make} value={make}>{make}</option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-bg pointer-events-none" />
        </div>

        {/* Model */}
        <div className="relative">
          <select
            value={fitmentData.model}
            onChange={(e) => handleInputChange('model', e.target.value)}
            className="w-full bg-white text-dark-bg font-medium py-3 px-4 pr-10 rounded-lg appearance-none focus:outline-none focus:ring-2 focus:ring-forest-green cursor-pointer"
            disabled={!fitmentData.make}
          >
            <option value="">MODEL</option>
            {models.map(model => (
              <option key={model} value={model}>{model}</option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-bg pointer-events-none" />
        </div>

        {/* Trim Level */}
        <div className="relative">
          <select
            value={fitmentData.trimLevel}
            onChange={(e) => handleInputChange('trimLevel', e.target.value)}
            className="w-full bg-white text-dark-bg font-medium py-3 px-4 pr-10 rounded-lg appearance-none focus:outline-none focus:ring-2 focus:ring-forest-green cursor-pointer"
            disabled={!fitmentData.model}
          >
            <option value="">TRIM LEVEL</option>
            {trimLevels.map(trim => (
              <option key={trim} value={trim}>{trim}</option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-bg pointer-events-none" />
        </div>

        {/* Drive */}
        <div className="relative">
          <select
            value={fitmentData.drive}
            onChange={(e) => handleInputChange('drive', e.target.value)}
            className="w-full bg-white text-dark-bg font-medium py-3 px-4 pr-10 rounded-lg appearance-none focus:outline-none focus:ring-2 focus:ring-forest-green cursor-pointer"
            disabled={!fitmentData.trimLevel}
          >
            <option value="">DRIVE</option>
            {driveTypes.map(drive => (
              <option key={drive} value={drive}>{drive}</option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-bg pointer-events-none" />
        </div>
      </div>

      <div className="text-center">
        <button
          onClick={handleShopNow}
          disabled={!isComplete}
          className={`px-8 py-3 rounded-full font-bold text-lg transition-all duration-300 ${
            isComplete
              ? 'bg-accent-gold text-dark-bg hover:bg-yellow-400 hover:shadow-glow-gold transform hover:scale-105'
              : 'bg-gray-400 text-gray-600 cursor-not-allowed'
          }`}
        >
          SHOP NOW
        </button>
      </div>

      {!isComplete && (
        <p className="text-center text-dark-text-secondary text-sm mt-2">
          Please select all vehicle details to continue
        </p>
      )}
    </div>
  )
}

