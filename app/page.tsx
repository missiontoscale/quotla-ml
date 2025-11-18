'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase/client'

export default function HomePage() {
  const router = useRouter()
  const [showDemo, setShowDemo] = useState(false)
  const [demoPrompt, setDemoPrompt] = useState('')
  const [demoResult, setDemoResult] = useState('')
  const [demoLoading, setDemoLoading] = useState(false)
  const [demoError, setDemoError] = useState('')
  const [checkingAuth, setCheckingAuth] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      if (session) {
        router.push('/dashboard')
      } else {
        setCheckingAuth(false)
      }
    }
    checkAuth()
  }, [router])

  const handleTryAI = async () => {
    if (!demoPrompt.trim()) {
      setDemoError('Please describe a service or product')
      return
    }

    setDemoLoading(true)
    setDemoError('')
    setDemoResult('')

    try {
      const response = await fetch('/api/ai/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: demoPrompt }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate')
      }

      setDemoResult(data.description)
    } catch (err) {
      setDemoError(err instanceof Error ? err.message : 'Failed to generate description')
    } finally {
      setDemoLoading(false)
    }
  }

  // Show loading while checking authentication
  if (checkingAuth) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-primary-50 to-white flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-primary-50 to-white">
      <nav className="border-b bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary-600">Quotla</h1>
            </div>
            <div className="flex gap-4">
              <Link href="/login" className="btn btn-secondary">
                Sign In
              </Link>
              <Link href="/signup" className="btn btn-primary">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            Generate a Professional Quote
            <br />
            <span className="text-primary-600">In Under 2 Minutes</span>
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Supercharge your workflow. Ease negotiations. Close deals faster with AI-powered quotes that impress clients and win business.
          </p>
          <div className="flex justify-center gap-4 mb-8">
            <button
              onClick={() => setShowDemo(true)}
              className="btn btn-primary text-lg px-8 py-3"
            >
              Try AI Generator Free
            </button>
            <Link href="/signup" className="btn btn-secondary text-lg px-8 py-3">
              Create Account
            </Link>
          </div>
          <p className="text-sm text-gray-500">No credit card required. Experience the power of AI instantly.</p>
        </div>

        <div className="mt-24 grid md:grid-cols-3 gap-8">
          <div className="card text-center">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-bold mb-2">Supercharge Your Workflow</h3>
            <p className="text-gray-600">
              Generate professional service descriptions in seconds. What used to take 30 minutes now takes 30 seconds.
            </p>
          </div>
          <div className="card text-center">
            <div className="text-4xl mb-4">🤝</div>
            <h3 className="text-xl font-bold mb-2">Ease Negotiations</h3>
            <p className="text-gray-600">
              Clear, professional quotes build trust. AI helps you articulate value so clients say yes faster.
            </p>
          </div>
          <div className="card text-center">
            <div className="text-4xl mb-4">⏱️</div>
            <h3 className="text-xl font-bold mb-2">2-Minute Quotes</h3>
            <p className="text-gray-600">
              From client request to professional quote in under 2 minutes. Stop losing deals to slow responses.
            </p>
          </div>
        </div>

        <div className="mt-24 bg-white rounded-lg border p-8">
          <div className="text-center mb-8">
            <h3 className="text-3xl font-bold mb-4">See It In Action</h3>
            <p className="text-gray-600">Try our AI quote generator right now. No signup needed.</p>
          </div>

          <div className="max-w-2xl mx-auto">
            <div className="mb-4">
              <label className="label">Describe your service:</label>
              <textarea
                className="input resize-none"
                rows={3}
                placeholder="e.g., Web design for a restaurant with online menu, reservation system, and mobile responsive layout"
                value={demoPrompt}
                onChange={(e) => setDemoPrompt(e.target.value)}
              />
            </div>
            <button
              onClick={handleTryAI}
              disabled={demoLoading}
              className="btn btn-primary w-full mb-4"
            >
              {demoLoading ? 'Generating...' : 'Generate Professional Description'}
            </button>

            {demoError && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mb-4">
                {demoError}
              </div>
            )}

            {demoResult && (
              <div className="bg-green-50 border border-green-200 p-4 rounded">
                <div className="font-bold text-green-800 mb-2">Generated Description:</div>
                <p className="text-green-900">{demoResult}</p>
                <div className="mt-4 text-center">
                  <Link href="/signup" className="btn btn-primary">
                    Create Full Quote with This
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="mt-24">
          <h3 className="text-3xl font-bold text-center mb-12">Why Professionals Choose Quotla</h3>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="card">
              <h4 className="text-xl font-bold mb-4">Stop Losing Deals to Slow Quotes</h4>
              <p className="text-gray-600 mb-4">
                Every hour you delay sending a quote, your chance of closing drops by 50%. Quotla lets you respond while the client is still excited.
              </p>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start">
                  <span className="text-primary-600 mr-2">✓</span>
                  <span>AI generates descriptions instantly</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-600 mr-2">✓</span>
                  <span>Pre-saved clients and templates</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-600 mr-2">✓</span>
                  <span>Automatic tax calculations</span>
                </li>
              </ul>
            </div>
            <div className="card">
              <h4 className="text-xl font-bold mb-4">Professional Documents That Win Trust</h4>
              <p className="text-gray-600 mb-4">
                Clients judge your professionalism by your documents. Quotla ensures every quote reflects your expertise.
              </p>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start">
                  <span className="text-primary-600 mr-2">✓</span>
                  <span>Custom branding with your logo</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-600 mr-2">✓</span>
                  <span>20+ currencies including African markets</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-600 mr-2">✓</span>
                  <span>Export to PDF, Word, or JSON</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-24 text-center">
          <h3 className="text-3xl font-bold mb-6">Ready to Close More Deals?</h3>
          <p className="text-xl text-gray-600 mb-8">
            Join thousands of professionals who create winning quotes in under 2 minutes.
          </p>
          <button
            onClick={() => setShowDemo(true)}
            className="btn btn-primary text-lg px-12 py-4"
          >
            Try AI Generator Now - It&apos;s Free
          </button>
        </div>
      </main>

      <footer className="border-t bg-gray-50 mt-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h4 className="font-bold text-lg mb-4">Quotla</h4>
              <p className="text-gray-600 text-sm">
                Supercharging workflows for consultants, freelancers, and service providers worldwide.
              </p>
            </div>
            <div>
              <h4 className="font-bold text-lg mb-4">Quick Links</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/blog" className="text-gray-600 hover:text-primary-600">Blog</Link></li>
                <li><Link href="/login" className="text-gray-600 hover:text-primary-600">Sign In</Link></li>
                <li><Link href="/signup" className="text-gray-600 hover:text-primary-600">Sign Up</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-lg mb-4">Newsletter</h4>
              <p className="text-gray-600 text-sm mb-4">
                Get tips on winning more clients
              </p>
              <Link href="/newsletter" className="btn btn-primary text-sm">
                Subscribe
              </Link>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t text-center text-gray-600 text-sm">
            <p>&copy; {new Date().getFullYear()} Quotla. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {showDemo && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-2xl font-bold">Try Quotla AI Generator</h3>
              <button
                onClick={() => {
                  setShowDemo(false)
                  setDemoResult('')
                  setDemoError('')
                }}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            <p className="text-gray-600 mb-6">
              Describe any service or product, and watch AI create a professional quote description instantly.
            </p>

            <div className="mb-4">
              <label className="label">What are you quoting?</label>
              <textarea
                className="input resize-none"
                rows={4}
                placeholder="Examples:
• Website redesign for e-commerce store with payment integration
• 3-month social media management for dental clinic
• Home renovation including kitchen and 2 bathrooms
• Consulting services for startup business strategy"
                value={demoPrompt}
                onChange={(e) => setDemoPrompt(e.target.value)}
              />
            </div>

            {demoError && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mb-4">
                {demoError}
              </div>
            )}

            <button
              onClick={handleTryAI}
              disabled={demoLoading}
              className="btn btn-primary w-full mb-4"
            >
              {demoLoading ? 'AI is generating...' : 'Generate Professional Description'}
            </button>

            {demoResult && (
              <div className="bg-green-50 border border-green-200 p-4 rounded mb-4">
                <div className="font-bold text-green-800 mb-2">Your Professional Description:</div>
                <p className="text-green-900 leading-relaxed">{demoResult}</p>
              </div>
            )}

            <div className="border-t pt-4">
              <p className="text-sm text-gray-600 mb-4">
                This is just the beginning. With a free account, you can:
              </p>
              <ul className="text-sm text-gray-700 space-y-2 mb-4">
                <li>• Create complete quotes with multiple line items</li>
                <li>• Add your logo and business details</li>
                <li>• Track quote status and client responses</li>
                <li>• Export to PDF and send to clients</li>
                <li>• Convert quotes to invoices instantly</li>
              </ul>
              <Link href="/signup" className="btn btn-primary w-full">
                Create Free Account
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
