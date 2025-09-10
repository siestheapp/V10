# Garment Feedback Strategy

## Current Situation
- **Body measurements**: Have feedback (chest, neck, sleeve)
- **Garment measurements**: NO feedback yet (coming soon for NN.07 data)

## Your Questions Answered:

### 1. Should garment feedback be separate columns or share existing ones?
**Answer: SEPARATE COLUMNS**

Why:
- Body feedback: "My chest feels tight" (about fit on body)
- Garment feedback: "The chest width measurement seems off" (about the actual garment spec)
- These are fundamentally different types of feedback

### 2. Is user_garment_id enough for uniqueness?
**Answer: YES, it's perfect!**

- `user_garment_id` is globally unique (PRIMARY KEY)
- Each ID already links to a specific user via `user_garments.user_id`
- No risk of collision between users

## Recommended Approach:

### Option A: Add More Columns (Simpler)
```sql
-- Update the materialized view to include garment feedback columns
DROP MATERIALIZED VIEW user_feedback_current;
CREATE MATERIALIZED VIEW user_feedback_current AS
SELECT 
    ugf.user_garment_id,
    -- Body measurement feedback (existing)
    MAX(CASE WHEN ugf.dimension = 'overall' THEN fc.feedback_text END) as overall_feedback,
    MAX(CASE WHEN ugf.dimension = 'chest' THEN fc.feedback_text END) as chest_feedback,
    MAX(CASE WHEN ugf.dimension = 'neck' THEN fc.feedback_text END) as neck_feedback,
    MAX(CASE WHEN ugf.dimension = 'sleeve' THEN fc.feedback_text END) as sleeve_feedback,
    
    -- Garment measurement feedback (new)
    MAX(CASE WHEN ugf.dimension = 'garment_chest_width' THEN fc.feedback_text END) as garment_chest_width_feedback,
    MAX(CASE WHEN ugf.dimension = 'garment_shoulder_width' THEN fc.feedback_text END) as garment_shoulder_width_feedback,
    MAX(CASE WHEN ugf.dimension = 'garment_body_length' THEN fc.feedback_text END) as garment_body_length_feedback,
    MAX(CASE WHEN ugf.dimension = 'garment_sleeve_length' THEN fc.feedback_text END) as garment_sleeve_length_feedback,
    
    -- Keep the JSON for flexibility
    jsonb_object_agg(ugf.dimension, fc.feedback_text) as all_feedback
FROM user_garment_feedback ugf
JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
GROUP BY ugf.user_garment_id;
```

### Option B: Use JSON Only (More Flexible)
```sql
-- Just use the JSON field for everything
CREATE MATERIALIZED VIEW user_feedback_current AS
SELECT 
    ugf.user_garment_id,
    jsonb_object_agg(ugf.dimension, fc.feedback_text) as feedback_json
FROM user_garment_feedback ugf
JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
GROUP BY ugf.user_garment_id;

-- Query like this:
SELECT 
    feedback_json->>'chest' as body_chest_feedback,
    feedback_json->>'garment_chest_width' as garment_chest_feedback
FROM user_feedback_current;
```

## My Recommendation: Option A with both

Keep individual columns for common queries (faster) AND the JSON field for flexibility:
- Named columns for the most common feedback dimensions
- JSON field captures everything including future dimensions
- Best of both worlds

## Implementation Plan:

1. **Update feedback_codes table** to include garment-specific options:
   - "Measurement seems accurate"
   - "Measurement seems too small"
   - "Measurement seems too large"

2. **Update user_garment_feedback check constraint** to allow new dimensions:
   ```sql
   ALTER TABLE user_garment_feedback 
   DROP CONSTRAINT user_garment_feedback_dimension_check;
   
   ALTER TABLE user_garment_feedback 
   ADD CONSTRAINT user_garment_feedback_dimension_check 
   CHECK (dimension IN (
       'overall', 'chest', 'waist', 'sleeve', 'neck', 'hip', 'length',
       'garment_chest_width', 'garment_shoulder_width', 
       'garment_body_length', 'garment_sleeve_length'
   ));
   ```

3. **Rebuild materialized view** with new columns when ready

## Note on Multi-User Safety:
The current structure is already safe for multiple users because:
- Each user_garment record belongs to exactly one user
- user_garment_id is globally unique
- The materialized view doesn't need user_id because user_garment_id implies it

