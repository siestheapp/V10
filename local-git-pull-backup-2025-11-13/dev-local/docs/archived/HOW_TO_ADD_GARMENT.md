# How to Add a Garment to the Database

**Created**: January 20, 2025  
**Purpose**: Simple guide for adding garments to your V10 closet database  

---

## 🎯 **Quick Overview**

There are **3 ways** to add a garment to your database:

1. **🌐 Web Interface** (Easiest) - User-friendly form
2. **🤖 AI Assistant** (Recommended) - I can do it for you  
3. **💻 Manual SQL** (Advanced) - Direct database commands

---

## 🌐 **Method 1: Web Interface (Easiest)**

### **Step 1: Start the Web Server**
```bash
cd /Users/seandavey/projects/V10
source venv/bin/activate
python scripts/admin/web_garment_manager.py
```

### **Step 2: Open Browser**
- Go to: `http://localhost:5000`
- Click "Add Garment"

### **Step 3: Fill Form**
- **User Email**: `user1@example.com`
- **Brand**: Select or type brand name
- **Category**: Usually "Tops"
- **Size**: Select from dropdown or choose "Other"
- **Gender**: Male/Female/Unisex
- **Fit Type**: Regular/Slim/Tall/NA
- **Product Name**: Optional but recommended
- **Product URL**: Optional

### **Step 4: Submit**
- Click "Add Garment"
- System automatically links to size guide if available

---

## 🤖 **Method 2: AI Assistant (Recommended)**

Just tell me what you want to add! I need:

### **Required Info:**
- **Brand**: e.g., "Uniqlo"
- **Size**: e.g., "M"
- **Type**: e.g., "T-shirt", "Button-down", etc.

### **Optional Info:**
- **Product name**: Specific product name
- **How it fits**: "Perfect Fit", "Good Fit", "Too Loose", etc.
- **Product URL**: Link to the item online
- **Notes**: Any special details

### **Example Request:**
> "Add a Uniqlo Medium t-shirt to my closet. It fits perfectly."

I'll handle all the database work automatically!

---

## 💻 **Method 3: Manual SQL (Advanced)**

### **Step 1: Get Required IDs**
```sql
-- Get user ID
SELECT id FROM users WHERE email = 'user1@example.com';

-- Get brand ID (or create if needed)
SELECT id FROM brands WHERE name = 'Uniqlo';

-- Get category ID
SELECT id FROM categories WHERE name = 'Tops';
```

### **Step 2: Insert Garment**
```sql
INSERT INTO user_garments (
    user_id, brand_id, category_id, subcategory_id, gender, 
    size_label, fit_type, unit, product_name, product_url, owns_garment,
    size_guide_id, size_guide_entry_id
) VALUES (
    1,          -- user_id
    12,         -- brand_id (Uniqlo)
    1,          -- category_id (Tops)
    NULL,       -- subcategory_id (optional)
    'Male',     -- gender
    'M',        -- size_label
    'NA',       -- fit_type
    'in',       -- unit
    'Basic T-Shirt',  -- product_name
    NULL,       -- product_url
    true,       -- owns_garment
    14,         -- size_guide_id (if available)
    NULL        -- size_guide_entry_id (if available)
) RETURNING id;
```

---

## 📋 **Required Information**

### **Always Needed:**
- ✅ **Brand name** (must exist in brands table)
- ✅ **Size** (e.g., S, M, L, XL)
- ✅ **Category** (usually "Tops")
- ✅ **Gender** (Male/Female/Unisex)

### **Usually Needed:**
- 📝 **Product name** (what kind of item it is)
- 📝 **Fit type** (Regular/Slim/Tall/NA)

### **Optional:**
- 🔗 **Product URL** (link to buy it online)
- 📝 **Notes** (any special details)
- 📂 **Subcategory** (T-Shirts, Button-Downs, etc.)

---

## 🔄 **After Adding a Garment**

### **Add Feedback (Recommended):**
Once you add a garment, you should add feedback about how it fits:

- **"Perfect Fit"** - Ideal fit
- **"Good Fit"** - Fits well
- **"Loose but I Like It"** - Intentionally loose
- **"Tight but I Like It"** - Intentionally fitted
- **"Too Loose"** - Would prefer smaller
- **"Too Tight"** - Would prefer larger

This helps your V10 app learn your preferences!

---

## 🚀 **Size Guide Auto-Linking**

If a size guide exists for the brand, the system will automatically:
- ✅ Link your garment to the size guide
- ✅ Connect to specific size measurements
- ✅ Enable dimensional fit analysis

**Brands with size guides:**
- Uniqlo ✅
- Lacoste ✅  
- J.Crew ✅
- Banana Republic ✅
- Patagonia ✅
- Lululemon ✅
- Faherty ✅
- Theory ✅
- Reiss ✅
- NN.07 ✅

---

## ❓ **Need Help?**

### **For Web Interface Issues:**
- Make sure virtual environment is activated
- Check that port 5000 isn't already in use
- Look for error messages in terminal

### **For AI Assistant Method:**
Just ask! Examples:
- "Add my Uniqlo large t-shirt"
- "I have a medium J.Crew button-down that fits perfectly"
- "Add a Patagonia XL shirt that's loose but I like it"

### **For Manual SQL:**
- Use the Database Query Cookbook for tested queries
- Check `logs/database_changes.log` to see what was added
- Verify with: `SELECT * FROM user_garments WHERE id = [new_id];`

---

**Last Updated**: January 20, 2025  
**Next Update**: Add screenshots of web interface
