# 📊 Analytics Implementation Guide - Proxi Landing Page

## ✅ What's Been Implemented

### 🎯 **Priority 1: TikTok Pixel Integration**
- ✅ TikTok Pixel base code installed
- ✅ Standard event tracking (PageView, SubmitForm, CompleteRegistration)
- ✅ Custom event tracking integrated
- ✅ Content tracking for video and diagnostic questions

### 🔗 **Priority 2: Enhanced Attribution**
- ✅ TikTok Click ID (ttclid) capture
- ✅ Facebook Click ID (fbclid) capture  
- ✅ Google Click ID (gclid) capture
- ✅ Full UTM parameter tracking (source, medium, campaign, term, content)
- ✅ Session-persistent attribution (survives page refreshes)

### 📹 **Video Engagement Tracking**
- ✅ Play events (distinguishes autoplay vs manual)
- ✅ Pause events (with progress percentage)
- ✅ Progress milestones (25%, 50%, 75%)
- ✅ Completion tracking
- ✅ TikTok Pixel ViewContent event on video play

### 🎯 **CTA Button Tracking**
- ✅ Button click tracking with location context (hero vs bottom)
- ✅ Button text capture
- ✅ TikTok Pixel ClickButton event

### 📝 **Form Interaction Tracking**
- ✅ Form view tracking (when form enters viewport)
- ✅ Form start tracking (first focus on email field)
- ✅ Field focus/blur with time spent
- ✅ First character input tracking
- ✅ Validation error tracking
- ✅ Form submission tracking (with time-to-submit)
- ✅ Form abandonment tracking (user leaves without submitting)
- ✅ Scroll-past tracking (user sees form but doesn't engage)
- ✅ TikTok Pixel SubmitForm event on form submission

### 🔍 **Diagnostic Question Tracking**
- ✅ Diagnostic view tracking
- ✅ Brand selection tracking
- ✅ Diagnostic completion tracking
- ✅ TikTok Pixel CompleteRegistration event on diagnostic completion
- ✅ Skip tracking

### 💻 **Device & Context Tracking**
- ✅ Screen resolution
- ✅ Viewport size
- ✅ Device pixel ratio
- ✅ Platform (OS)
- ✅ Language
- ✅ Touch capability detection
- ✅ Connection type (4G, 5G, etc.)
- ✅ Timezone

---

## 🚀 Setup Instructions

### Step 1: Get Your TikTok Pixel ID

1. Go to [TikTok Ads Manager](https://ads.tiktok.com/)
2. Navigate to **Assets** → **Events** in the left sidebar
3. Click **Manage** next to "Web Events"
4. Click **Create Pixel** if you don't have one
5. Copy your **Pixel ID** (looks like: `C9N7BK1234567890ABCD`)

### Step 2: Update Your Landing Page

Open `/freestyle-october/index.html` and find line 28:

```javascript
// TODO: Replace 'YOUR_TIKTOK_PIXEL_ID' with your actual TikTok Pixel ID
ttq.load('YOUR_TIKTOK_PIXEL_ID');
```

Replace `YOUR_TIKTOK_PIXEL_ID` with your actual Pixel ID:

```javascript
ttq.load('C9N7BK1234567890ABCD');
```

### Step 3: Test Your Pixel

1. Install the [TikTok Pixel Helper Chrome Extension](https://chrome.google.com/webstore/detail/tiktok-pixel-helper/)
2. Visit your landing page
3. Click the extension icon - you should see your Pixel ID and events firing
4. Test all interactions:
   - Page load (should fire PageView)
   - Video play
   - CTA button click
   - Form submission (should fire SubmitForm)
   - Diagnostic completion (should fire CompleteRegistration)

### Step 4: Verify in TikTok Events Manager

1. Go back to **TikTok Ads Manager** → **Assets** → **Events**
2. Click on your Pixel
3. You should see events appearing in real-time
4. Wait 15-30 minutes for the "Test Events" tab to populate

---

## 📈 Events Being Tracked

### TikTok Pixel Standard Events

| Event | Trigger | Purpose |
|-------|---------|---------|
| `PageView` | Page loads | Track page visits, build audiences |
| `ViewContent` | Video plays, diagnostic viewed | Track content engagement |
| `ClickButton` | CTA button clicked | Track button engagement |
| `SubmitForm` | Form submitted | Track conversion intent |
| `CompleteRegistration` | Diagnostic completed | **Primary conversion event** |

### Custom Events (Formspree)

| Event Type | Description | Data Captured |
|------------|-------------|---------------|
| `page_view` | Initial page load | URL, UTM params, device info |
| `heartbeat` | Every 20 seconds | Time on page, visibility state |
| `video_play` | Video starts playing | Autoplay vs manual |
| `video_progress` | 25%, 50%, 75% milestones | Progress percentage |
| `video_pause` | Video paused | Current time, percentage |
| `video_complete` | Video finished | N/A |
| `cta_click` | CTA button clicked | Location (hero/bottom), button text |
| `form_view` | Form enters viewport | Location |
| `form_start` | User focuses email field | Location, timestamp |
| `form_field_blur` | User leaves email field | Time spent, has value, value length |
| `form_field_input` | First character typed | Field name |
| `form_error` | Validation error | Error message |
| `form_submit` | Form submitted | Location, time-to-submit, error count |
| `form_abandon` | User leaves without submitting | Time spent, had errors, field had value |
| `form_scroll_past` | User scrolls past without engaging | Location |
| `diagnostic_view` | Diagnostic question shown | N/A |
| `diagnostic_select` | Brand selected | Selected brand |
| `diagnostic_complete` | Diagnostic submitted/skipped | Brand choice |
| `mock_click` | Mockup clicked | Which mockup |
| `mock_button_click` | Button inside mockup clicked | Button identifier |
| `section_dwell` | Time spent in section | Section name, duration |
| `scroll_depth` | 25%, 50%, 75%, 100% reached | Percentage |
| `hover` | Mouse hover on tracked elements | Element, duration |
| `faq_toggle` | FAQ item opened/closed | Question text, open/closed |
| `nav_click` | Navigation link clicked | Link href |
| `outbound_click` | External link clicked | URL |
| `page_dwell` | Total time on page | Duration |

---

## 🎯 TikTok Ad Campaign Optimization

### Conversion Event Setup

1. In TikTok Ads Manager, go to **Campaign** → **Create**
2. Choose **Website Conversions** as your objective
3. For **Optimization Event**, select **CompleteRegistration**
   - This fires when users complete your diagnostic question
   - This is your **primary conversion event**

### Alternative Optimization Events

| Event | When to Use |
|-------|-------------|
| `CompleteRegistration` | ✅ **Recommended** - Full funnel completion |
| `SubmitForm` | If you want to optimize for form submissions (before diagnostic) |
| `ClickButton` | Early-stage campaigns, optimizing for engagement |
| `PageView` | Brand awareness campaigns |

### URL Structure for TikTok Ads

Use this URL structure in your TikTok ads to ensure proper tracking:

```
https://yourdomain.com/?utm_source=tiktok&utm_medium=cpc&utm_campaign=waitlist_q4&utm_content=video_v1
```

TikTok will automatically append `ttclid` parameter for conversion tracking.

---

## 📊 Data Analysis

### Formspree Data (Custom Events)

Your custom event data is being sent to: `https://formspree.io/f/meorpayo`

**To access your data:**
1. Go to [Formspree Dashboard](https://formspree.io/forms)
2. Find the form with ID `meorpayo`
3. Export submissions to CSV for analysis

**Key Metrics to Track:**
- **Conversion Rate**: form_submit / page_view
- **Engagement Rate**: form_start / form_view
- **Abandonment Rate**: form_abandon / form_start
- **Video Completion Rate**: video_complete / video_play
- **Time to Convert**: Check `timeToSubmit` in form_submit events
- **Top Struggle Brands**: From diagnostic_complete events

### TikTok Events Manager

**To view your TikTok data:**
1. Go to **TikTok Ads Manager** → **Assets** → **Events**
2. Click on your Pixel
3. View real-time events and conversion data

**Key Reports:**
- **Event Activity**: See all events firing in real-time
- **Test Events**: Verify tracking before going live
- **Audience Size**: See how many users you can retarget

---

## 🔥 Advanced: Retargeting Audiences

Once you have traffic, create these audiences in TikTok:

### Audience 1: Page Visitors (Cold)
- **Event**: PageView
- **Timeframe**: Last 30 days
- **Use**: Retarget people who visited but didn't engage

### Audience 2: Video Watchers (Warm)
- **Event**: ViewContent (where content_name = hero_demo)
- **Timeframe**: Last 14 days
- **Use**: Retarget engaged users

### Audience 3: Form Starters (Hot)
- **Custom Event**: form_start
- **Timeframe**: Last 7 days
- **Use**: Retarget users who engaged with form but didn't submit

### Audience 4: Converters (Exclude)
- **Event**: CompleteRegistration
- **Timeframe**: Last 180 days
- **Use**: Exclude from acquisition campaigns

---

## 🔐 Privacy & Compliance

### Data Being Collected

**Personal Data:**
- Email address (only when submitted)
- IP address (via TikTok Pixel)
- Browser fingerprint (via session ID)

**Anonymous Data:**
- Device info, screen size, browser details
- Interaction events (clicks, scrolls, hovers)
- Time spent on page/sections

### Compliance Notes

✅ **GDPR/CCPA**: Your page doesn't include a cookie consent banner. Consider adding one if you're targeting EU/CA users.

✅ **Privacy Policy**: You have a privacy policy link in the footer - make sure it discloses:
- TikTok Pixel usage
- Data collection practices
- Cookie usage
- Third-party data sharing (Formspree, TikTok)

---

## 🐛 Troubleshooting

### "TikTok Pixel Not Firing"

1. Check console for errors: `console.log(window.ttq)`
2. Verify Pixel ID is correct (line 28 of index.html)
3. Install TikTok Pixel Helper extension
4. Check if ad blockers are interfering

### "Events Not Showing in TikTok"

1. Wait 15-30 minutes - TikTok has delay
2. Check Test Events tab instead of Event Activity
3. Verify your Pixel status is "Active"
4. Try a different browser/device

### "Formspree Events Not Arriving"

1. Check Network tab in DevTools for 200 response from Formspree
2. Verify `meorpayo` form ID is correct
3. Check spam folder in Formspree email notifications
4. Events are batched - may take a few minutes

---

## 📈 Next Steps

### Immediate (Before Running Ads)
1. ✅ Replace TikTok Pixel ID (line 28)
2. ✅ Test all events with Pixel Helper extension
3. ✅ Verify events in TikTok Events Manager
4. ✅ Set up CompleteRegistration as optimization event
5. ✅ Create retargeting audiences

### Short-term (First Week)
1. Monitor conversion rates daily
2. Check for tracking errors in console
3. Analyze which brands users select in diagnostic
4. Test different video creatives (track completion rates)
5. A/B test CTA copy (track click rates by button text)

### Long-term (Ongoing)
1. Build lookalike audiences from converters
2. Analyze time-to-convert to optimize ad frequency
3. Track scroll depth to optimize page length
4. Monitor form abandonment to identify friction
5. Segment by device type, connection speed, etc.

---

## 🎁 Bonus: Quick Analytics Dashboard

Here's a simple way to visualize your Formspree data:

1. Export submissions to CSV from Formspree
2. Import to Google Sheets
3. Create pivot tables for:
   - Events by type
   - Conversions by UTM source/campaign
   - Form abandonment by location
   - Video completion rates
   - Top struggle brands

---

## 📞 Support

If you encounter issues:
- **TikTok Pixel**: [TikTok Ads Support](https://ads.tiktok.com/help/)
- **Formspree**: [Formspree Support](https://help.formspree.io/)
- **General Tracking**: Check browser console for JavaScript errors

---

**Last Updated**: October 24, 2025  
**Author**: AI Assistant  
**Version**: 1.0






