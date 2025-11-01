# Find Screen Redesign: What Changed & Why

## What I Updated in the Mockup

### 1. **Category-Specific Matching** ✅

**BEFORE:**
```
Match pill: "Strong match"
Shared item: "You both wear size S in Theory Perfect Tee"
```
❌ Problem: Matching on a TEE to recommend a DRESS size

**AFTER:**
```
Match pill: "Strong match • 3 shared dresses"
Shared item: "You both wear size S in Reformation Juliette Dress"
```
✅ Solution: Only matches on dresses. User sees relevance immediately.

---

### 2. **Keep/Return Status Badges** ✅

**NEW ELEMENT:**
```
✓ Kept it     (Green badge, top right)
✗ Returned it (Red badge, top right)
```

**Why it matters:**
- **2 twins bought M and KEPT it** = Strong buy signal
- **1 twin bought L and RETURNED it** = Warning signal

This is the #1 trust signal. More powerful than any algorithm.

---

### 3. **Fit Notes** ✅

**NEW SECTION:**
```
┌─────────────────────────────────────┐
│ 💬 Fit notes                         │
│ "Sized up for a looser fit. Perfect │
│  length at 5'6". Runs slightly small│
│  in bust."                           │
└─────────────────────────────────────┘
```

**What users ACTUALLY want to know:**
- Does it run small/large?
- How's the length?
- Any fit quirks?

This is Amazon reviews, but filtered by people who fit like you.

---

### 4. **Improved Recommendation Card** ✅

**BEFORE:**
```
We recommend size M
2 out of 3 twins bought size M
```

**AFTER:**
```
We recommend size M
2 out of 3 dress twins bought size M and kept it.
Your closest match (@sarah_chen with 3 shared dresses)
sized up from S to M.
```

**What changed:**
- "dress twins" (not just any twins)
- "and kept it" (outcome data)
- "3 shared dresses" (match strength)
- "sized up from S to M" (sizing direction)

More specific = more trustworthy.

---

### 5. **Transparent Match Strength** ✅

**Match Pills Now Show:**
```
✨ Strong match • 3 shared dresses
🎯 Good match • 2 shared dresses
👤 Match • 1 shared dress
```

**Why this wins:**
- Users see WHY it's a strong match
- Can judge for themselves
- Builds trust through honesty

---

### 6. **Different Scenarios** ✅

**Card 1:** Best case
- ✓ Kept it
- Strong match (3 shared dresses)
- Positive fit notes
- → Clear "Shop this size" CTA

**Card 2:** Also good
- ✓ Kept it
- Good match (2 shared dresses)
- Positive fit notes
- → "Shop this size" CTA

**Card 3:** Warning signal (HONEST)
- ✗ Returned it
- Weaker match (1 shared dress)
- Negative fit notes ("Runs very small")
- → "View details" CTA (not pushing the buy)

**Why show the returned one?**
Because it's VALUABLE data. "Maya tried L and it was too small" helps the user avoid the same mistake.

---

## Implementation Priority

### Must Have for Launch (Can't launch without):
1. ✅ Category-specific filtering
2. ✅ Match strength scoring
3. ✅ Keep/return tracking
4. ✅ Basic fit notes (multiple choice)
5. ✅ Transparent recommendations

### Should Have (Launch month 2-3):
6. ⏳ Free-form fit note text
7. ⏳ Photo uploads
8. ⏳ Height/measurements display

### Nice to Have (After traction):
9. ⏳ Community features
10. ⏳ Twin profiles
11. ⏳ Direct messaging

---

## Database Schema Additions Needed

### 1. Keep/Return Status
```sql
ALTER TABLE demo.user_owned_variant
ADD COLUMN keep_status TEXT DEFAULT 'pending';
-- Values: 'kept', 'returned', 'pending'

ADD COLUMN status_updated_at TIMESTAMPTZ;
```

### 2. Fit Notes
```sql
CREATE TABLE demo.fit_notes (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL,
  variant_id BIGINT NOT NULL,

  -- Multiple choice (required)
  fit_rating TEXT NOT NULL,
  -- Values: 'true_to_size', 'runs_small', 'runs_large', 'poor_fit'

  -- Free form (optional)
  notes TEXT,

  -- Specific details (optional)
  height_cm INTEGER,
  bust_cm INTEGER,
  waist_cm INTEGER,

  created_at TIMESTAMPTZ DEFAULT now()
);
```

