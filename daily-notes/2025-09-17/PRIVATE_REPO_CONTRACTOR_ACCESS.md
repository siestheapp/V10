# Giving Contractor Access to Private Repository

Now that your repo is private (good move!), here's how to give the contractor LIMITED access:

## Option 1: Read-Only Access to Specific Branch (RECOMMENDED)

1. **Go to GitHub Settings**:
   - https://github.com/siestheapp/V10/settings/access
   
2. **Add Outside Collaborator**:
   - Click "Add people"
   - Enter contractor's GitHub username
   - Select "Read" permission
   - They can clone but not push

3. **Contractor Workflow**:
   - They fork the repo (creates their own copy)
   - Make changes in their fork
   - Submit pull requests back to you
   - You review and merge only what you approve

## Option 2: Use GitHub Deploy Keys (More Restricted)

1. **Create a deploy key** (read-only):
   ```bash
   ssh-keygen -t ed25519 -f contractor_key -C "contractor@v10"
   # Don't set a passphrase
   ```

2. **Add to GitHub**:
   - Settings → Deploy keys
   - Add the public key (contractor_key.pub)
   - Don't check "Allow write access"

3. **Give contractor** the private key to clone

## Option 3: Create a Separate Public Fork (Most Secure)

1. **You create a new PUBLIC repo** with only contractor branch:
   ```bash
   # Create new repo "V10-contractor" on GitHub (public)
   git clone https://github.com/siestheapp/V10.git V10-contractor
   cd V10-contractor
   git checkout contractor-performance-simple
   git remote set-url origin https://github.com/siestheapp/V10-contractor.git
   git push origin contractor-performance-simple:main
   ```

2. **Contractor works on public fork**
3. **You manually merge back changes**

## For Render Deployment:

### If Render Lost Access:

1. **Go to**: https://dashboard.render.com
2. **Click on your V10 service**
3. **Settings → Build & Deploy**
4. **Click "Configure GitHub App"**
5. **Grant access to V10 repository**
6. **Manual Deploy** to test it works

### Alternative: Use Deploy Hook

1. **In Render Dashboard**:
   - Settings → Deploy Hook
   - Copy the deploy hook URL

2. **Trigger deploys manually**:
   ```bash
   curl -X POST [deploy-hook-url]
   ```

## Contractor Instructions Update:

Since repo is now private, tell the contractor:

```
I'll add you as a collaborator with read access.
What's your GitHub username?

Once added:
1. Fork the repository
2. Work on branch: contractor-performance-simple
3. Submit PRs for review
```

## Security Checklist:

- ✅ Repository is private
- ✅ Scrapers removed from contractor branch
- ✅ Only test data in database
- ⏳ Add contractor with READ only access
- ⏳ Monitor their activity daily
- ⏳ Revoke access after project

---

**Good catch on the public repo!** This could have been a serious issue. Now your scrapers and proprietary code are protected.
