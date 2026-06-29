import Image from 'next/image'
import { Zap, Shield, Users, Award } from 'lucide-react'

export const metadata = {
  title: 'About Us - Fitment Labs',
  description: 'Learn about Fitment Labs and our commitment to providing premium automotive performance parts.',
}

export default function AboutPage() {
  const values = [
    {
      icon: Zap,
      title: 'Performance First',
      description: 'Every product we carry is tested and proven to deliver exceptional performance on the street and track.',
    },
    {
      icon: Shield,
      title: 'Quality Assurance',
      description: 'We partner only with trusted manufacturers who share our commitment to quality and reliability.',
    },
    {
      icon: Users,
      title: 'Expert Support',
      description: 'Our team of automotive enthusiasts provides knowledgeable support to help you make the right choice.',
    },
    {
      icon: Award,
      title: 'Proven Results',
      description: 'Thousands of satisfied customers trust us to deliver the parts that make their builds stand out.',
    },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-4xl lg:text-5xl font-bold text-charcoal mb-6">
          About Fitment Labs
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
          We're passionate automotive enthusiasts dedicated to providing the highest quality 
          wheels, tires, and suspension components for performance-driven builds.
        </p>
      </div>

      {/* Story Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-20">
        <div>
          <h2 className="text-3xl font-bold text-charcoal mb-6">Our Story</h2>
          <div className="space-y-4 text-gray-700 leading-relaxed">
            <p>
              Founded by a team of automotive enthusiasts, Fitment Labs was born from a simple 
              belief: every vehicle deserves components that match its owner's passion for performance.
            </p>
            <p>
              We started in a small garage, testing and perfecting fitments for our own builds. 
              Word spread quickly about our attention to detail and commitment to quality, and 
              soon we were helping fellow enthusiasts across the country achieve their perfect setup.
            </p>
            <p>
              Today, we're proud to be a trusted source for premium wheels, high-performance tires, 
              and precision-engineered suspension components. Every product in our catalog has been 
              carefully selected and tested to meet our exacting standards.
            </p>
          </div>
        </div>
        <div>
          <Image
            src="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600"
            alt="Fitment Labs Workshop"
            width={600}
            height={400}
            className="rounded-lg shadow-lg"
          />
        </div>
      </div>

      {/* Values Section */}
      <div className="mb-20">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-charcoal mb-4">Our Values</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            These core principles guide everything we do, from product selection to customer service.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {values.map((value, index) => (
            <div key={index} className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-forest-green text-white rounded-full mb-4">
                <value.icon className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-semibold text-charcoal mb-3">
                {value.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {value.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Team Section */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-charcoal mb-6">Meet the Team</h2>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
          Our team combines decades of automotive experience with a genuine passion 
          for helping customers achieve their perfect build.
        </p>
        <div className="bg-forest-green text-white p-8 rounded-lg">
          <p className="text-lg">
            "At Fitment Labs, we don't just sell parts – we help bring automotive dreams to life. 
            Every customer's build is as important to us as our own."
          </p>
          <p className="mt-4 font-semibold">- The Fitment Labs Team</p>
        </div>
      </div>
    </div>
  )
}

