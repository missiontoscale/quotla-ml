import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Quotla - Professional Quote & Invoice Management',
  description: 'Create professional quotes and invoices with AI-powered content generation',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
