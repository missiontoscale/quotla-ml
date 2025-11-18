export function validateEmail(email: string): boolean {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

export function validatePassword(password: string): {
  valid: boolean
  errors: string[]
} {
  const errors: string[] = []

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long')
  }
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter')
  }
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter')
  }
  if (!/[0-9]/.test(password)) {
    errors.push('Password must contain at least one number')
  }
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('Password must contain at least one special character')
  }

  return {
    valid: errors.length === 0,
    errors,
  }
}

export function sanitizeInput(input: string): string {
  return input
    .replace(/[<>]/g, '')
    .trim()
}

export function validateFileUpload(file: File): {
  valid: boolean
  error?: string
} {
  const MAX_SIZE = 2 * 1024 * 1024 // 2MB
  const ALLOWED_TYPES = ['image/png', 'image/jpeg', 'image/webp']

  if (file.size > MAX_SIZE) {
    return { valid: false, error: 'File size must be less than 2MB' }
  }

  if (!ALLOWED_TYPES.includes(file.type)) {
    return { valid: false, error: 'Only PNG, JPEG, and WebP images are allowed' }
  }

  return { valid: true }
}

export function validatePhoneNumber(phone: string): boolean {
  const re = /^[\d\s\-+()]+$/
  return re.test(phone)
}

export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount)
}

export function calculateTax(subtotal: number, taxRate: number): number {
  return Number((subtotal * (taxRate / 100)).toFixed(2))
}

export function calculateTotal(subtotal: number, taxAmount: number): number {
  return Number((subtotal + taxAmount).toFixed(2))
}
