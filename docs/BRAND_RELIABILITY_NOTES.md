# Brand Reliability Notes

This document tracks known issues with brand-specific measurement reliability due to care instruction factors.

## NN.07 Care Instruction Issue

**Problem**: NN.07 garments have "Do Not Tumble Dry" care instructions that most users ignore for basic items like long sleeve shirts.

**Impact on Measurements**:
- Material: 50% Cotton + 50% TENCEL™ Modal  
- Cotton component shrinks 3-5% with repeated tumble drying
- TENCEL Modal stiffens when heat-damaged
- Users likely to ignore care instructions for "everyday" items

**Data Reliability Impact**:
- **"Tight" feedback becomes unreliable** after improper care
- Original good-fitting garments (41" chest) appear as "tight" after shrinkage
- Corrupts fit zone calculations by creating false tight measurements

**Recommendation**: 
- Reduce confidence weight for "Tight" ratings from NN.07 garments
- Consider flagging NN.07 tight ratings with warning about care sensitivity
- Document user behavior assumption: basic cotton blend items will be tumble dried regardless of instructions

## General Brand Care Sensitivity Guidelines

### High Care Sensitivity (reduce tight feedback confidence):
- **NN.07**: Cotton blends with anti-tumble dry instructions
- **[Add other brands as discovered]**

### Care Assumption Rules:
1. **Basic items** (t-shirts, casual long sleeves): Users will tumble dry regardless of instructions
2. **Formal items** (dress shirts, suits): Users more likely to follow care instructions  
3. **Cotton/cotton blends**: High shrinkage risk with improper care
4. **Synthetic blends**: Generally more stable but can still be affected

### Implementation Notes:
- Consider adding "garment condition" field to feedback forms
- "How did this fit when new?" vs "How does this fit now?"
- Track garment age for reliability weighting
- Flag measurements that appear in multiple fit categories as potentially corrupted

## System Integration

The confidence weighting system should account for:

```python
def _get_care_adjusted_confidence(self, feedback: str, brand_name: str, garment_type: str) -> float:
    """Adjust confidence based on known care instruction issues"""
    base_confidence = self._get_confidence_weight(feedback)
    
    # Reduce confidence for tight ratings from care-sensitive brands
    if feedback in ['Tight but I Like It', 'Too Tight'] and brand_name == 'NN.07':
        if garment_type in ['basic_shirt', 'casual_top']:
            base_confidence *= 0.5  # 50% confidence reduction
    
    return base_confidence
```

## Future Improvements

1. **Brand-specific care flags** in database
2. **User behavior modeling** (likelihood of following care instructions by garment type)
3. **Garment condition tracking** (new vs aged measurements)  
4. **Material composition analysis** (shrinkage risk by fabric blend) 