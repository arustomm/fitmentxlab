import { Mail, Phone, MapPin, Clock } from 'lucide-react'

export const metadata = {
  title: 'Contact Us - Fitment Labs',
  description: 'Get in touch with our team for product questions, support, or custom fitment advice.',
}

export default function ContactPage() {
  const contactInfo = [
    {
      icon: Mail,
      title: 'Email',
      details: 'info@fitmentlabs.com',
      description: 'Send us an email anytime',
    },
    {
      icon: Phone,
      title: 'Phone',
      details: '(555) 123-4567',
      description: 'Mon-Fri 9AM-6PM EST',
    },
    {
      icon: MapPin,
      title: 'Address',
      details: '123 Performance Ave\nAuto City, AC 12345',
      description: 'Visit our showroom',
    },
    {
      icon: Clock,
      title: 'Hours',
      details: 'Mon-Fri: 9AM-6PM\nSat: 10AM-4PM\nSun: Closed',
      description: 'Eastern Standard Time',
    },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      {/* Header */}
      <div className="text-center mb-16">
        <h1 className="text-4xl lg:text-5xl font-bold text-charcoal mb-6">
          Contact Us
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Have questions about our products or need fitment advice? 
          Our team of experts is here to help.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Contact Information */}
        <div>
          <h2 className="text-2xl font-bold text-charcoal mb-8">Get in Touch</h2>
          
          <div className="space-y-6 mb-8">
            {contactInfo.map((info, index) => (
              <div key={index} className="flex items-start space-x-4">
                <div className="flex-shrink-0 w-12 h-12 bg-forest-green text-white rounded-lg flex items-center justify-center">
                  <info.icon className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-semibold text-charcoal mb-1">{info.title}</h3>
                  <p className="text-gray-700 whitespace-pre-line mb-1">{info.details}</p>
                  <p className="text-sm text-gray-500">{info.description}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-gray-50 p-6 rounded-lg">
            <h3 className="font-semibold text-charcoal mb-3">Need Fitment Help?</h3>
            <p className="text-gray-600 mb-4">
              Not sure which wheels or tires will fit your vehicle? Our fitment specialists 
              can help you find the perfect setup for your build.
            </p>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Custom wheel and tire packages</li>
              <li>• Suspension compatibility advice</li>
              <li>• Performance recommendations</li>
              <li>• Installation guidance</li>
            </ul>
          </div>
        </div>

        {/* Contact Form */}
        <div>
          <h2 className="text-2xl font-bold text-charcoal mb-8">Send us a Message</h2>
          
          <form className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <label htmlFor="firstName" className="block text-sm font-medium text-charcoal mb-2">
                  First Name *
                </label>
                <input
                  type="text"
                  id="firstName"
                  name="firstName"
                  required
                  className="input-field"
                />
              </div>
              <div>
                <label htmlFor="lastName" className="block text-sm font-medium text-charcoal mb-2">
                  Last Name *
                </label>
                <input
                  type="text"
                  id="lastName"
                  name="lastName"
                  required
                  className="input-field"
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-charcoal mb-2">
                Email Address *
              </label>
              <input
                type="email"
                id="email"
                name="email"
                required
                className="input-field"
              />
            </div>

            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-charcoal mb-2">
                Phone Number
              </label>
              <input
                type="tel"
                id="phone"
                name="phone"
                className="input-field"
              />
            </div>

            <div>
              <label htmlFor="subject" className="block text-sm font-medium text-charcoal mb-2">
                Subject *
              </label>
              <select
                id="subject"
                name="subject"
                required
                className="input-field"
              >
                <option value="">Select a subject</option>
                <option value="product-question">Product Question</option>
                <option value="fitment-help">Fitment Help</option>
                <option value="order-support">Order Support</option>
                <option value="technical-support">Technical Support</option>
                <option value="general-inquiry">General Inquiry</option>
              </select>
            </div>

            <div>
              <label htmlFor="vehicle" className="block text-sm font-medium text-charcoal mb-2">
                Vehicle Information
              </label>
              <input
                type="text"
                id="vehicle"
                name="vehicle"
                placeholder="e.g., 2020 Honda Civic Type R"
                className="input-field"
              />
            </div>

            <div>
              <label htmlFor="message" className="block text-sm font-medium text-charcoal mb-2">
                Message *
              </label>
              <textarea
                id="message"
                name="message"
                rows={6}
                required
                className="input-field resize-none"
                placeholder="Tell us how we can help you..."
              ></textarea>
            </div>

            <button
              type="submit"
              className="btn-primary w-full"
            >
              Send Message
            </button>
          </form>

          <p className="text-sm text-gray-500 mt-4">
            * Required fields. We typically respond within 24 hours during business days.
          </p>
        </div>
      </div>
    </div>
  )
}

