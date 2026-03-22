# Vercel Git Integration Fix

## Current Problem
- Vercel is building from the **wrong Git repository**
- Latest code (commit `dc1b753`) is in `Mo-101/MoStar-Grid` fork
- Vercel is pulling from a different source (likely upstream or old fork)
- Result: `/api/moments` returns OLD code instead of NEW code with Neo4j

## Solution: Reconnect Vercel to Correct Repository

### Step 1: Open Vercel Git Settings
Go to: **https://vercel.com/mo-101s-projects/mo-star-grid/settings/git**

### Step 2: Check Current Connected Repository
Look for the section labeled "Connected Repository" or "Git Integration"
- **If it shows:** `Mo-101/MoStar-Grid` → Skip to Step 4
- **If it shows:** Anything else (e.g., `Mostar-Industries/MoStar-Grid`) → Continue to Step 3

### Step 3: Disconnect and Reconnect
1. Click the **"Disconnect"** button next to the current repository
2. Click **"Connect Git Repository"**
3. In the modal that appears:
   - Search for: `MoStar-Grid`
   - Select: `Mo-101/MoStar-Grid` (your fork)
   - Click **"Connect"**
4. Set **Production Branch** to: `main`
5. Click **"Save"**

### Step 4: Verify Configuration
After reconnecting, you should see:
- **Connected Repository:** `Mo-101/MoStar-Grid`
- **Production Branch:** `main`
- **Root Directory:** (leave blank or `/frontend`)

### Step 5: Trigger Fresh Deployment
Vercel will automatically start building. Wait 3-5 minutes for the build to complete.

You can monitor progress at: **https://vercel.com/mo-101s-projects/mo-star-grid/deployments**

### Step 6: Verify the Fix
Once the deployment shows "Ready", run this in PowerShell:

```powershell
.\verify_and_fix.ps1
```

Expected output:
```
✅ Response contains NEW code fields (provenance)
✅ Connected to Neo4j Aura!
```

## If Build Fails
1. Go to the failed deployment in Vercel
2. Click **"View Build Logs"**
3. Look for error messages
4. Common issues:
   - Missing `package.json` at root → Already fixed in commit `a76f66c`
   - Missing env vars → Check Settings → Environment Variables
   - Node version mismatch → Check Settings → Node.js Version

## After Fix is Complete
Once `/api/moments` returns NEW code:
1. Test Neo4j connection
2. Attach `mostarindustries.com` custom domain
3. Grid will be live and operational
