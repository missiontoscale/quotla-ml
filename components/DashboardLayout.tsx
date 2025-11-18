'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const { signOut, profile } = useAuth()

  const navigation = [
    { name: 'Dashboard', href: '/dashboard' },
    { name: 'Quotes', href: '/quotes' },
    { name: 'Invoices', href: '/invoices' },
    { name: 'Clients', href: '/clients' },
    { name: 'Settings', href: '/settings' },
  ]

  if (profile?.is_admin) {
    navigation.push({ name: 'Admin', href: '/admin' })
  }

  const handleSignOut = async () => {
    try {
      await signOut()
    } catch (error) {
      console.error('Sign out error:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link href="/dashboard" className="flex items-center text-2xl font-bold text-primary-600">
                Quotla
              </Link>
              <div className="ml-10 flex items-center space-x-4">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`px-3 py-2 rounded text-sm font-medium ${
                      pathname === item.href
                        ? 'bg-primary-50 text-primary-600'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {item.name}
                  </Link>
                ))}
              </div>
            </div>
            <div className="flex items-center">
              <span className="text-sm text-gray-600 mr-4">{profile?.email}</span>
              <button onClick={handleSignOut} className="btn btn-secondary text-sm">
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">{children}</main>

      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-6">
              <span className="text-sm font-medium text-gray-900">Quotla</span>
              <Link href="/blog" className="text-sm text-gray-600 hover:text-primary-600">
                Blog
              </Link>
              <Link href="/" className="text-sm text-gray-600 hover:text-primary-600">
                Home
              </Link>
            </div>
            <div className="text-sm text-gray-500">
              &copy; {new Date().getFullYear()} Quotla. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
