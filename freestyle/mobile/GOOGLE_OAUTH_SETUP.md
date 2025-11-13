# Google OAuth Integration - Setup Complete!

## ✅ What Was Implemented

### 1. Dependencies Installed
- ✅ `expo-auth-session` - OAuth flow handling
- ✅ `expo-web-browser` - Browser session management

### 2. Database Changes
- ✅ Updated `demo.api_signup` RPC to accept optional `p_user_id` parameter
- ✅ Granted execute permissions to anon role for updated function
- ✅ Now supports linking real auth users to demo profiles

### 3. Code Changes

**New Files:**
- ✅ `mobile/src/lib/auth.ts` - Auth helper functions
  - `linkToDemoProfile()` - Links Google user to demo profile
  - `getCurrentUser()` - Gets current session
  - `signOut()` - Signs out user

**Modified Files:**
- ✅ `mobile/src/lib/supabase.ts` - Enabled session persistence with AsyncStorage
- ✅ `mobile/app/auth/signin.tsx` - Real Google OAuth implementation
- ✅ `mobile/app/(tabs)/home.tsx` - Uses real session instead of AsyncStorage
- ✅ `mobile/app/confirm-item.tsx` - Uses real session instead of AsyncStorage

### 4. How It Works

1. **User taps "Continue with Google"**
   - App opens Google OAuth in browser
   - User selects Google account
   - Browser redirects back to app

2. **Auth State Listener Fires**
   - Detects `SIGNED_IN` event
   - Calls `linkToDemoProfile()` to create demo profile with real user ID
   - Navigates to home feed

3. **Subsequent Screens**
   - Use `supabase.auth.getSession()` to get real user ID
   - All RPC calls use real auth user ID
   - Demo profiles linked to real auth accounts

## 🚀 Next Steps - Required Configuration

### Step 1: Get Your Redirect URI

Run the app and check the console logs when you tap "Continue with Google". You'll see:

```
Redirect URI: freestyle://127.0.0.1:19000/--/
Add this URL to Supabase Dashboard → Auth → URL Configuration → Redirect URLs
```

The redirect URI will be something like:
- Development: `freestyle://127.0.0.1:19000/--/`
- Expo Go: `exp://127.0.0.1:19000/--/`
- Production: `freestyle://redirect`

### Step 2: Configure Supabase Dashboard

1. Go to **Supabase Dashboard** → **Authentication** → **URL Configuration**
2. Under **Redirect URLs**, add:
   - The exact redirect URI from your console log
   - Also add: `freestyle://redirect` (for production builds)
   - Also add: `exp://127.0.0.1:19000/--/` (if using Expo Go)

3. Click **Save**

### Step 3: Verify Google OAuth Provider

1. Go to **Supabase Dashboard** → **Authentication** → **Providers**
2. Find **Google** in the list
3. Verify:
   - ✅ Enabled toggle is ON
   - ✅ Client ID is filled in
   - ✅ Client Secret is filled in
   - ✅ Authorized Client IDs (if applicable)

### Step 4: Verify Google Cloud Configuration

Your Google OAuth client should have these redirect URIs:

1. **Web Application** redirect:
   ```
   https://ymncgfobqwhkekbydyjx.supabase.co/auth/v1/callback
   ```

2. **Authorized JavaScript origins** (optional for testing):
   ```
   http://localhost:19000
   http://127.0.0.1:19000
   ```

## 🧪 Testing

### Test the Flow

1. **Start the app:**
   ```bash
   cd mobile
   npm run ios
   # or
   npm run android
   ```

2. **Sign In:**
   - Tap "Continue with Google"
   - Check console for redirect URI (add to Supabase if not already)
   - You should see Google account picker
   - Select an account
   - App should redirect back and navigate to home

3. **Verify Demo Profile:**
   Check your database:
   ```sql
   SELECT * FROM demo.user_profile ORDER BY created_at DESC LIMIT 5;
   ```
   
   You should see a profile with:
   - `id` matching your Supabase auth user ID
   - `username` from your email (e.g., "seandavey" from seandavey@gmail.com)

4. **Add an Item:**
   - Tap "+ Add Item"
   - Paste a product URL
   - Select size
   - Add to closet
   - Check feed for matches

## 🔐 Security Benefits

- ✅ **Real Authentication** - Uses Google OAuth, not fake sign-in
- ✅ **Demo Schema Isolation** - All writes still go to `demo.*` tables
- ✅ **Production Safety** - Can reset demo data without affecting auth
- ✅ **Session Persistence** - Users stay signed in
- ✅ **Secure Storage** - Sessions stored in AsyncStorage

## 🐛 Troubleshooting

### "Redirect not allowed" Error
**Solution:** Add the exact redirect URI from console logs to Supabase Dashboard → Auth → Redirect URLs

### Stuck in Browser After Sign-In
**Solution:** 
1. Ensure `freestyle://` scheme matches `app.json`
2. Check that `WebBrowser.maybeCompleteAuthSession()` is called
3. Try rebuilding the app: `npm run ios -- --reset-cache`

### "Provider not configured" Error
**Solution:** Verify Google provider is enabled in Supabase Dashboard with correct Client ID/Secret

### No Demo Profile Created
**Solution:** 
1. Check console for errors in `linkToDemoProfile()`
2. Verify `api_signup` RPC accepts `p_user_id` parameter:
   ```sql
   \df demo.api_signup
   ```
3. Check database logs in Supabase Dashboard

### OAuth Opens But Nothing Happens
**Solution:**
1. Check if URL is in test mode (Google Cloud Console → OAuth consent screen)
2. Add your Google account to test users
3. Check Supabase logs for auth errors

## 📝 Implementation Notes

### Hybrid Approach
- Real Google authentication for user management
- Demo schema for safe testing and data isolation
- Best of both worlds: real auth + safe sandbox

### Session Management
- Sessions persist across app restarts
- Auto-refresh tokens enabled
- Stored securely in AsyncStorage

### User Linking
- Google user ID = demo profile ID
- One-to-one mapping
- Username derived from email

## 🎯 Current Scheme Configuration

From your `app.json`:
```json
{
  "scheme": "freestyle",
  "ios": {
    "bundleIdentifier": "com.davey.proxy"
  }
}
```

This means your redirect URIs will use `freestyle://` prefix.

## 📱 Testing on Different Platforms

### iOS Simulator
- Works with `freestyle://` scheme
- May need Xcode rebuild after scheme changes

### Android Emulator
- Works with `freestyle://` scheme
- May need to rebuild after changing app.json

### Physical Device
- Best testing experience
- Most reliable OAuth flow
- Test with: `npm run ios` or `npm run android`

### Expo Go
- May use `exp://` instead of `freestyle://`
- Add both redirect URIs to Supabase if testing with Expo Go

## ✨ What's New vs Old Implementation

| Feature | Old (Fake Sign-In) | New (Real OAuth) |
|---------|-------------------|------------------|
| Authentication | Random username | Real Google account |
| Session | AsyncStorage only | Supabase auth session |
| User ID | Generated UUID | Real auth user ID |
| Persistence | Manual storage | Auto-persisted |
| Security | Demo only | Production-ready auth |
| User Management | None | Full Supabase auth |

## 🚀 Ready to Test!

Your app is now configured for real Google OAuth! Just:

1. Run the app
2. Note the redirect URI in console
3. Add it to Supabase Dashboard
4. Test the sign-in flow

The app will log the exact redirect URI you need - just copy and paste it into Supabase! 🎉

