'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { supabase } from '@/lib/supabase/client'
import { BlogPost } from '@/types'
import { format } from 'date-fns'

export default function BlogPage() {
  const [posts, setPosts] = useState<BlogPost[]>([])
  const [loading, setLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    checkAuth()
    loadPosts()
  }, [])

  const checkAuth = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    setIsAuthenticated(!!session)
  }

  const loadPosts = async () => {
    const { data, error } = await supabase
      .from('blog_posts')
      .select('*')
      .eq('published', true)
      .order('published_at', { ascending: false })

    if (!error && data) {
      setPosts(data)
    }
    setLoading(false)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div>Loading...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="border-b bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="text-2xl font-bold text-primary-600">
              Quotla
            </Link>
            <div className="flex gap-4">
              {isAuthenticated ? (
                <Link href="/dashboard" className="btn btn-primary">
                  Dashboard
                </Link>
              ) : (
                <>
                  <Link href="/login" className="btn btn-secondary">
                    Sign In
                  </Link>
                  <Link href="/signup" className="btn btn-primary">
                    Get Started
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Blog</h1>

        {posts.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-500">No blog posts yet. Check back soon!</p>
          </div>
        ) : (
          <div className="space-y-8">
            {posts.map((post) => (
              <div key={post.id} className="card hover:shadow-md transition-shadow">
                <Link href={`/blog/${post.slug}`}>
                  <h2 className="text-2xl font-bold text-gray-900 hover:text-primary-600 mb-2">
                    {post.title}
                  </h2>
                </Link>
                {post.excerpt && (
                  <p className="text-gray-600 mb-4">{post.excerpt}</p>
                )}
                <div className="text-sm text-gray-500">
                  {post.published_at && format(new Date(post.published_at), 'MMMM d, yyyy')}
                </div>
                <Link
                  href={`/blog/${post.slug}`}
                  className="inline-block mt-4 text-primary-600 hover:text-primary-700 font-medium"
                >
                  Read more →
                </Link>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
