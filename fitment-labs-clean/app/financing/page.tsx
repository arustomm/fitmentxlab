'use client'

import { useState } from 'react'
import { CreditCard, Shield, Clock, CheckCircle } from 'lucide-react'

interface FinancingFormData {
  // Personal Information
  firstName: string
  lastName: string
  address: string
  city: string
  state: string
  zip: string
  yearsAtAddress: string
  rentOrOwn: string
  phone: string
  email: string
  ssn: string
  birthdate: string
  driverLicenseNumber: string
  driverLicenseState: string
  driverLicenseExpiration: string
  
  // Income Information
  employmentStatus: string
  yearsEmployed: string
  employerName: string
  employerPhone: string
  monthlyIncome: string
  payFrequency: string
  
  // Reference Information
  reference1Name: string
  reference1Phone: string
  reference2Name: string
  reference2Phone: string
  
  // Payment Information
  routingNumber: string
  accountNumber: string
  yearsAccountOpen: string
  creditCardNumber: string
  cardExpiration: string
  cardVerification: string
}

export default function FinancingPage() {
  const [formData, setFormData] = useState<FinancingFormData>({
    firstName: '',
    lastName: '',
    address: '',
    city: '',
    state: '',
    zip: '',
    yearsAtAddress: '',
    rentOrOwn: '',
    phone: '',
    email: '',
    ssn: '',
    birthdate: '',
    driverLicenseNumber: '',
    driverLicenseState: '',
    driverLicenseExpiration: '',
    employmentStatus: '',
    yearsEmployed: '',
    employerName: '',
    employerPhone: '',
    monthlyIncome: '',
    payFrequency: '',
    reference1Name: '',
    reference1Phone: '',
    reference2Name: '',
    reference2Phone: '',
    routingNumber: '',
    accountNumber: '',
    yearsAccountOpen: '',
    creditCardNumber: '',
    cardExpiration: '',
    cardVerification: '',
  })

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      // Send form data to email endpoint
      const response = await fetch('/api/financing', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        setIsSubmitted(true)
      } else {
        throw new Error('Failed to submit application')
      }
    } catch (error) {
      console.error('Error submitting financing application:', error)
      alert('There was an error submitting your application. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isSubmitted) {
    return (
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
          <h1 className="text-3xl font-bold text-charcoal mb-4">Application Submitted!</h1>
          <p className="text-xl text-gray-600 mb-8">
            Thank you for your financing application. We'll review your information and get back to you within 24-48 hours.
          </p>
          <div className="bg-gray-50 p-6 rounded-lg mb-8">
            <h3 className="font-semibold text-charcoal mb-2">What's Next?</h3>
            <ul className="text-left text-gray-600 space-y-2">
              <li>• We'll review your application within 24-48 hours</li>
              <li>• You'll receive an email confirmation shortly</li>
              <li>• Our financing team may contact you for additional information</li>
              <li>• Once approved, you can complete your purchase</li>
            </ul>
          </div>
          <a href="/shop" className="btn-primary">
            Continue Shopping
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-charcoal mb-4">Financing Application</h1>
        <p className="text-xl text-gray-600 mb-8">
          Get approved for financing and drive away with your dream setup today.
        </p>
        
        {/* Benefits */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="text-center">
            <div className="w-12 h-12 bg-accent-orange bg-opacity-10 rounded-full flex items-center justify-center mx-auto mb-3">
              <Clock className="w-6 h-6 text-accent-orange" />
            </div>
            <h3 className="font-semibold text-charcoal mb-2">Quick Approval</h3>
            <p className="text-sm text-gray-600">Get approved in as little as 24 hours</p>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-accent-orange bg-opacity-10 rounded-full flex items-center justify-center mx-auto mb-3">
              <CreditCard className="w-6 h-6 text-accent-orange" />
            </div>
            <h3 className="font-semibold text-charcoal mb-2">Flexible Terms</h3>
            <p className="text-sm text-gray-600">Choose payment terms that work for you</p>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-accent-orange bg-opacity-10 rounded-full flex items-center justify-center mx-auto mb-3">
              <Shield className="w-6 h-6 text-accent-orange" />
            </div>
            <h3 className="font-semibold text-charcoal mb-2">Secure Process</h3>
            <p className="text-sm text-gray-600">Your information is protected and secure</p>
          </div>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Personal Information */}
        <div className="card p-6">
          <h2 className="text-2xl font-semibold text-charcoal mb-6">Personal Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">First Name *</label>
              <input
                type="text"
                name="firstName"
                value={formData.firstName}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Last Name *</label>
              <input
                type="text"
                name="lastName"
                value={formData.lastName}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Address *</label>
              <input
                type="text"
                name="address"
                value={formData.address}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">City *</label>
              <input
                type="text"
                name="city"
                value={formData.city}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">State *</label>
              <input
                type="text"
                name="state"
                value={formData.state}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">ZIP Code *</label>
              <input
                type="text"
                name="zip"
                value={formData.zip}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Years at Address *</label>
              <input
                type="text"
                name="yearsAtAddress"
                value={formData.yearsAtAddress}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Do You Rent or Own? *</label>
              <select
                name="rentOrOwn"
                value={formData.rentOrOwn}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              >
                <option value="">Select...</option>
                <option value="rent">Rent</option>
                <option value="own">Own</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Phone *</label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">SSN *</label>
              <input
                type="text"
                name="ssn"
                value={formData.ssn}
                onChange={handleInputChange}
                required
                placeholder="XXX-XX-XXXX"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Birthdate *</label>
              <input
                type="date"
                name="birthdate"
                value={formData.birthdate}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Driver's License Number *</label>
              <input
                type="text"
                name="driverLicenseNumber"
                value={formData.driverLicenseNumber}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">License State *</label>
              <input
                type="text"
                name="driverLicenseState"
                value={formData.driverLicenseState}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">License Expiration *</label>
              <input
                type="date"
                name="driverLicenseExpiration"
                value={formData.driverLicenseExpiration}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
          </div>
        </div>

        {/* Income Information */}
        <div className="card p-6">
          <h2 className="text-2xl font-semibold text-charcoal mb-6">Income Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Employment Status *</label>
              <select
                name="employmentStatus"
                value={formData.employmentStatus}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              >
                <option value="">Select...</option>
                <option value="employed-fulltime">Employed Full-Time</option>
                <option value="employed-parttime">Employed Part-Time</option>
                <option value="self-employed">Self-Employed</option>
                <option value="social-security">Social Security</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Years Employed *</label>
              <input
                type="text"
                name="yearsEmployed"
                value={formData.yearsEmployed}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Employer Name *</label>
              <input
                type="text"
                name="employerName"
                value={formData.employerName}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Employer Phone *</label>
              <input
                type="tel"
                name="employerPhone"
                value={formData.employerPhone}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Monthly Income *</label>
              <input
                type="text"
                name="monthlyIncome"
                value={formData.monthlyIncome}
                onChange={handleInputChange}
                required
                placeholder="$0.00"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Pay Frequency *</label>
              <select
                name="payFrequency"
                value={formData.payFrequency}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              >
                <option value="">Select...</option>
                <option value="weekly">Weekly</option>
                <option value="biweekly">Bi-weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
          </div>
        </div>

        {/* Reference Information */}
        <div className="card p-6">
          <h2 className="text-2xl font-semibold text-charcoal mb-6">Reference Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Reference 1 Name *</label>
              <input
                type="text"
                name="reference1Name"
                value={formData.reference1Name}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Reference 1 Phone *</label>
              <input
                type="tel"
                name="reference1Phone"
                value={formData.reference1Phone}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Reference 2 Name *</label>
              <input
                type="text"
                name="reference2Name"
                value={formData.reference2Name}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Reference 2 Phone *</label>
              <input
                type="tel"
                name="reference2Phone"
                value={formData.reference2Phone}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
          </div>
        </div>

        {/* Payment Information */}
        <div className="card p-6">
          <h2 className="text-2xl font-semibold text-charcoal mb-6">Payment Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Routing Number *</label>
              <input
                type="text"
                name="routingNumber"
                value={formData.routingNumber}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Account Number *</label>
              <input
                type="text"
                name="accountNumber"
                value={formData.accountNumber}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Years Account Open *</label>
              <input
                type="text"
                name="yearsAccountOpen"
                value={formData.yearsAccountOpen}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Credit Card Number</label>
              <input
                type="text"
                name="creditCardNumber"
                value={formData.creditCardNumber}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Card Expiration</label>
              <input
                type="text"
                name="cardExpiration"
                value={formData.cardExpiration}
                onChange={handleInputChange}
                placeholder="MM/YY"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Card Verification</label>
              <input
                type="text"
                name="cardVerification"
                value={formData.cardVerification}
                onChange={handleInputChange}
                placeholder="CVV"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent-orange"
              />
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="text-center">
          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary px-12 py-4 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Submitting Application...' : 'Submit Application'}
          </button>
          <p className="text-sm text-gray-600 mt-4">
            By submitting this application, you agree to our terms and conditions and privacy policy.
          </p>
        </div>
      </form>
    </div>
  )
}

