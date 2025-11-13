# Fix Try-On Session Issues - Practical Solutions

## 📱 Problem 1: iOS App Only Runs in Simulator

### The Issue
The app won't run on a real iPhone, only in Xcode simulator.

### Quick Fix Steps

1. **Check Signing & Capabilities** (5 minutes)
```bash
# Open Xcode
open src/ios_app/V10.xcodeproj

# In Xcode:
# 1. Select V10 project in navigator
# 2. Select V10 target
# 3. Go to "Signing & Capabilities" tab
# 4. Check "Automatically manage signing"
# 5. Select your Apple Developer Team
# 6. Bundle Identifier should be: com.yourname.V10
```

2. **Add Your Device** (2 minutes)
```
# Connect iPhone via USB
# In Xcode:
# 1. Window → Devices and Simulators
# 2. Your iPhone should appear
# 3. If "Untrusted", unlock phone and tap "Trust This Computer"
# 4. Select your iPhone as run destination (next to play button)
```

3. **Fix Common Issues**
```bash
# If "Device Not Supported" error:
# - Update iOS on phone (Settings → General → Software Update)
# - Update Xcode if needed

# If "Could not launch" error:
# - On iPhone: Settings → General → Device Management
# - Trust your developer certificate

# If build fails:
# - Product → Clean Build Folder
# - Delete derived data:
rm -rf ~/Library/Developer/Xcode/DerivedData/V10-*
```

---

## 🗄️ Problem 2: Database Not Equipped for Try-Ons

### The Issue
Tables exist (`try_on_sessions`, `try_on_items`) but have 0 records. The backend endpoints aren't properly saving data.

### Fix the Backend Save Logic

**1. Fix the try-on session creation** (`src/ios_app/Backend/app.py`):

```python
@app.post("/tryon/create-session")
async def create_tryon_session(request: dict):
    """
    Create a new try-on session in the database
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        user_id = request.get("user_id", 1)
        location = request.get("location", "Home")
        brand = request.get("brand", "J.Crew")
        
        # Create session
        cur.execute("""
            INSERT INTO try_on_sessions (
                user_id, 
                store_location, 
                store_brand, 
                session_date,
                status,
                created_at
            ) VALUES (%s, %s, %s, NOW(), 'active', NOW())
            RETURNING id
        """, (user_id, location, brand))
        
        session_id = cur.fetchone()[0]
        conn.commit()
        
        return {
            "session_id": session_id,
            "status": "created",
            "message": "Try-on session started"
        }
        
    except Exception as e:
        conn.rollback()
        print(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.post("/tryon/add-item")
async def add_tryon_item(request: dict):
    """
    Add an item to the try-on session
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        session_id = request.get("session_id")
        product_url = request.get("product_url")
        size_tried = request.get("size_tried")
        
        # First, get or create the garment
        cur.execute("""
            SELECT id FROM garments 
            WHERE product_url = %s
        """, (product_url,))
        
        result = cur.fetchone()
        if result:
            garment_id = result[0]
        else:
            # Create garment if it doesn't exist
            brand_name = extract_brand_from_url(product_url)["brand_name"]
            product_name = extract_product_name_from_url(product_url)
            
            cur.execute("""
                SELECT id FROM brands WHERE name = %s
            """, (brand_name,))
            brand_id = cur.fetchone()[0] if cur.rowcount > 0 else 4  # Default to J.Crew
            
            cur.execute("""
                INSERT INTO garments (
                    brand_id,
                    product_name,
                    product_url,
                    category_id,
                    created_at
                ) VALUES (%s, %s, %s, 1, NOW())
                RETURNING id
            """, (brand_id, product_name, product_url))
            garment_id = cur.fetchone()[0]
        
        # Add to try_on_items
        cur.execute("""
            INSERT INTO try_on_items (
                session_id,
                garment_id,
                size_tried,
                try_order,
                created_at
            ) VALUES (%s, %s, %s, 
                (SELECT COALESCE(MAX(try_order), 0) + 1 FROM try_on_items WHERE session_id = %s),
                NOW()
            )
            RETURNING id
        """, (session_id, garment_id, size_tried, session_id))
        
        item_id = cur.fetchone()[0]
        conn.commit()
        
        return {
            "item_id": item_id,
            "garment_id": garment_id,
            "status": "added"
        }
        
    except Exception as e:
        conn.rollback()
        print(f"Error adding item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.post("/tryon/save-feedback")
async def save_tryon_feedback(request: dict):
    """
    Save detailed feedback for a try-on item
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        item_id = request.get("item_id")
        feedback = request.get("feedback")  # {chest: 3, neck: 2, etc}
        final_decision = request.get("final_decision", "pending")
        notes = request.get("notes", "")
        
        # Update try_on_items
        cur.execute("""
            UPDATE try_on_items
            SET final_decision = %s,
                notes = %s,
                fit_score = %s,
                updated_at = NOW()
            WHERE id = %s
        """, (final_decision, notes, 
              sum(feedback.values()) / len(feedback),  # Average score
              item_id))
        
        # Save dimension-specific feedback
        for dimension, rating in feedback.items():
            cur.execute("""
                INSERT INTO user_garment_feedback (
                    user_garment_id,
                    dimension,
                    feedback_code_id,
                    created_at,
                    created_by
                ) VALUES (
                    %s, %s, %s, NOW(), 1
                )
            """, (item_id, dimension, rating))
        
        conn.commit()
        
        return {
            "status": "saved",
            "item_id": item_id,
            "feedback_count": len(feedback)
        }
        
    except Exception as e:
        conn.rollback()
        print(f"Error saving feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
```

