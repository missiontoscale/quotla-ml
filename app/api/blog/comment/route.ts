import { NextRequest, NextResponse } from 'next/server'
import { supabaseAdmin } from '@/lib/supabase/server'
import { checkRateLimit, getClientIp, sanitizeHtml } from '@/lib/utils/security'
import { validateEmail } from '@/lib/utils/validation'

export async function POST(request: NextRequest) {
  try {
    const { post_id, author_name, author_email, content } = await request.json()

    if (!post_id || !author_name || !author_email || !content) {
      return NextResponse.json(
        { error: 'All fields are required' },
        { status: 400 }
      )
    }

    if (!validateEmail(author_email)) {
      return NextResponse.json(
        { error: 'Invalid email address' },
        { status: 400 }
      )
    }

    const ip = getClientIp(request)
    const rateLimit = await checkRateLimit(`comment:${ip}`, 'blog_comment', 5, 60)

    if (!rateLimit.allowed) {
      return NextResponse.json(
        { error: 'Too many comments. Please try again later.' },
        { status: 429 }
      )
    }

    const sanitizedContent = sanitizeHtml(content)

    const { error } = await supabaseAdmin.from('blog_comments').insert({
      post_id,
      author_name: author_name.trim(),
      author_email: author_email.trim().toLowerCase(),
      content: sanitizedContent,
      approved: false,
    })

    if (error) throw error

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Comment submission error:', error)
    return NextResponse.json(
      { error: 'Failed to submit comment' },
      { status: 500 }
    )
  }
}
