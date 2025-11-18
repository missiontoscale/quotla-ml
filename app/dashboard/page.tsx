'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { supabase } from '@/lib/supabase/client'
import { Quote, Invoice } from '@/types'
import { useAuth } from '@/contexts/AuthContext'
import { format } from 'date-fns'
import { formatCurrency } from '@/lib/utils/validation'

export default function DashboardPage() {
  const { user, profile } = useAuth()
  const [quotes, setQuotes] = useState<Quote[]>([])
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [user])

  const loadData = async () => {
    if (!user) return

    const [quotesRes, invoicesRes] = await Promise.all([
      supabase
        .from('quotes')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })
        .limit(5),
      supabase
        .from('invoices')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })
        .limit(5),
    ])

    if (quotesRes.data) setQuotes(quotesRes.data)
    if (invoicesRes.data) setInvoices(invoicesRes.data)
    setLoading(false)
  }

  const stats = {
    totalQuotes: quotes.length,
    totalInvoices: invoices.length,
    pendingInvoices: invoices.filter((i) => i.status === 'sent').length,
    paidInvoices: invoices.filter((i) => i.status === 'paid').length,
  }

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back{profile?.company_name ? `, ${profile.company_name}` : ''}
        </h1>
        <p className="mt-2 text-gray-600">Here&apos;s what&apos;s happening with your business</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="text-sm text-gray-600">Total Quotes</div>
          <div className="text-3xl font-bold text-gray-900 mt-2">{stats.totalQuotes}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-600">Total Invoices</div>
          <div className="text-3xl font-bold text-gray-900 mt-2">{stats.totalInvoices}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-600">Pending Invoices</div>
          <div className="text-3xl font-bold text-yellow-600 mt-2">{stats.pendingInvoices}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-600">Paid Invoices</div>
          <div className="text-3xl font-bold text-green-600 mt-2">{stats.paidInvoices}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Recent Quotes</h2>
            <Link href="/quotes" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              View all
            </Link>
          </div>
          {quotes.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No quotes yet</p>
              <Link href="/quotes/new" className="btn btn-primary mt-4 inline-block">
                Create your first quote
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {quotes.map((quote) => (
                <Link
                  key={quote.id}
                  href={`/quotes/${quote.id}`}
                  className="block p-3 border rounded hover:bg-gray-50"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium">{quote.quote_number}</div>
                      {quote.title && <div className="text-sm text-gray-600">{quote.title}</div>}
                    </div>
                    <div className="text-right">
                      <div className="font-medium">{formatCurrency(quote.total, quote.currency)}</div>
                      <div className="text-xs text-gray-500">
                        {format(new Date(quote.created_at), 'MMM d, yyyy')}
                      </div>
                    </div>
                  </div>
                  <div className="mt-2">
                    <span
                      className={`inline-block px-2 py-1 text-xs rounded ${
                        quote.status === 'approved'
                          ? 'bg-green-100 text-green-800'
                          : quote.status === 'sent'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {quote.status}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Recent Invoices</h2>
            <Link href="/invoices" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              View all
            </Link>
          </div>
          {invoices.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No invoices yet</p>
              <Link href="/invoices/new" className="btn btn-primary mt-4 inline-block">
                Create your first invoice
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {invoices.map((invoice) => (
                <Link
                  key={invoice.id}
                  href={`/invoices/${invoice.id}`}
                  className="block p-3 border rounded hover:bg-gray-50"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium">{invoice.invoice_number}</div>
                      {invoice.title && <div className="text-sm text-gray-600">{invoice.title}</div>}
                    </div>
                    <div className="text-right">
                      <div className="font-medium">{formatCurrency(invoice.total, invoice.currency)}</div>
                      <div className="text-xs text-gray-500">
                        {format(new Date(invoice.created_at), 'MMM d, yyyy')}
                      </div>
                    </div>
                  </div>
                  <div className="mt-2">
                    <span
                      className={`inline-block px-2 py-1 text-xs rounded ${
                        invoice.status === 'paid'
                          ? 'bg-green-100 text-green-800'
                          : invoice.status === 'sent'
                          ? 'bg-blue-100 text-blue-800'
                          : invoice.status === 'overdue'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {invoice.status}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link href="/quotes/new" className="btn btn-primary text-center">
            Create New Quote
          </Link>
          <Link href="/invoices/new" className="btn btn-primary text-center">
            Create New Invoice
          </Link>
          <Link href="/clients/new" className="btn btn-secondary text-center">
            Add New Client
          </Link>
        </div>
      </div>
    </div>
  )
}