**2. Test the endpoints**:
```bash
# Test creating a session
curl -X POST http://localhost:8000/tryon/create-session \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "location": "Home", "brand": "J.Crew"}'

# Should return: {"session_id": 1, "status": "created", ...}
```

---

## 🎮 Problem 3: Try-On Flow Has Kinks

### The Issues in the iOS App

**1. Session Not Persisting to Database**

In `TryOnSessionView.swift`, fix the `createTryOnSession` function:

```swift
private func createTryOnSession(completion: @escaping (Bool) -> Void) {
    guard let url = URL(string: "http://localhost:8000/tryon/create-session") else {
        completion(false)
        return
    }
    
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let body: [String: Any] = [
        "user_id": 1,  // Get from actual user
        "location": "Home",
        "brand": garment.brand
    ]
    
    request.httpBody = try? JSONSerialization.data(withJSONObject: body)
    
    URLSession.shared.dataTask(with: request) { data, response, error in
        DispatchQueue.main.async {
            if let data = data,
               let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let sessionId = json["session_id"] as? Int {
                self.sessionId = sessionId
                print("✅ Session created with ID: \(sessionId)")
                completion(true)
            } else {
                print("❌ Failed to create session: \(error?.localizedDescription ?? "Unknown error")")
                completion(false)
            }
        }
    }.resume()
}
```

**2. Fix Feedback Submission**

In `TryOnSessionView.swift`, update `submitFeedback`:

