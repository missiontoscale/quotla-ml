# Deployment Guide

This guide covers deploying Quotla to production using Vercel.

## Pre-Deployment Checklist

Before deploying, ensure you have:

- [x] Completed local setup (see SETUP.md)
- [x] Tested all features locally
- [x] Set up Supabase project
- [x] Configured database schema
- [x] Created storage bucket
- [x] Obtained Anthropic API key
- [x] Code pushed to GitHub

## Deploying to Vercel

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/quotla.git
git push -u origin main
```

### Step 2: Connect to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign up or log in
3. Click "Add New Project"
4. Import your GitHub repository
5. Select the repository

### Step 3: Configure Environment Variables

In the Vercel dashboard, add the following environment variables:

```
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
ANTHROPIC_API_KEY=sk-ant-...
NEXT_PUBLIC_APP_URL=https://your-domain.vercel.app
```

**Important:** Copy these exactly from your `.env` file, except for `NEXT_PUBLIC_APP_URL` which should be your production URL.

### Step 4: Deploy

1. Click "Deploy"
2. Wait for the deployment to complete
3. Vercel will provide you with a URL

### Step 5: Update Supabase Configuration

1. Go to your Supabase project
2. Navigate to Authentication → Settings
3. Under "Site URL", add your Vercel URL:
   ```
   https://your-project.vercel.app
   ```
4. Under "Redirect URLs", add:
   ```
   https://your-project.vercel.app/**
   ```

### Step 6: Test Production Deployment

1. Visit your Vercel URL
2. Test all critical features:
   - Sign up/Login
   - Profile settings
   - Client creation
   - Quote creation with AI
   - Invoice creation
   - Blog viewing
   - Newsletter subscription

## Custom Domain (Optional)

### Adding a Custom Domain

1. In Vercel dashboard, go to your project
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions
5. Wait for DNS propagation

### Update Supabase for Custom Domain

After adding a custom domain:

1. Go to Supabase → Authentication → Settings
2. Update "Site URL" to your custom domain
3. Update "Redirect URLs" to include your custom domain

### Update Environment Variables

1. In Vercel, update `NEXT_PUBLIC_APP_URL`:
   ```
   NEXT_PUBLIC_APP_URL=https://yourdomain.com
   ```
2. Redeploy the application

## Production Configuration

### Enable Email Confirmation

For production, you should enable email confirmation:

1. Go to Supabase → Authentication → Settings
2. Under "Email Auth", enable "Confirm email"
3. Customize email templates:
   - Confirmation email
   - Password reset email
   - Magic link email

### Set Up Custom SMTP (Recommended)

By default, Supabase limits emails. For production:

1. Get an SMTP service (SendGrid, Mailgun, AWS SES)
2. In Supabase → Settings → Auth
3. Configure SMTP settings
4. Test email delivery

### Review Rate Limits

The default rate limit is 5 comments per hour. Adjust if needed in:
```typescript
// lib/utils/security.ts
export async function checkRateLimit(
  identifier: string,
  action: string,
  maxRequests: number = 10, // Adjust this
  windowMinutes: number = 60
)
```

## Monitoring & Maintenance

### Set Up Error Tracking

Consider adding error tracking:

1. **Sentry**: For error monitoring
   ```bash
   npm install @sentry/nextjs
   ```

2. **Vercel Analytics**: Enable in project settings

### Database Backups

Supabase automatically backs up your database. To ensure safety:

1. Go to Supabase → Database → Backups
2. Review backup schedule
3. Consider enabling Point-in-Time Recovery (PITR) for Pro plan

### Performance Monitoring

Monitor your application:

1. Use Vercel Analytics (free)
2. Check Supabase metrics (Database, Auth, Storage)
3. Monitor Anthropic API usage

## Security Best Practices

### For Production

1. **Enable HTTPS only**
   - Vercel does this automatically

2. **Review RLS Policies**
   - Audit all policies in Supabase
   - Test with different user roles

3. **Secure Storage Bucket**
   - Review storage policies
   - Ensure proper access controls

4. **Rotate Secrets Regularly**
   - API keys
   - Service role keys
   - Database passwords

5. **Set Up WAF** (Web Application Firewall)
   - Consider Cloudflare for additional protection

## Scaling Considerations

### Database

- Monitor query performance in Supabase
- Add indexes for slow queries
- Consider upgrading Supabase plan as you grow

### AI Usage

- Monitor Anthropic API usage
- Set up usage alerts
- Consider implementing caching for common descriptions

### Storage

- Monitor storage usage
- Implement image optimization
- Set up CDN for faster delivery

## Continuous Deployment

Vercel automatically redeploys when you push to your main branch:

```bash
git add .
git commit -m "Update feature"
git push
```

Vercel will:
1. Build the project
2. Run any checks
3. Deploy to production
4. Provide a preview URL

## Rollback

If something goes wrong:

1. Go to Vercel dashboard
2. Navigate to Deployments
3. Find the last working deployment
4. Click "Promote to Production"

## Environment-Specific Configuration

### Staging Environment

Create a staging environment:

1. Create a new branch: `staging`
2. In Vercel, create a new project linked to `staging` branch
3. Use separate Supabase project for staging
4. Test changes before merging to `main`

## Troubleshooting Production Issues

### Build Failures

Check Vercel build logs:
- Missing environment variables
- TypeScript errors
- Dependency issues

### Runtime Errors

Check Vercel function logs:
- API route errors
- Database connection issues
- Authentication problems

### Slow Performance

- Check Supabase query performance
- Review Vercel function execution times
- Optimize images and assets

## Cost Optimization

### Vercel

- Free tier: Includes hobby projects
- Pro tier: $20/month for commercial use

### Supabase

- Free tier: 500MB database, 1GB storage
- Pro tier: $25/month for more resources

### Anthropic

- Pay per use
- Monitor usage to control costs
- Implement caching where possible

## Compliance & Legal

### GDPR Compliance

If serving EU users:
- Add privacy policy
- Implement data export
- Add account deletion
- Cookie consent (if using analytics)

### Data Retention

Configure data retention policies:
- How long to keep audit logs
- When to delete inactive accounts
- Newsletter unsubscribe handling

## Post-Deployment Tasks

After successful deployment:

- [ ] Test all features in production
- [ ] Send test emails
- [ ] Create first admin user
- [ ] Add initial blog content
- [ ] Set up monitoring and alerts
- [ ] Configure backups
- [ ] Document any custom configurations
- [ ] Train users (if applicable)

## Support

For issues:
1. Check Vercel deployment logs
2. Review Supabase logs
3. Check browser console for errors
4. Refer to main README.md

---

**Congratulations!** Your Quotla application is now live in production.
