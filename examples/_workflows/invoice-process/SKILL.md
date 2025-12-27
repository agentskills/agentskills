---
name: invoice-process
description: |
  Process incoming invoices: extract data via OCR/AI, match to purchase orders,
  validate against contracts, route for approval based on amount/vendor,
  and create accounting entries.
level: 3
operation: WRITE
license: Apache-2.0
composes:
  - email-attachment-read
  - document-parse
  - po-lookup
  - vendor-lookup
  - accounting-entry-create
  - approval-request
  - slack-message-send
tool_discovery:
  document_source:
    prefer: [email-attachment-read, drive-file-read, dropbox-read]
  ocr_extraction:
    prefer: [document-ai-parse, textract-parse, azure-form-recognizer]
    fallback: vision-extract
  accounting:
    prefer: [xero-entry-create, quickbooks-entry-create, netsuite-entry-create]
  approval:
    prefer: [slack-approval-request, email-approval-request]
---

# Invoice Process

Automated invoice processing with extraction, validation, and routing.

## Trigger Phrases

- "Process this invoice"
- "Handle invoice from [vendor]"
- "New invoice in email, please process"
- Auto-trigger: Invoice email received

## Workflow Steps

```
1. INGEST: Receive invoice document
       │
       ├── Email attachment
       ├── Shared drive upload
       └── Direct upload
       │
       ▼
2. EXTRACT: Parse invoice data (AI/OCR)
       │
       ├── Vendor name and address
       ├── Invoice number and date
       ├── Line items with amounts
       ├── Tax and totals
       ├── Payment terms
       └── Bank details
       │
       ▼
3. VALIDATE: Check extracted data
       │
       ├── Required fields present
       ├── Amounts calculate correctly
       ├── Valid date ranges
       └── Currency detection
       │
       ▼
4. MATCH: Find related records
       │
       ├── Purchase order (if referenced)
       ├── Vendor in system
       ├── Contract terms
       └── Previous invoices (duplicate check)
       │
       ▼
5. VERIFY: Business rule checks
       │
       ├── Amount vs PO (within tolerance)
       ├── Vendor approved status
       ├── Budget availability
       └── Contract compliance
       │
       ▼
6. ROUTE: Determine approval path
       │
       ├── [< $500] → Auto-approve if PO match
       ├── [$500-$5000] → Manager approval
       ├── [$5000+] → Finance director
       ├── [New vendor] → Procurement review
       └── [Variance > 10%] → Exception handling
       │
       ▼
7. APPROVE: Request/process approval
       │
       ├── Slack approval workflow
       ├── Email approval request
       └── Pending queue for manual
       │
       ▼
8. BOOK: Create accounting entry
       │
       ├── General ledger entry
       ├── Accounts payable
       └── Cost centre allocation
       │
       ▼
9. RETURN: Processing summary
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source` | string | Yes | Invoice source (email ID, file path, URL) |
| `auto_approve_threshold` | number | No | Amount for auto-approval (default: $500) |
| `require_po_match` | boolean | No | Require PO for processing (default: true) |
| `notify_on_complete` | boolean | No | Notify when processed (default: true) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `invoice` | object | Extracted invoice data |
| `vendor` | object | Vendor details and status |
| `matching` | object | PO match, contract details |
| `validation` | object | Validation results |
| `approval` | object | Approval status and routing |
| `accounting` | object | Created entries |
| `actions_taken` | object[] | Processing steps completed |

## Usage

```
Process the invoice attached to email from accounts@vendor.com
```

```
Handle new invoice from Acme Corp, check against PO-2024-0456
```

```
Process all invoices in the pending folder
```

## Example Response

