# Test Scenarios for CBA Refund Processing System

This directory contains XML test files based on the CSV data to test different scenarios in the refund processing system.

## Test Scenarios

### 1. **Matched Nostro Scenario** ✅

- **Files**: `test_scenario_1_matched_nostro.xml` + `test_scenario_1_matched_nostro_pacs008.xml`
- **Customer**: Alice Smith (GB29NWBK60161331926819)
- **Amount**: USD 1,000.00
- **Return Reason**: AC01 (Invalid account)
- **Expected Flow**:
  - Pre-flow checks: All pass
  - FX loss: Within $300 limit
  - Nostro reconciliation: **MATCHED** (UETR: 123e4567-e89b-12d3-a456-426614174000)
  - Refund Decision: D1→D2→D3 (FCA refund)
  - **Result**: Refund processed to Alice Smith FCA USD account

### 2. **FCA Refund Scenario** ✅

- **Files**: `test_scenario_2_fca_refund.xml` + `test_scenario_2_fca_refund_pacs008.xml`
- **Customer**: Alice Smith (2002195062 - FCA USD account)
- **Original Amount**: USD 800.00 (PACS.008)
- **Returned Amount**: USD 750.00 (PACS.004)
- **FX Loss**: USD 50.00 → AUD ~$75 (within $300 limit)
- **Return Reason**: AC04 (Account closed)
- **Expected Flow**:
  - Pre-flow checks: All pass
  - FX loss: Within $300 limit
  - Nostro reconciliation: **MATCHED** (UETR: abc12345-e89b-12d3-a456-426614174abc)
  - Refund Decision: D1→D2→D3 (FCA refund)
  - **Result**: Refund processed to Alice Smith FCA USD account

### 3. **AUD Payment - Manual Review** ⚠️

- **Files**: `test_scenario_3_aud_payment.xml` + `test_scenario_3_aud_payment_pacs008.xml`
- **Customer**: Bob Lee (3003195062)
- **Amount**: AUD 1,500.00
- **Return Reason**: AC01 (Invalid account number)
- **Expected Flow**:
  - Pre-flow checks: **FAILS** at "Is AUD payment" check
  - **Result**: Manual review required (AUD payments need manual review)

### 4. **High FX Loss - Manual Review** ⚠️

- **Files**: `test_scenario_4_high_fx_loss.xml` + `test_scenario_4_high_fx_loss_pacs008.xml`
- **Customer**: Carol Tan (4004195062 - FCA EUR account)
- **Original Amount**: EUR 400.00 (PACS.008)
- **Returned Amount**: EUR 100.00 (PACS.004)
- **FX Loss**: EUR 300.00 → AUD ~$450 (exceeds $300 limit)
- **Return Reason**: AC01 (Account not found)
- **Expected Flow**:
  - Pre-flow checks: All pass
  - FX loss: **EXCEEDS $300 limit** (EUR 300 loss)
  - **Result**: Manual review required (FX loss exceeds threshold)

### 5. **Low FX Loss - Successful Refund** ✅

- **Files**: `test_scenario_6_low_fx_loss.xml` + `test_scenario_6_low_fx_loss_pacs008.xml`
- **Customer**: Alice Smith (GB29NWBK60161331926819)
- **Original Amount**: USD 200.00 (PACS.008)
- **Returned Amount**: USD 195.00 (PACS.004)
- **FX Loss**: USD 5.00 → AUD ~$7.50 (within $300 limit)
- **Return Reason**: AC01 (Invalid account)
- **Expected Flow**:
  - Pre-flow checks: All pass
  - FX loss: Within $300 limit
  - Nostro reconciliation: Not matched
  - Refund Decision: D1→D2→D7→D8 (OB fallback)
  - **Result**: Refund processed via Operating Bank fallback

### 6. **Unmatched Nostro - OB Fallback** ✅

- **Files**: `test_scenario_5_unmatched_nostro.xml` + `test_scenario_5_unmatched_nostro_pacs008.xml`
- **Customer**: David Ong (8008195062 - FCA SGD account)
- **Amount**: SGD 3,000.00
- **Return Reason**: AC01 (Account closed)
- **Expected Flow**:
  - Pre-flow checks: All pass
  - FX loss: Within $300 limit
  - Nostro reconciliation: **NOT MATCHED** (no corresponding entry)
  - Refund Decision: D1→D2→D7→D8 (OB fallback)
  - **Result**: Refund processed via Operating Bank fallback

