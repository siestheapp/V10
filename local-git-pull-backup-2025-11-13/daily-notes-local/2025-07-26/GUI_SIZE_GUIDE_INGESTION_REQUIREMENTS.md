# GUI Size Guide Ingestion Requirements

## 📋 **Overview**
This document outlines the requirements for updating the admin GUI to support the complete 6-table size guide ingestion process that is currently only possible via terminal commands. The goal is to make the comprehensive data ingestion process accessible through a user-friendly web interface.

## 🎯 **Current State vs. Target State**

### **Current GUI Capabilities (Limited)**
- ✅ Basic brand creation
- ✅ Simple size guide metadata (brand, gender, category)
- ✅ Basic size entry form (chest, sleeve only)
- ✅ Raw size guide storage

### **Missing GUI Capabilities (Need to Add)**
- ❌ Dynamic measurement field selection (chest, waist, sleeve, neck, hip, center_back_length)
- ❌ Term standardization mapping interface
- ❌ Measurement instructions entry
- ❌ Measurement methodology tracking
- ❌ Data validation and completeness checking
- ❌ Preview and confirmation workflow

## 🗄️ **Database Tables Involved in Complete Ingestion**

### **Core Tables (Currently Supported)**
1. **`brands`** - Brand creation ✅
2. **`size_guides`** - Size guide metadata ✅  
3. **`size_guide_entries`** - Individual size measurements ✅ (limited)
4. **`raw_size_guides`** - Original source data ✅

### **Advanced Tables (Need GUI Support)**
5. **`standardization_log`** - Term mapping (original → standardized) ❌
6. **`measurement_methodology`** - Data provenance and quality tracking ❌

### **Optional Tables**
7. **`measurement_instructions`** - "How to measure" text (optional)

## 🔧 **Required GUI Enhancements**

### **1. Enhanced Size Entry Form**

#### **Dynamic Measurement Fields**
- **Current**: Fixed chest/sleeve fields
- **Required**: Dynamic selection of available measurements
- **UI**: Checkbox selection for: chest, waist, sleeve, neck, hip, center_back_length
- **Behavior**: Show/hide measurement input fields based on selection

#### **Flexible Value Input**
- **Current**: Min/max range inputs only
- **Required**: Support for single values, ranges, and text descriptions
- **Examples**: 
  - Single: `"34"` (chest measurement)
  - Range: `"34-36"` (chest range)
  - Text: `"14.5"` (collar size)

### **2. Term Standardization Interface**

#### **Automatic Detection**
- **Logic**: When user enters measurement labels, detect if they match standard terms
- **Standard Terms**: `chest`, `waist`, `sleeve`, `neck`, `hip`, `center_back_length`
- **Alert**: Flag non-standard terms for mapping

#### **Mapping Interface**
- **Trigger**: When non-standard terms detected (e.g., "collar", "bust")
- **UI**: Modal or section showing:
  ```
  Original Term: "collar" → Standardized Term: [dropdown: neck]
  Notes: [text area for explanation]
  ```
- **Auto-populate**: `standardization_log` table with mappings

### **3. Measurement Instructions Section**

#### **Optional Instructions Entry**
- **UI**: Expandable section "Add Measurement Instructions (Optional)"
- **Fields**: 
  - Original term (from brand)
  - Instruction text
  - Source URL
- **Example**:
  ```
  Chest: "Measure around the fullest part of your chest"
  Source: https://brand.com/size-guide
  ```

### **4. Data Quality & Methodology Tracking**