### 3. Category Tracking
```sql
-- Already exists in public schema, just need to filter queries
-- Style has category_id → category table
```

### 4. Match Strength Calculation
```sql
-- RPC function update to count category-specific matches
CREATE OR REPLACE FUNCTION demo.api_find_size_twins(
  p_variant_id BIGINT,
  p_requesting_user_id UUID
)
RETURNS TABLE (
  twin_user_id UUID,
  twin_username TEXT,
  size_label TEXT,
  shared_items_same_category INT,  -- NEW: count by category
  keep_status TEXT,                 -- NEW: kept/returned/pending
  fit_rating TEXT,                  -- NEW: from fit_notes
  fit_notes TEXT,                   -- NEW: free form text
  match_strength INT                -- Overall score
)
```

---

## The User Flow That Wins

### Step 1: User Sees the Dress
```
User on Reformation.com
Sees: "Carina Linen Dress - $248"
Thinks: "Love it but what size?"
```

### Step 2: Opens Proxi
```
Copies URL
Opens Proxi app
Pastes into Find screen
Taps "Find Size Twins"
```

### Step 3: Sees Smart Recommendation
```
✨ We recommend size M

2 out of 3 dress twins bought size M and kept it.
Your closest match (@sarah_chen with 3 shared dresses)
sized up from S to M.
```

### Step 4: Reviews Twin Cards
```
Card 1: @sarah_chen
- ✓ Kept it
- Strong match (3 shared dresses)
- "Sized up for looser fit. Perfect at 5'6""

Card 2: @emma_rose
- ✓ Kept it
- Good match (2 shared dresses)
- "True to size. Love the length!"

Card 3: @maya_patel
- ✗ Returned it
- 1 shared dress
- "Sized up but still too tight. Runs very small"
```

### Step 5: Makes Decision
```
Thinks: "2 people kept M, 1 returned L because too small.
Sarah matches me on 3 dresses and sized up.
Emma says it's true to size.
I'll go with M."
```

### Step 6: Clicks Through
```
Taps: "Shop this size →"
Returns to Reformation
Adds size M to cart
Checks out with confidence
```

### Step 7: Becomes a Twin (Growth Loop)
```
Dress arrives
Proxi: "Did you keep the Reformation Carina Dress?"
User: "Yes! ✓"
Proxi: "How did it fit?"
User: "True to size, love it!"

→ User is now a twin for the next person
→ Cycle repeats
→ Network grows
```

---

## Why This Mockup Works for Investors/Landing Page

### It Shows:
1. **Clear value prop** - "Find your size" not "here's an algorithm"
2. **Social proof** - Real people, not faceless data
3. **Transparency** - Shows the math, builds trust
4. **Outcomes** - Kept it vs returned it (ROI signal)
5. **Network effects** - More users = better matches

### What to Say:
> "Unlike generic size charts, Proxi shows you what people with your EXACT fit bought - and whether they kept it. It's Amazon reviews, but filtered by body type. 2 out of 3 dress twins bought size M and loved it? That's a signal you can trust."

### The Investor Hook:
> "Every user who adds an item becomes a twin for someone else. The more users, the better the matches. And our marginal cost? $0. Users create all the value - photos, fit notes, keep/return data. We just organize it. That's how you scale to millions."

---

## Next Steps

### For Landing Page Video:
1. ✅ Screen record this mockup (auto-plays perfectly)
2. ✅ Show the journey: paste → loading → recommendation → twins
3. ✅ Highlight: kept/returned badges, fit notes, match strength
4. ✅ End on "Shop this size" button

### For MVP Development:
1. Build category filtering in RPC functions
2. Add keep_status column and tracking
3. Create fit_notes table and prompts
4. Update recommendation logic to use category + outcomes
5. Design fit note collection flow (2 weeks post-purchase)

### For User Testing:
1. Show this mockup to 10 target users
2. Ask: "Would you trust this recommendation?"
3. Ask: "What would make you MORE confident?"
4. Ask: "Would you share your fit notes?"
5. Iterate based on feedback

---

## The Bottom Line

**Before:** Generic "size twins" concept (unclear value)
**After:** Category-specific matches + outcomes + fit notes (clear value)

**Before:** "Here's what people bought" (meh)
**After:** "Here's what dress twins bought AND KEPT" (compelling)

**Before:** Algorithm black box (distrust)
**After:** Transparent data + real people (trust)

This is what will make Proxi a home run. 🎯
