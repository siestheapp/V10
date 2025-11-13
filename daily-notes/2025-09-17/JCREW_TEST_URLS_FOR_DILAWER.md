# J.Crew Test URLs for Dilawer

Since the database has J.Crew products but no URLs stored, here are **working J.Crew URLs** that Dilawer can test in the app. These correspond to products that exist in the database:

## ✅ **Working J.Crew URLs to Test:**

### 1. **Baird McNutt Irish Linen Shirt (MP123)**
- **URL**: `https://www.jcrew.com/p/mens/categories/clothing/shirts/linen/baird-mcnutt-irish-linen-shirt/MP123`
- **Database**: 35 variants in system
- **Good for testing**: Multiple colors/fits

### 2. **Secret Wash Cotton Poplin Shirt (CF783)**
- **URL**: `https://www.jcrew.com/p/mens/categories/clothing/shirts/secret-wash/secret-wash-cotton-poplin-shirt-with-point-collar/CF783`
- **Database**: 50 variants in system
- **Good for testing**: Lots of variants

### 3. **Secret Wash Cotton Poplin Shirt (MP832)**
- **URL**: `https://www.jcrew.com/p/mens/categories/clothing/shirts/secret-wash/secret-wash-cotton-poplin-shirt/MP832`
- **Database**: 45 variants in system
- **Good for testing**: Many options

### 4. **Secret Wash Cotton Poplin Shirt (BW439)**
- **URL**: `https://www.jcrew.com/p/mens/categories/clothing/shirts/secret-wash/secret-wash-cotton-poplin-shirt/BW439`
- **Database**: 40 variants in system

### 5. **Short-sleeve Baird McNutt Irish Linen Shirt (MP251)**
- **URL**: `https://www.jcrew.com/p/mens/categories/clothing/shirts/linen/short-sleeve-baird-mcnutt-irish-linen-shirt/MP251`
- **Database**: 18 variants in system

### 6. **Linen-cotton Blend Twill Workshirt (CG345)**
- **URL**: `https://www.jcrew.com/p/mens/categories/clothing/shirts/casual/linen-cotton-blend-twill-workshirt/CG345`
- **Database**: 6 variants in system

## 🎯 **Best URLs for Performance Testing:**

**Start with these 3 - they have the most variants and will stress-test the app:**

1. **CF783** (50 variants): `https://www.jcrew.com/p/mens/categories/clothing/shirts/secret-wash/secret-wash-cotton-poplin-shirt-with-point-collar/CF783`

2. **MP832** (45 variants): `https://www.jcrew.com/p/mens/categories/clothing/shirts/secret-wash/secret-wash-cotton-poplin-shirt/MP832`

3. **MP123** (35 variants): `https://www.jcrew.com/p/mens/categories/clothing/shirts/linen/baird-mcnutt-irish-linen-shirt/MP123`

## 📱 **How to Test:**

1. **Open the app** in simulator
2. **Go to Scan tab**
3. **Paste one of these URLs**
4. **The app should recognize it as J.Crew and load product data**
5. **Test the performance** while navigating through variants

## ⚠️ **Note:**

These URLs are constructed based on J.Crew's standard URL pattern and the product codes in our database. If any don't work, it means J.Crew has changed their URL structure or discontinued the product.

The app should handle both working and non-working URLs gracefully for performance testing purposes.