### 7. **High FX Loss - No FCA Account - Pending 5 Days** ⏳

- **Files**: `test_scenario_7_high_fx_no_fca.xml` + `test_scenario_7_high_fx_no_fca_pacs008.xml`
- **Customer**: Alice Smith (GB29NWBK60161331926819 - regular USD account, no FCA)
- **Original Amount**: USD 500.00 (PACS.008)
- **Returned Amount**: USD 100.00 (PACS.004)
- **FX Loss**: USD 400.00 → AUD ~$600 (exceeds $300 limit)
- **Return Reason**: AC01 (Invalid account)
- **Expected Flow**:
  - Pre-flow checks: All pass
  - FX loss: **EXCEEDS $300 limit** (USD 400 loss)
  - FCA Account Check: **NOT FOUND** (customer has regular USD account but no FCA)
  - **Result**: Case submitted to pending for 5 business days (no manual review required)

### 8. **High FX Loss - With FCA Account - Proceed with Refund** ✅

- **Files**: `test_scenario_8_high_fx_with_fca.xml` + `test_scenario_8_high_fx_with_fca_pacs008.xml`
- **Customer**: Alice Smith (GB29NWBK60161331926819 - has FCA account GB29NWBK60161331926820)
- **Original Amount**: USD 600.00 (PACS.008)
- **Returned Amount**: USD 200.00 (PACS.004)
- **FX Loss**: USD 400.00 → AUD ~$600 (exceeds $300 limit)
- **Return Reason**: AC01 (Invalid account)
- **Expected Flow**:
  - Pre-flow checks: All pass
  - FX loss: **EXCEEDS $300 limit** (USD 400 loss)
  - FCA Account Check: **FOUND** (customer has FCA account)
  - Nostro reconciliation: **MATCHED** (UETR: UETR-HIGH-FX-WITH-FCA-001)
  - Refund Decision: D1→D2→D3 (FCA refund)
  - **Result**: Refund processed despite high FX loss (FCA account found)

## How to Test

1. **Start the web server**:

   ```bash
   python app/web.py
   ```

2. **Upload XML pairs**:

   - Go to http://localhost:5000
   - Upload both PACS.004 and PACS.008 files for each scenario
   - Click "Process Refund"

3. **Check Results**:
   - **Process Flowchart tab**: Shows decision path through flow*.md and refund_flow*.md
   - **Account Operations tab**: Shows balance changes and money flow
   - **Transaction Timeline tab**: Shows chronological processing events
   - **Communication tab**: Shows generated notifications

## Expected Outcomes

### ✅ **Successful Refunds** (Scenarios 1, 2, 5, 6):

- Account balances update persistently in CSV files
- Transaction history recorded in `data/transaction_history.csv`
- Customer and branch notifications generated
- Complete audit trail maintained

### ⚠️ **Manual Review Cases** (Scenarios 3, 4):

- Processing stops at pre-flow checks or FX validation
- Manual review case created with detailed reasons
- No account operations performed
- Review case logged for human intervention

### ⏳ **Pending Cases** (Scenario 7):

- FX loss exceeds $300 limit but no FCA account found
- Case automatically submitted to pending for 5 business days
- No manual review required - automatic processing after pending period
- Pending date calculated excluding weekends

## CSV Data Integration

All scenarios use real customer and account data from:

- `data/customer_data.csv` - Customer account information
- `data/bank_accounts.csv` - Bank account details and balances
- `data/nostro_statement.csv` - Nostro reconciliation data

## Balance Persistence

After processing successful refunds:

- Check `data/bank_accounts.csv` for updated balances
- Check `data/transaction_history.csv` for complete audit trail
- Balances persist across multiple runs

## Testing the Enhanced UI

The new UI features to test:

1. **Process Flowchart**: Visual flow through both flow*.md and refund_flow*.md
2. **Balance Comparison Table**: Before/after balances with net changes
3. **Money Flow Visualization**: Account-to-account transfer display
4. **Transaction Timeline**: Chronological event tracking
5. **Enhanced Account Operations**: Detailed debit/credit operations

Each scenario tests different decision paths and routing logic in the refund processing system.