```swift
private func submitFeedback(finalDecision: String, purchaseSize: String? = nil) {
    guard let sessionId = sessionId else {
        print("❌ No session ID")
        return
    }
    
    // First, add the item to the session
    addItemToSession { itemId in
        guard let itemId = itemId else {
            print("❌ Failed to add item")
            return
        }
        
        // Then save the feedback
        self.saveFeedback(itemId: itemId, finalDecision: finalDecision, purchaseSize: purchaseSize)
    }
}

private func addItemToSession(completion: @escaping (Int?) -> Void) {
    guard let url = URL(string: "http://localhost:8000/tryon/add-item") else {
        completion(nil)
        return
    }
    
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let body: [String: Any] = [
        "session_id": sessionId ?? 0,
        "product_url": productUrl,
        "size_tried": sessionState.selectedSize
    ]
    
    request.httpBody = try? JSONSerialization.data(withJSONObject: body)
    
    URLSession.shared.dataTask(with: request) { data, response, error in
        DispatchQueue.main.async {
            if let data = data,
               let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let itemId = json["item_id"] as? Int {
                completion(itemId)
            } else {
                completion(nil)
            }
        }
    }.resume()
}

private func saveFeedback(itemId: Int, finalDecision: String, purchaseSize: String?) {
    guard let url = URL(string: "http://localhost:8000/tryon/save-feedback") else {
        return
    }
    
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    // Convert feedback values to dictionary
    var feedbackDict: [String: Int] = [:]
    for (dimension, value) in sessionState.feedbackValues {
        feedbackDict[dimension.rawValue] = value
    }
    
    let body: [String: Any] = [
        "item_id": itemId,
        "feedback": feedbackDict,
        "final_decision": finalDecision,
        "notes": "Submitted from iOS app"
    ]
    
    request.httpBody = try? JSONSerialization.data(withJSONObject: body)
    
    URLSession.shared.dataTask(with: request) { data, response, error in
        DispatchQueue.main.async {
            if error == nil {
                print("✅ Feedback saved successfully")
                self.dismiss()
            } else {
                print("❌ Failed to save feedback: \(error?.localizedDescription ?? "")")
            }
        }
    }.resume()
}
```

**3. Fix Dimension Feedback Flow**

The app is asking for too many dimensions. Simplify in `TryOnSessionModels.swift`:

```swift
enum FitDimension: String, CaseIterable {
    case overall = "overall"
    case chest = "chest"
    case length = "length"
    // Remove neck, sleeve, waist for shirts - too granular
    
    var displayName: String {
        switch self {
        case .overall: return "Overall Fit"
        case .chest: return "Chest/Body"
        case .length: return "Length"
        }
    }
    
    var questionText: String {
        switch self {
        case .overall: return "How's the OVERALL fit?"
        case .chest: return "How does it fit through the BODY?"
        case .length: return "How's the LENGTH?"
        }
    }
}
```

---

## ✅ Quick Test Checklist

### 1. Backend is saving data:
```bash
# After trying on an item, check database:
psql $DATABASE_URL -c "SELECT * FROM try_on_sessions;"
psql $DATABASE_URL -c "SELECT * FROM try_on_items;"
```

### 2. iOS app is connecting:
```swift
// Add to viewDidAppear in TryOnSessionView:
print("🔗 Backend URL: http://localhost:8000")
print("📱 Product URL: \(productUrl)")
print("👕 Garment: \(garment.brand) - \(garment.productName)")
```

### 3. Data flow is complete:
1. Start try-on → Creates session in DB ✓
2. Select size → Saves to state ✓  
3. Give feedback → Creates try_on_item ✓
4. Submit → Saves feedback & decision ✓

---

## 🚀 Testing the Full Flow

1. **Start the backend**:
```bash
cd src/ios_app/Backend
python app.py
```

2. **Run iOS app on real device**:
- Open Xcode
- Select your iPhone
- Press Run

3. **Test J.Crew product**:
- Paste: `https://www.jcrew.com/p/mens/categories/clothing/shirts/casual/BH290`
- Select size: M
- Give feedback: Overall (4), Chest (3), Length (4)
- Submit

4. **Verify in database**:
```bash
psql $DATABASE_URL -c "SELECT * FROM try_on_sessions ORDER BY created_at DESC LIMIT 1;"
psql $DATABASE_URL -c "SELECT * FROM try_on_items ORDER BY created_at DESC LIMIT 1;"
```

---

## 📝 Summary

Your problems aren't about "tests" (unit tests), they're about:

1. **iOS provisioning** → Fix signing in Xcode
2. **Database integration** → Backend isn't saving to the right tables
3. **App flow** → Too complex, needs simplification

The code structure exists, it just needs to be connected properly!
