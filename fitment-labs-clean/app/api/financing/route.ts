import { NextRequest, NextResponse } from 'next/server'
import nodemailer from 'nodemailer'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.json()

    // Format the application data for email
    const applicationText = `
FINANCING APPLICATION SUBMISSION
================================

PERSONAL INFORMATION
-------------------
Name: ${formData.firstName} ${formData.lastName}
Address: ${formData.address}
City: ${formData.city}
State: ${formData.state}
ZIP: ${formData.zip}
Years at Address: ${formData.yearsAtAddress}
Rent/Own: ${formData.rentOrOwn}
Phone: ${formData.phone}
Email: ${formData.email}
SSN: ${formData.ssn}
Birthdate: ${formData.birthdate}
Driver's License: ${formData.driverLicenseNumber}
License State: ${formData.driverLicenseState}
License Expiration: ${formData.driverLicenseExpiration}

INCOME INFORMATION
-----------------
Employment Status: ${formData.employmentStatus}
Years Employed: ${formData.yearsEmployed}
Employer Name: ${formData.employerName}
Employer Phone: ${formData.employerPhone}
Monthly Income: ${formData.monthlyIncome}
Pay Frequency: ${formData.payFrequency}

REFERENCE INFORMATION
--------------------
Reference 1: ${formData.reference1Name} - ${formData.reference1Phone}
Reference 2: ${formData.reference2Name} - ${formData.reference2Phone}

PAYMENT INFORMATION
------------------
Routing Number: ${formData.routingNumber}
Account Number: ${formData.accountNumber}
Years Account Open: ${formData.yearsAccountOpen}
Credit Card: ${formData.creditCardNumber}
Card Expiration: ${formData.cardExpiration}
Card Verification: ${formData.cardVerification}

Submitted: ${new Date().toISOString()}
    `.trim()

    // Create HTML version
    const applicationHtml = applicationText.replace(/\n/g, '<br>').replace(/=/g, '').replace(/-/g, '')

    try {
      // For development/testing, log the application data
      console.log('=== FINANCING APPLICATION RECEIVED ===')
      console.log('To: fitmentxlab@gmail.com')
      console.log('Subject: New Financing Application -', formData.firstName, formData.lastName)
      console.log('Application Data:')
      console.log(applicationText)
      console.log('=== END APPLICATION ===')

      // Create transporter using Gmail SMTP (you can change this to any email service)
      const transporter = nodemailer.createTransport({
        service: 'gmail',
        auth: {
          user: process.env.EMAIL_USER || 'fitmentxlab@gmail.com',
          pass: process.env.EMAIL_PASS || 'your-app-password'
        }
      })

      // Send email
      await transporter.sendMail({
        from: process.env.EMAIL_USER || 'fitmentxlab@gmail.com',
        to: 'fitmentxlab@gmail.com',
        subject: `New Financing Application - ${formData.firstName} ${formData.lastName}`,
        text: applicationText,
        html: `<pre style="font-family: monospace; white-space: pre-wrap;">${applicationHtml}</pre>`
      })

      console.log('Email sent successfully to fitmentxlab@gmail.com')
    } catch (emailError) {
      console.error('Email sending failed, but application data has been logged:', emailError)
      console.log('IMPORTANT: Financing application data logged above for manual processing')
      
      // Even if email fails, we'll still return success to avoid user confusion
      // The application data is logged to console for manual processing
    }

    return NextResponse.json({ 
      success: true, 
      message: 'Application submitted successfully. We will review your application and contact you within 24 hours.' 
    })

  } catch (error) {
    console.error('Error processing financing application:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to process application. Please try again or contact us directly.' 
      },
      { status: 500 }
    )
  }
}

