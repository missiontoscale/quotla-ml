import { supabaseAdmin } from '@/lib/supabase/server'

export interface RateLimitResult {
  allowed: boolean
  remaining: number
  resetAt: Date
}

export async function checkRateLimit(
  identifier: string,
  action: string,
  maxRequests: number = 5,
  windowMinutes: number = 60
): Promise<RateLimitResult> {
  const now = new Date()
  const windowStart = new Date(now.getTime() - windowMinutes * 60 * 1000)

  const { data: existing } = await supabaseAdmin
    .from('rate_limits')
    .select('*')
    .eq('identifier', identifier)
    .eq('action', action)
    .gte('window_start', windowStart.toISOString())
    .order('window_start', { ascending: false })
    .limit(1)
    .single()

  if (existing) {
    if (existing.count >= maxRequests) {
      const resetAt = new Date(
        new Date(existing.window_start).getTime() + windowMinutes * 60 * 1000
      )
      return {
        allowed: false,
        remaining: 0,
        resetAt,
      }
    }

    await supabaseAdmin
      .from('rate_limits')
      .update({ count: existing.count + 1 })
      .eq('id', existing.id)

    const resetAt = new Date(
      new Date(existing.window_start).getTime() + windowMinutes * 60 * 1000
    )

    return {
      allowed: true,
      remaining: maxRequests - (existing.count + 1),
      resetAt,
    }
  }

  await supabaseAdmin.from('rate_limits').insert({
    identifier,
    action,
    count: 1,
    window_start: now.toISOString(),
  })

  return {
    allowed: true,
    remaining: maxRequests - 1,
    resetAt: new Date(now.getTime() + windowMinutes * 60 * 1000),
  }
}

export async function logAudit(
  userId: string | null,
  action: string,
  resourceType?: string,
  resourceId?: string,
  details?: Record<string, unknown>,
  ipAddress?: string
): Promise<void> {
  await supabaseAdmin.from('audit_logs').insert({
    user_id: userId,
    action,
    resource_type: resourceType,
    resource_id: resourceId,
    details: details as never,
    ip_address: ipAddress,
  })
}

export function getClientIp(request: Request): string {
  const forwarded = request.headers.get('x-forwarded-for')
  const ip = forwarded ? forwarded.split(',')[0] : 'unknown'
  return ip
}

export function sanitizeHtml(html: string): string {
  return html
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
    .replace(/on\w+\s*=\s*["'][^"']*["']/gi, '')
    .replace(/javascript:/gi, '')
}
