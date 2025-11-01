# 🚀 Analytics Quick Start - 5 Minutes to Launch

## ⚡ Step 1: Get TikTok Pixel ID (2 min)

1. Go to https://ads.tiktok.com/
2. Click **Assets** → **Events** → **Manage**
3. Copy your **Pixel ID** (e.g., `C9N7BK1234567890ABCD`)

## ⚡ Step 2: Update Landing Page (1 min)

Open `freestyle-october/index.html` and edit **line 28**:

```javascript
// BEFORE:
ttq.load('YOUR_TIKTOK_PIXEL_ID');

// AFTER (replace with your actual ID):
ttq.load('C9N7BK1234567890ABCD');
```

## ⚡ Step 3: Test It (2 min)

1. Install [TikTok Pixel Helper Chrome Extension](https://chrome.google.com/webstore/detail/tiktok-pixel-helper/)
2. Visit your landing page
3. Click extension icon → should see your Pixel ID ✅
4. Submit the form → should see "SubmitForm" event ✅
5. Complete diagnostic → should see "CompleteRegistration" event ✅

## 🎯 Your Primary Conversion Event

**`CompleteRegistration`** = User completed diagnostic question

Use this as your optimization event in TikTok Ads Manager.

---

## 📊 What's Being Tracked

### Critical Events
| Event | What It Means |
|-------|---------------|
| `PageView` | Someone visited your page |
| `SubmitForm` | Someone entered their email |
| `CompleteRegistration` | **🎯 Someone completed the full funnel** |

### Engagement Events
| Event | What It Means |
|-------|---------------|
| `ViewContent` | Watched your video or saw diagnostic |
| `ClickButton` | Clicked "Get early access" button |
| `video_progress` | Watched 25%/50%/75% of video |
| `form_start` | Started typing in email field |
| `form_abandon` | Left without submitting |

---

## 🔥 TikTok Ad Setup

### Campaign Settings
- **Objective**: Website Conversions
- **Optimization Event**: CompleteRegistration
- **Landing Page URL**: 
  ```
  https://yourdomain.com/?utm_source=tiktok&utm_medium=cpc&utm_campaign=waitlist_q4
  ```

### Creative Strategy
- Video ads perform best on TikTok
- Use UGC-style content (authentic, not polished)
- First 3 seconds = hook (e.g., "I'm done ordering the wrong size online...")
- Include CTA: "Link in bio to join waitlist"

---

## 📈 Key Metrics to Watch

### First 48 Hours
- **Pixel Status**: Should show "Active" in Events Manager
- **Event Count**: Should see PageView, ClickButton, SubmitForm events
- **Conversion Rate**: Aim for 2-5% (SubmitForm / PageView)

### First Week
- **Cost Per CompleteRegistration**: Track in TikTok Ads Manager
- **Form Abandonment Rate**: Check Formspree for `form_abandon` events
- **Video Completion Rate**: Check for `video_complete` events
- **Top Struggle Brands**: See what users select in diagnostic

### Ongoing
- **CPA (Cost Per Acquisition)**: Keep under $X (set your target)
- **ROAS (Return on Ad Spend)**: Calculate based on LTV
- **Audience Size**: Monitor retargeting pool growth

---

## 🚨 Common Issues

### Pixel Not Showing Up
- ✅ Check line 28 has correct Pixel ID
- ✅ Hard refresh page (Cmd+Shift+R / Ctrl+Shift+R)
- ✅ Disable ad blockers
- ✅ Check browser console for errors

### Events Not in TikTok
- ✅ Wait 15-30 minutes for delay
- ✅ Check "Test Events" tab instead of "Event Activity"
- ✅ Try incognito/private browsing

### Low Conversion Rate
- ✅ Check form abandonment data (Formspree)
- ✅ Test mobile experience (80% of TikTok is mobile)
- ✅ Simplify form (you only have email - good!)
- ✅ Add urgency/scarcity to CTA

---

## 📞 Quick Links

- **TikTok Ads Manager**: https://ads.tiktok.com/
- **TikTok Events Manager**: https://ads.tiktok.com/ → Assets → Events
- **Formspree Dashboard**: https://formspree.io/forms
- **Pixel Helper Extension**: [Chrome Web Store](https://chrome.google.com/webstore/detail/tiktok-pixel-helper/)
- **Full Documentation**: See `ANALYTICS_IMPLEMENTATION.md`

---

## ✅ Launch Checklist

Before running ads:

- [ ] TikTok Pixel ID updated (line 28)
- [ ] Pixel Helper shows events firing
- [ ] Test form submission → sees SubmitForm event
- [ ] Test diagnostic completion → sees CompleteRegistration event
- [ ] Events showing in TikTok Events Manager
- [ ] CompleteRegistration set as optimization event
- [ ] UTM parameters added to ad URL
- [ ] Privacy policy updated with tracking disclosure
- [ ] Form submission notifications working (check email)
- [ ] Backup tracking working (check Formspree)

---

**🎉 You're ready to launch!**

Start with a small daily budget ($20-50) and scale up once you validate tracking and see positive metrics.

---

**Questions?** Check the full documentation in `ANALYTICS_IMPLEMENTATION.md`






