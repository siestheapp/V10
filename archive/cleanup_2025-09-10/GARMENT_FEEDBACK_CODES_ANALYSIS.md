# Should We Create Separate Feedback Codes for Garment Measurements?

## Current Situation
Same feedback codes for both body and garment measurements:
- "Too Tight", "Good Fit", "Too Loose", etc.

## Option 1: Keep Same Codes (Current)

### Example:
```
Body Feedback:    Chest 42-44" → "Good Fit"
Garment Feedback: Chest 20.5"  → "Too Tight"
```

### PROS:
✅ **Simpler** - One set of codes to maintain
✅ **Consistent UX** - Users learn one set of options
✅ **Direct comparison** - Can query: "Why is body 'Good Fit' but garment 'Too Tight'?"
✅ **Less complexity** - No need to update iOS app with conditional logic

### CONS:
❌ **Ambiguous** - "Too Tight" on 20.5" width vs "Too Tight" on 42-44" body
❌ **Missing context** - Can't express garment-specific issues
❌ **Confusing analysis** - Developers might mix up feedback types

## Option 2: Create Garment-Specific Codes

### New Feedback Codes for Garments:
```sql
-- Garment Fit Codes (g_ prefix)
INSERT INTO feedback_codes (feedback_text, measurement_source_type) VALUES
('g_Runs Small', 'garment_spec'),           -- Smaller than size guide suggests
('g_True to Spec', 'garment_spec'),         -- Matches measurements
('g_Runs Large', 'garment_spec'),           -- Larger than expected
('g_Shrunk After Wash', 'garment_spec'),    -- Post-wash feedback
('g_Fabric Stretches', 'garment_spec'),     -- Material property
('g_Measurement Seems Wrong', 'garment_spec'); -- Quality issue
```

### PROS:
✅ **Clear distinction** - No confusion about feedback type
✅ **Richer insights** - "Runs Small" vs just "Too Tight"
✅ **Garment-specific issues** - Shrinkage, stretch, quality
✅ **Better queries** - Can filter by feedback type easily

### CONS:
❌ **More complexity** - Two sets of codes to maintain
❌ **iOS app changes** - Need conditional UI based on measurement type
❌ **User learning curve** - Different options for different contexts
❌ **Data migration** - Need to ensure old codes don't mix

## Option 3: Hybrid Approach (RECOMMENDED)

### Keep core codes, add garment-specific ones:
```sql
-- Shared codes (work for both)
"Too Tight" (id: 1)
"Good Fit" (id: 3)
"Too Loose" (id: 4)

-- Garment-specific additions
"Runs Smaller Than Size Guide" (id: 14)
"Runs Larger Than Size Guide" (id: 15)  
"Accurate to Measurements" (id: 16)
"Shrunk After Washing" (id: 17)
```

### Implementation:
```sql
-- Add a column to track which codes apply where
ALTER TABLE feedback_codes
ADD COLUMN applicable_to TEXT[] DEFAULT ARRAY['size_guide', 'garment_spec'];

-- Mark garment-specific codes
UPDATE feedback_codes 
SET applicable_to = ARRAY['garment_spec']
WHERE id >= 14;
```

### PROS:
✅ **Backwards compatible** - Existing codes still work
✅ **Progressive enhancement** - Add specificity where valuable
✅ **Flexible** - Can use simple or detailed feedback
✅ **Clear intent** - Garment codes have descriptive names

## Real-World Example

### User tries on NN07 Size M:

**Without separate codes:**
- Chest (body): "Good Fit"
- Chest (garment): "Too Tight"
- Analysis: ??? Confusing

**With hybrid codes:**
- Chest (body): "Good Fit" 
- Chest (garment): "Runs Smaller Than Size Guide"
- Analysis: Clear - garment doesn't match its size guide!

## SQL to Implement Hybrid Approach

```sql
-- Add garment-specific feedback codes
INSERT INTO feedback_codes (feedback_text) VALUES
('Runs Smaller Than Size Guide'),
('Runs Larger Than Size Guide'),
('Accurate to Measurements'),
('Shrunk After Washing'),
('Fabric Has Good Stretch'),
('Fabric Has No Stretch'),
('Measurement Seems Incorrect');

-- Track applicability (optional but helpful)
ALTER TABLE feedback_codes
ADD COLUMN IF NOT EXISTS applicable_to TEXT[] 
DEFAULT ARRAY['size_guide', 'garment_spec'];

-- Mark garment-specific codes
UPDATE feedback_codes
SET applicable_to = ARRAY['garment_spec']
WHERE feedback_text LIKE 'Runs %' 
   OR feedback_text LIKE '%Shrunk%'
   OR feedback_text LIKE '%Measurement%';
```

## Recommendation

**Go with Option 3 (Hybrid)**:
1. Keeps it simple for basic feedback
2. Adds precision where it matters
3. Backwards compatible
4. Provides richer insights

The key insight: "Too Tight" means different things for body vs garment measurements. Having codes like "Runs Smaller Than Size Guide" makes the data much more actionable!
