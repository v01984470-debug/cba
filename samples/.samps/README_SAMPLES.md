# Sample PACS Files - Multiple Return Reason Codes

This directory contains sample PACS.004 (return) and PACS.008 (original payment) files with various return reason codes and FX loss scenarios.

## 📁 Available Sample Files

### **Original Sample (AC01)**

- **pacs004.xml** - EUR 970.00 return with AC01 (Incorrect Account Number)
- **pacs008.xml** - EUR 1000.00 original payment
- **FX Loss**: EUR 30.00 (1,000 - 970)

### **Return Reason Code Samples**

#### **AC01 - Incorrect Account Number**

- **pacs004_ac01.xml** - USD 2475.00 return with AC01
- **pacs008_ac01.xml** - USD 2500.00 original payment
- **Scenario**: US Corporation to European Supplier
- **FX Loss**: USD 25.00 (2,500 - 2,475)
- **UETR**: a1b2c3d4-5e6f-7g8h-9i0j-k1l2m3n4o5p6

#### **AC04 - Account Closed**

- **pacs004_ac04.xml** - GBP 1485.00 return with AC04
- **pacs008_ac04.xml** - GBP 1500.00 original payment
- **Scenario**: UK Trading Company to German Manufacturing
- **FX Loss**: GBP 15.00 (1,500 - 1,485)
- **UETR**: b2c3d4e5-6f7g-8h9i-0j1k-l2m3n4o5p6q7

#### **MS03 - Reason Not Specified**

- **pacs004_ms03.xml** - JPY 495000.00 return with MS03
- **pacs008_ms03.xml** - JPY 500000.00 original payment
- **Scenario**: Japan Electronics to European Distributor
- **FX Loss**: JPY 5,000.00 (500,000 - 495,000)
- **UETR**: c3d4e5f6-7g8h-9i0j-1k2l-m3n4o5p6q7r8

#### **CURR - Wrong Currency**

- **pacs004_curr.xml** - CHF 485.00 return with CURR
- **pacs008_curr.xml** - CHF 500.00 original payment
- **Scenario**: Swiss Trading to European Importer
- **FX Loss**: CHF 15.00 (500 - 485)
- **UETR**: d4e5f6g7-8h9i-0j1k-2l3m-n4o5p6q7r8s9

## 🔍 Return Reason Code Details

### **AC01 - Incorrect Account Number**

- **Description**: The account number specified in the payment is incorrect
- **Auto-Refund**: ✅ Eligible
- **Action**: Seek alternate active account

### **AC04 - Account Closed**

- **Description**: The destination account is closed
- **Auto-Refund**: ✅ Eligible
- **Action**: Seek alternate active account

### **MS03 - Reason Not Specified**

- **Description**: Return reason not specified by the beneficiary bank
- **Auto-Refund**: ❌ Not eligible (requires manual review)
- **Action**: Manual review required

### **CURR - Wrong Currency**

- **Description**: Payment was made in wrong currency (currency mismatch detected)
- **Auto-Refund**: ❌ Not eligible (requires manual review)
- **Action**: Manual review required due to currency mismatch

## 💡 Usage Instructions

### **Testing Different Scenarios**

1. **AC01/AC04**: Test auto-refund with alternate account logic
2. **MS03**: Test manual review requirement
3. **CURR**: Test currency correction processing
4. **FX Loss**: Test FX loss calculations with different currencies

### **File Pairing**

- `pacs004.xml` ↔ `pacs008.xml` (EUR, AC01)
- `pacs004_ac01.xml` ↔ `pacs008_ac01.xml` (USD, AC01)
- `pacs004_ac04.xml` ↔ `pacs008_ac04.xml` (GBP, AC04)
- `pacs004_ms03.xml` ↔ `pacs008_ms03.xml` (JPY, MS03)
- `pacs004_curr.xml` ↔ `pacs008_curr.xml` (CHF→EUR, CURR)

## 🎯 Testing Benefits

### **Multi-Currency Testing**

- **EUR**: Original sample (30.00 FX loss)
- **USD**: AC01 sample (25.00 FX loss)
- **GBP**: AC04 sample (15.00 FX loss)
- **JPY**: MS03 sample (5,000.00 FX loss)
- **CHF→EUR**: CURR sample (currency mismatch, 88.48 FX loss)

### **Different Return Reasons**

- **Auto-Refund Eligible**: AC01, AC04
- **Manual Review Required**: MS03, CURR
- **Various FX Loss Amounts**: From 15.00 to 5,000.00

### **Different Bank Scenarios**

- **US Banks**: CHASUS33XXX (JP Morgan Chase)
- **UK Banks**: BARCGB22XXX (Barclays)
- **Japanese Banks**: SMBCJPJTXXX (Sumitomo Mitsui)
- **Swiss Banks**: UBSWCHZHXXX (UBS)
- **European Banks**: BANKAADEFF (Deutsche Bank)

## 📊 Expected Processing Results

### **AC01/AC04 Processing**

- ✅ **Auto-Refund Eligible**: Yes
- ✅ **Alternate Account**: Required
- ✅ **Enhanced Processing**: Complete 8-step flow
- ✅ **FX Loss Calculation**: Accurate conversion to AUD

### **MS03 Processing**

- ❌ **Auto-Refund Eligible**: No (manual review required)
- ✅ **Manual Review**: Required
- ✅ **FX Loss Calculation**: Still calculated for reference

### **CURR Processing**

- ✅ **Auto-Refund Eligible**: Yes
- ✅ **Currency Correction**: Process with correct currency
- ✅ **Enhanced Processing**: Complete 8-step flow

## 🚀 Quick Start

1. **Start the application**:

   ```cmd
   start.bat
   ```

2. **Upload sample files**:

   - Choose any PACS.004 and PACS.008 pair
   - Upload customers.csv
   - Click "Run Investigation"

3. **Analyze results**:
   - Review eligibility assessment
   - Check enhanced refund processing
   - Examine agent flow diagram
   - Click on audit trail agents for details

## 📈 FX Loss Examples

### **EUR Sample (Original)**

- Original: EUR 1,000.00
- Returned: EUR 970.00
- FX Loss: EUR 30.00
- AUD Equivalent: ~AUD 50.00 (within limit)

### **USD Sample (AC01)**

- Original: USD 2,500.00
- Returned: USD 2,475.00
- FX Loss: USD 25.00
- AUD Equivalent: ~AUD 40.00 (within limit)

### **GBP Sample (AC04)**

- Original: GBP 1,500.00
- Returned: GBP 1,485.00
- FX Loss: GBP 15.00
- AUD Equivalent: ~AUD 30.00 (within limit)

### **JPY Sample (MS03)**

- Original: JPY 500,000.00
- Returned: JPY 495,000.00
- FX Loss: JPY 5,000.00
- AUD Equivalent: ~AUD 50.00 (within limit)

### **CHF Sample (CURR)**

- Original: CHF 500.00
- Returned: CHF 485.00
- FX Loss: CHF 15.00
- AUD Equivalent: ~AUD 25.00 (within limit)

---

**Ready to test multiple return reason codes with FX loss scenarios? Choose your sample files and start investigating!** 🎉