#### **Automatic Methodology Assignment**
- **Logic**: For each measurement entered, automatically create methodology entries
- **Default Values**:
  - `methodology_type`: "native" (from brand's size guide)
  - `measurement_confidence`: 1.0 (high confidence for direct entry)
  - `reliability_score`: 1.0 (high reliability for manual entry)
  - `source_methodology`: "Direct from [brand] size guide"

#### **Quality Indicators**
- **UI**: Show data completeness indicators during entry
- **Real-time**: Update completeness percentage as user fills form
- **Validation**: Prevent submission if core requirements not met

### **5. Enhanced Workflow Steps**

#### **Step 1: Brand & Metadata**
- Brand selection/creation ✅ (already exists)
- Gender, category, source URL ✅ (already exists)
- **Add**: Screenshot URL field
- **Add**: Fit type selection (Regular, Slim, Tall, NA)
- **Add**: Guide level (brand_level, category_level, product_level)

#### **Step 2: Measurement Configuration**
- **New**: Select which measurements are available
- **New**: Configure measurement labels (detect standardization needs)
- **New**: Set up term mappings if needed

#### **Step 3: Size Data Entry**
- **Enhanced**: Dynamic measurement fields based on Step 2
- **Enhanced**: Support for various input formats (single/range/text)
- **New**: Real-time validation

#### **Step 4: Instructions & Quality (Optional)**
- **New**: Add measurement instructions if available
- **New**: Review auto-generated methodology entries
- **New**: Adjust confidence/reliability scores if needed

#### **Step 5: Review & Submit**
- **New**: Complete data preview
- **New**: Completeness check (6-table validation)
- **New**: Confirmation with summary of what will be created

### **6. Validation & Error Handling**

#### **Real-time Validation**
- **Brand existence**: Check if brand already exists
- **Duplicate detection**: Prevent duplicate size guides
- **Data consistency**: Ensure measurement ranges make sense
- **Required fields**: Highlight missing required data

#### **Error Messages**
- **Clear feedback**: "Missing chest measurements for sizes M, L, XL"
- **Suggestions**: "Consider adding measurement instructions for better data quality"
- **Warnings**: "Non-standard term 'collar' detected - map to 'neck'?"

## 🎨 **UI/UX Considerations**

### **Progressive Disclosure**
- **Start Simple**: Basic brand/metadata entry
- **Expand Gradually**: Show advanced options as needed
- **Hide Complexity**: Don't overwhelm with all 6 tables at once

### **Visual Feedback**
- **Progress Indicators**: Show completion status
- **Color Coding**: Green for complete, yellow for optional, red for missing
- **Icons**: Use intuitive icons for different measurement types

### **Responsive Design**
- **Table Views**: Handle variable number of measurements
- **Mobile Friendly**: Ensure usability on different screen sizes
- **Keyboard Navigation**: Support tab navigation through forms

## 🔌 **Backend API Enhancements**

### **New Endpoints Needed**

#### **Validation Endpoints**
```python
GET /admin/api/validate-brand/<brand_name>
GET /admin/api/validate-measurements/<measurement_terms>
GET /admin/api/check-standardization/<brand_id>/<terms>
```

#### **Data Retrieval Endpoints**
```python
GET /admin/api/measurement-options  # Available measurement types
GET /admin/api/brand-completeness/<brand_id>  # Real-time completeness
GET /admin/api/size-guide-preview/<brand_id>  # Preview before submit
```

#### **Enhanced Upload Endpoint**
```python
POST /admin/size-guides/upload
# Enhanced to handle all 6 tables:
# - brands, size_guides, size_guide_entries, raw_size_guides
# - standardization_log, measurement_methodology
# - measurement_instructions (optional)
```

### **Database Transaction Handling**
- **Atomic Operations**: All 6 tables updated in single transaction
- **Rollback Support**: If any table fails, rollback all changes
- **Error Logging**: Detailed error messages for debugging

## 📊 **Integration with Existing Tools**

### **Brand Completeness Checker**
- **Real-time Integration**: Use completeness checker during GUI workflow
- **API Integration**: Call completeness checker via API
- **Visual Indicators**: Show completeness status in GUI

### **Existing Views**
- **Leverage**: Use existing database views for validation
- **Display**: Show brand_data_completeness results in GUI
- **Monitoring**: Use brand_missing_data for ongoing maintenance

## 🚀 **Implementation Phases**

### **Phase 1: Enhanced Form Fields**
- Dynamic measurement selection
- Flexible value input (single/range)
- Basic term standardization detection

### **Phase 2: Standardization Interface**
- Term mapping modal/interface
- Automatic standardization_log population
- Real-time validation feedback

### **Phase 3: Quality & Methodology**
- Automatic methodology entry creation
- Optional measurement instructions
- Data completeness indicators

### **Phase 4: Advanced Workflow**
- Multi-step wizard enhancement
- Preview and confirmation screens
- Integration with completeness checker

### **Phase 5: Polish & Testing**
- Error handling and validation
- UI/UX improvements
- Comprehensive testing with real data

## 📝 **Success Criteria**

### **Functional Requirements**
- ✅ Complete 6-table ingestion via GUI
- ✅ No terminal commands required for standard size guide ingestion
- ✅ All brands achieve 100% completeness via GUI
- ✅ Data quality equivalent to manual terminal entry

### **Usability Requirements**
- ✅ Non-technical users can complete full ingestion
- ✅ Clear error messages and guidance
- ✅ Intuitive workflow with minimal training
- ✅ Time to complete ingestion < 10 minutes per brand

### **Technical Requirements**
- ✅ Atomic database transactions
- ✅ Proper error handling and rollback
- ✅ Integration with existing completeness tracking
- ✅ Backward compatibility with existing GUI features

## 🔄 **Migration Strategy**

### **Backward Compatibility**
- **Existing GUI**: Continue to work for basic ingestion
- **Enhanced GUI**: New features optional, not required
- **Gradual Adoption**: Users can migrate to enhanced workflow over time

### **Data Migration**
- **No Migration Needed**: Existing data remains valid
- **Enhanced Features**: Available for new entries
- **Backfill Support**: Use existing completeness checker for old data

---

## 📞 **Next Steps**
1. **Review Requirements**: Validate requirements with stakeholders
2. **Technical Design**: Create detailed technical specifications
3. **UI Mockups**: Design user interface mockups
4. **Development Planning**: Break down into development tasks
5. **Implementation**: Begin with Phase 1 development 