```json
{
  "invoice": {
    "vendor": "Acme Software Inc",
    "invoice_number": "INV-2024-1234",
    "date": "2024-12-20",
    "due_date": "2025-01-19",
    "currency": "USD",
    "line_items": [
      {
        "description": "Annual SaaS License",
        "quantity": 50,
        "unit_price": 99.00,
        "amount": 4950.00
      },
      {
        "description": "Premium Support",
        "quantity": 1,
        "unit_price": 500.00,
        "amount": 500.00
      }
    ],
    "subtotal": 5450.00,
    "tax": 545.00,
    "total": 5995.00,
    "payment_terms": "Net 30"
  },
  "vendor": {
    "id": "V-001234",
    "name": "Acme Software Inc",
    "status": "approved",
    "payment_method": "ACH",
    "contract_end": "2025-06-30"
  },
  "matching": {
    "po_number": "PO-2024-0456",
    "po_amount": 6000.00,
    "variance": -0.08,
    "variance_status": "within_tolerance",
    "contract_id": "C-2024-089"
  },
  "validation": {
    "passed": true,
    "checks": [
      {"check": "required_fields", "status": "pass"},
      {"check": "amount_calculation", "status": "pass"},
      {"check": "duplicate_check", "status": "pass"},
      {"check": "po_match", "status": "pass"},
      {"check": "budget_available", "status": "pass"}
    ]
  },
  "approval": {
    "required": true,
    "reason": "Amount exceeds $5000",
    "approver": "finance-director",
    "status": "pending",
    "request_sent": true,
    "request_url": "https://slack.com/approval/xyz"
  },
  "accounting": {
    "status": "pending_approval",
    "draft_entry": {
      "debit": {"account": "6200-Software", "amount": 5995.00},
      "credit": {"account": "2100-AP", "amount": 5995.00}
    }
  },
  "actions_taken": [
    {"action": "extracted", "result": "14 fields parsed"},
    {"action": "validated", "result": "all checks passed"},
    {"action": "matched_po", "result": "PO-2024-0456, 8% under"},
    {"action": "routed", "result": "finance-director approval"},
    {"action": "notified", "result": "Slack request sent"}
  ]
}
```

## Extraction Fields

| Field | Confidence | Validation |
|-------|------------|------------|
| Vendor name | High | Match against vendor list |
| Invoice number | High | Uniqueness check |
| Amounts | High | Line items sum to total |
| Dates | Medium | Reasonable range check |
| Bank details | Medium | Format validation |

## Approval Thresholds

| Amount | Approval Required |
|--------|-------------------|
| < $500 | Auto-approve (if PO match) |
| $500 - $2,000 | Team lead |
| $2,000 - $5,000 | Manager |
| $5,000 - $25,000 | Finance director |
| > $25,000 | CFO |

## Why Level 3

This workflow demonstrates:
1. **Document AI**: OCR + structured extraction
2. **Multi-system matching**: PO, vendor, contract lookup
3. **Business rules engine**: Validation and routing
4. **Approval workflows**: Human-in-the-loop for thresholds
5. **Accounting integration**: Creates proper journal entries
6. **Exception handling**: Routes anomalies for review

## Composition Graph

```
invoice-process (L3)
    │
    ├─── email-attachment-read (L1) ► Get document
    │
    ├─── document-parse (L2) ────────► Extract fields
    │    [Tool Discovery: Document AI|Textract|Azure]
    │         │
    │         └── [OCR + AI extraction]
    │
    ├──► [Validate]
    │     • Required fields
    │     • Calculations
    │     • Duplicates
    │
    ├─┬─ [Match - Parallel]
    │ │
    │ ├── po-lookup (L1) ──────────► Purchase order
    │ ├── vendor-lookup (L1) ──────► Vendor status
    │ └── contract-lookup (L1) ────► Contract terms
    │
    ├──► [Route]
    │     • Apply approval rules
    │     • Determine approver
    │
    ├─── approval-request (L1) ────► Request approval
    │    [Tool Discovery: Slack|Email]
    │
    └─── accounting-entry-create (L1)
         [Tool Discovery: Xero|QuickBooks|NetSuite]
```

## Notes

- Never auto-pays without approval workflow
- Duplicate invoices are flagged, not rejected
- Partial PO matches route to procurement
- Stores original document with extracted data
- Audit trail of all processing steps
