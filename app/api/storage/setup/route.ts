import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

export async function POST() {
  try {
    // Use service role key for admin operations
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
    const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY

    if (!supabaseUrl || !supabaseServiceKey) {
      return NextResponse.json(
        { error: 'Server configuration error' },
        { status: 500 }
      )
    }

    const supabaseAdmin = createClient(supabaseUrl, supabaseServiceKey, {
      auth: { persistSession: false },
    })

    // Check if bucket exists
    const { data: buckets, error: listError } = await supabaseAdmin.storage.listBuckets()

    if (listError) {
      throw listError
    }

    const bucketExists = buckets?.some((bucket) => bucket.name === 'business-assets')

    if (!bucketExists) {
      // Create the bucket
      const { error: createError } = await supabaseAdmin.storage.createBucket('business-assets', {
        public: true,
        fileSizeLimit: 2097152, // 2MB
        allowedMimeTypes: ['image/png', 'image/jpeg', 'image/webp'],
      })

      if (createError) {
        throw createError
      }

      // Create storage policies for the bucket
      // Note: These need to be created via SQL in the Supabase dashboard
      // The policies allow authenticated users to upload and public to view

      return NextResponse.json({
        success: true,
        message: 'Storage bucket created successfully. Please run supabase-storage-policies.sql in your Supabase SQL Editor to enable uploads.',
        created: true,
        needsPolicies: true,
      })
    }

    return NextResponse.json({
      success: true,
      message: 'Storage bucket already exists',
      created: false,
    })
  } catch (error) {
    console.error('Storage setup error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to setup storage' },
      { status: 500 }
    )
  }
}

export async function GET() {
  try {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
    const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY

    if (!supabaseUrl || !supabaseServiceKey) {
      return NextResponse.json(
        { error: 'Server configuration error' },
        { status: 500 }
      )
    }

    const supabaseAdmin = createClient(supabaseUrl, supabaseServiceKey, {
      auth: { persistSession: false },
    })

    const { data: buckets, error: listError } = await supabaseAdmin.storage.listBuckets()

    if (listError) {
      throw listError
    }

    const bucket = buckets?.find((b) => b.name === 'business-assets')

    return NextResponse.json({
      exists: !!bucket,
      bucket: bucket || null,
    })
  } catch (error) {
    console.error('Storage check error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to check storage' },
      { status: 500 }
    )
  }
}
