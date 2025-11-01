# Freestyle Demo App Setup

This guide will help you get the demo app running with Supabase integration.

## Prerequisites

- Expo/React Native development environment set up
- Access to your Supabase project dashboard

## Setup Steps

### 1. Get Your Supabase Anon Key

1. Go to your Supabase project dashboard: https://supabase.com/dashboard
2. Navigate to **Settings** > **API**
3. Copy the `anon` `public` key

### 2. Update Environment Variables

Edit `mobile/.env` and replace `your-anon-key-here` with your actual anon key:

```env
EXPO_PUBLIC_SUPABASE_URL=https://ymncgfobqwhkekbydyjx.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=<paste-your-anon-key-here>
```

### 3. Install Dependencies

```bash
cd mobile
npm install
```

### 4. Run the App

**iOS:**
```bash
npm run ios
```

**Android:**
```bash
npm run android
```

**Web (for testing):**
```bash
npm run web
```

## How It Works

### Demo Flow

1. **Sign In Screen** (`/auth/signin`)
   - Click "Continue with Google (demo)"
   - Creates a random demo user (`user123`, etc.)
   - Stores user ID in AsyncStorage
   - Navigates to home feed

2. **Home Feed** (`/(tabs)/home`)
   - Shows "size twins" - other users who own the same items in the same size
   - Initially empty until you add items
   - Pull to refresh to update feed
   - Tap "+ Add Item" to add your first item

3. **Add Item Screen** (`/add-item`)
   - Paste a product URL from a supported brand
   - App resolves URL to product variant
   - Supported brands: Theory, Aritzia, Babaton, J.Crew, etc.

4. **Confirm Item Screen** (`/confirm-item`)
   - Shows product image, brand, and style name
   - Select your size (XXS - XXL)
   - Tap "Add to Closet" to claim ownership

5. **Feed Updates**
   - Once multiple users own the same variant/size
   - Feed shows "proxy cards" with pill text like:
     - "user456 also owns Theory Shirt (XS)"
   - Shows product image, brand, style, and shared size

## Database Architecture

### Demo Schema (Safe Sandbox)
- All writes go to `demo.*` tables
- No production data is touched
- Can be reset anytime

### Public Schema (Read-Only)
- Real product catalog (brands, styles, variants)
- Images, prices, and product URLs
- Used for lookups and display

## Testing with Multiple Users

To see the proxy feed in action:

1. **User 1**: Sign in, add an item with size "S"
2. **User 2**: Sign in (different device/session), add the SAME item with size "S"
3. **Check feeds**: Both users will now see each other in their feeds!

## Sample Product URLs for Testing

Here are some product URLs from the database you can test with:

```
# Check your database for actual product URLs:
SELECT url FROM public.product_url LIMIT 10;
```

## Troubleshooting

### "Missing Supabase environment variables"
- Make sure `.env` file exists in `mobile/` directory
- Check that anon key is correctly pasted (no extra spaces)
- Restart Expo dev server after changing `.env`

### "Error calling RPC function"
- Verify database setup is complete (see DATABASE_CONNECTION_GUIDE.md)
- Check Supabase logs in dashboard for detailed errors
- Ensure RPC functions were created and granted to `anon` role

### Feed is empty
- Add at least one item to your closet
- Have another demo user add the same item/size
- Pull to refresh the feed

### URL resolution fails
- The URL must match entries in `public.product_url` table
- Check available URLs with: `SELECT url FROM public.product_url LIMIT 20;`
- URL must be from a brand that exists in your catalog

## Resetting Demo Data

To start fresh:

```sql
TRUNCATE TABLE demo.user_owned_variant RESTART IDENTITY CASCADE;
TRUNCATE TABLE demo.user_profile RESTART IDENTITY CASCADE;
```

Then clear app storage:
- iOS: Uninstall and reinstall app
- Android: Clear app data
- Web: Clear browser localStorage

## Security Notes

✅ **Safe for demo:**
- Anon key can only access demo schema
- RLS policies restrict to demo tables
- No production data can be modified

⚠️ **Production considerations:**
- Replace fake Google auth with real OAuth
- Add user-specific RLS policies
- Implement proper session management
- Use separate schema or database for production

## Next Steps

- Add more brands and products to catalog
- Implement real authentication
- Add user profiles and settings
- Build out closet management
- Add social features (follow users, etc.)

## Support

For issues or questions, check:
- `DATABASE_CONNECTION_GUIDE.md` for database setup
- Supabase documentation: https://supabase.com/docs
- Expo documentation: https://docs.expo.dev

