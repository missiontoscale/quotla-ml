# Keep-Alive Setup for Render Free Tier

Render's free tier spins down after 15 minutes of inactivity, causing 50+ second delays on the next request. This guide shows how to prevent that.

## ✅ Option 1: GitHub Actions (Automated - Recommended)

A GitHub Actions workflow has been set up to ping your service every 10 minutes.

### Setup Steps:

1. **Set Your Render URL** (Optional):
   - Go to your GitHub repository: https://github.com/missiontoscale/quotla-ml
   - Navigate to **Settings → Secrets and variables → Actions**
   - Click **New repository secret**
   - Name: `RENDER_SERVICE_URL`
   - Value: Your Render service URL (e.g., `https://quotla-ml.onrender.com`)
   - Click **Add secret**

2. **Enable GitHub Actions** (if not already enabled):
   - Go to **Actions** tab in your repository
   - If disabled, click **Enable GitHub Actions**

3. **Verify It's Working**:
   - Go to **Actions** tab
   - You should see the "Keep Render Service Alive" workflow
   - It runs automatically every 10 minutes
   - You can also click **Run workflow** to test it manually

### How It Works:
- Pings `/health` endpoint every 10 minutes
- Prevents Render from spinning down (15-minute timeout)
- Runs 24/7 automatically via GitHub Actions
- Completely free (GitHub Actions free tier includes 2,000 minutes/month)

---

## ✅ Option 2: UptimeRobot (External Monitoring - Also Free)

UptimeRobot is a free monitoring service that can also keep your service alive.

### Setup Steps:

1. **Sign Up**:
   - Go to https://uptimerobot.com
   - Create a free account

2. **Add Monitor**:
   - Click **+ Add New Monitor**
   - Monitor Type: **HTTP(s)**
   - Friendly Name: `Quotla ML API`
   - URL: `https://your-service.onrender.com/health`
   - Monitoring Interval: **5 minutes** (minimum on free tier)

3. **Configure Alerts** (Optional):
   - Add email alerts for downtime
   - Get notified if the service is actually down

### Benefits:
- Status page to share with others
- Downtime alerts
- Response time tracking
- More reliable than GitHub Actions (doesn't depend on your repo)

### Limitations:
- 5-minute interval (vs 1-minute with GitHub Actions)
- 50 monitors max on free tier

---

## ✅ Option 3: Cron-Job.org (Most Flexible)

### Setup Steps:

1. **Sign Up**:
   - Go to https://cron-job.org
   - Create a free account

2. **Create Cron Job**:
   - Click **Create Cronjob**
   - Title: `Keep Quotla ML Alive`
   - URL: `https://your-service.onrender.com/health`
   - Schedule: Every **10 minutes** (`*/10 * * * *`)
   - Save

### Benefits:
- 1-minute minimum interval (better than UptimeRobot's 5 min)
- Unlimited cron jobs
- Simple and reliable

---

## Comparison

| Solution | Interval | Setup Complexity | Cost |
|----------|----------|-----------------|------|
| **GitHub Actions** | 10 min | Easy (already set up!) | Free |
| **UptimeRobot** | 5 min | Easy | Free |
| **Cron-Job.org** | 10 min | Easy | Free |
| **Render Paid** | N/A (always on) | None | $7/month |

---

## 🎯 Recommendation

**Use GitHub Actions (already configured!)** because:
1. ✅ Already set up and ready to go
2. ✅ No external accounts needed
3. ✅ Runs every 10 minutes (optimal for 15-min timeout)
4. ✅ Completely free
5. ✅ Easy to monitor in GitHub Actions tab

**Optional**: Also set up UptimeRobot for:
- Status page monitoring
- Downtime alerts via email
- Additional redundancy

---

## Testing

To verify your keep-alive is working:

1. **Check GitHub Actions**:
   ```bash
   # Visit your repo
   https://github.com/missiontoscale/quotla-ml/actions

   # Look for "Keep Render Service Alive" workflow runs
   ```

2. **Check Render Logs**:
   - Go to your Render dashboard
   - Click on your service
   - View logs - you should see health check hits every 10 minutes

3. **Manual Test**:
   ```bash
   # Ping your health endpoint
   curl https://your-service.onrender.com/health

   # Should return: {"status":"healthy"}
   ```

---

## Troubleshooting

### GitHub Actions Not Running?

1. Check if Actions are enabled in your repository settings
2. Verify the workflow file is in `.github/workflows/keep-alive.yml`
3. Check the Actions tab for any error messages

### Service Still Spinning Down?

1. Verify your Render URL is correct in GitHub secrets
2. Check if the cron schedule is correct (`*/10 * * * *`)
3. Look at Render logs to confirm requests are coming in

### Want to Change Ping Frequency?

Edit `.github/workflows/keep-alive.yml`:
```yaml
# Every 5 minutes instead of 10
- cron: '*/5 * * * *'

# Every 14 minutes (just before 15-min timeout)
- cron: '*/14 * * * *'
```

---

## Cost Optimization

All three solutions are **100% free** and will keep your Render service from spinning down without any monthly costs!

If you need guaranteed uptime and faster response times, consider:
- **Render Starter Plan**: $7/month (always-on, no cold starts)
- Still cheaper than most hosting providers
