import { NextRequest, NextResponse } from 'next/server'
import { convertCurrency, getExchangeRates } from '@/lib/currency'

export async function POST(request: NextRequest) {
  try {
    const { amount, from, to } = await request.json()

    if (!amount || !from || !to) {
      return NextResponse.json(
        { error: 'Missing required fields: amount, from, to' },
        { status: 400 }
      )
    }

    if (typeof amount !== 'number' || amount < 0) {
      return NextResponse.json(
        { error: 'Amount must be a positive number' },
        { status: 400 }
      )
    }

    const result = await convertCurrency(amount, from, to)

    return NextResponse.json(result)
  } catch (error) {
    console.error('Currency conversion error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to convert currency' },
      { status: 500 }
    )
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const base = searchParams.get('base') || 'USD'

    const rates = await getExchangeRates(base)

    return NextResponse.json({
      base,
      rates,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('Exchange rates fetch error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch exchange rates' },
      { status: 500 }
    )
  }
}
