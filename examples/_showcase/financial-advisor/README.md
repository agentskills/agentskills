# Financial Advisor Workflow Management

A comprehensive showcase demonstrating the composable skills architecture for **regulated financial advisory practices**. This example shows how complex compliance-driven workflows can be modularised into reusable, testable components.

## Why Financial Advisory?

Financial advisory workflows are ideal for demonstrating composable skills because they require:

- **Strict compliance**: Every action must be documented and auditable
- **Multi-step processes**: Onboarding, advice delivery, and reviews span days/weeks
- **State management**: Workflows pause for client input, approvals, signatures
- **Conditional branching**: Different paths based on risk profile, client tier, advice type
- **Document generation**: FSG, SOA, risk profiles, fee disclosures
- **Regulatory triggers**: Best interests duty, KYC/AML, professional development

## Architecture Overview

```
Level 3: WORKFLOWS (Multi-day, stateful processes)
├── client-onboard ──────── Discovery → KYC → Strategy → Signatures
├── advice-delivery ─────── Analysis → SOA → Approval → Execution
├── annual-review ───────── Pre-review → Meeting → Post-review
├── portfolio-rebalance ─── Monitor → Trigger → Approve → Execute
└── compliance-audit ────── Collect → Verify → Report → Remediate

Level 2: COMPOSITE (Multi-step operations)
├── risk-profile-assess ─── Questionnaire → Scoring → Classification
├── soa-prepare ─────────── Analysis → Drafting → Compliance check
├── portfolio-analyse ───── Holdings → Performance → Attribution
├── portfolio-construct ─── Objectives → Allocation → Selection
├── best-interests-verify ─ Loyalty → Care → Good faith checks
└── fee-disclosure-prepare ─ Fees → Conflicts → Statement

Level 1: ATOMIC (Single operations)
├── client-data-read ────── CRM/database lookup
├── client-data-update ──── CRM/database write
├── document-generate ───── Template → PDF/DOCX
├── compliance-check ────── Rule verification
├── portfolio-read ──────── Holdings and values
├── meeting-schedule ────── Calendar booking
├── kyc-verify ──────────── Identity/AML checks
└── trade-execute ───────── Order placement
```

## Compliance Features

Each skill includes:

1. **Audit logging**: Every action recorded with timestamp, user, rationale
2. **State persistence**: Workflows can pause and resume across sessions
3. **Approval gates**: Certain actions require supervisor sign-off
4. **Document retention**: All generated documents archived per regulations
5. **Compliance flags**: Best interests duty verified at each advice point

## Regulatory Context

These skills are designed for Australian financial advisory regulations (ASIC):

- **Best Interests Duty** (s961B Corporations Act)
- **Financial Services Guide** (FSG) requirements
- **Statement of Advice** (SOA) requirements
- **Know Your Client** (KYC) / AML-CTF obligations
- **Ongoing Fee Arrangement** (OFA) consent
- **Professional Standards** (FASEA Code of Ethics)

The architecture can be adapted for other jurisdictions (UK FCA, US SEC/FINRA, etc.).

## Skill Categories

### Client Lifecycle
- `client-onboard`: Full onboarding workflow (discovery → signatures)
- `annual-review`: Scheduled review process
- `client-offboard`: Termination and record archival

### Advice Delivery
- `advice-delivery`: End-to-end advice process
- `soa-prepare`: Statement of Advice generation
- `best-interests-verify`: Regulatory compliance verification

### Portfolio Management
- `portfolio-construct`: Build portfolio from objectives
- `portfolio-rebalance`: Monitor and rebalance workflow
- `portfolio-analyse`: Performance and attribution

### Compliance
- `compliance-audit`: Periodic compliance review
- `kyc-verify`: Identity and AML verification
- `fee-disclosure-prepare`: Fee transparency statements

## Tool Discovery

Financial advisors use various platforms. These skills discover and adapt:

```yaml
tool_discovery:
  crm:
    prefer: [xplan-client, iress-client, salesforce-client]
  portfolio:
    prefer: [xplan-portfolio, iress-portfolio, praemium-portfolio]
  documents:
    prefer: [xplan-docgen, templafy-generate, docusign-generate]
  compliance:
    prefer: [xplan-compliance, iress-compliance, custom-compliance]
  trading:
    prefer: [hub24-trade, netwealth-trade, praemium-trade]
```

## Usage Examples

```
# Start client onboarding
"Begin onboarding for John Smith, discovered via referral"

# Prepare advice
"Prepare SOA for client 12345 recommending superannuation consolidation"

# Run annual review
"Conduct annual review for the Henderson family"

# Check portfolio
"Analyse portfolio drift for all clients, flag those needing rebalance"

# Compliance check
"Run quarterly compliance audit for adviser Jane Doe"
```

## State Machine Example

The `client-onboard` workflow demonstrates state management:

```
┌─────────────────┐
│  DISCOVERY      │ ← Initial meeting, provide FSG
└────────┬────────┘
         │ FSG acknowledged
         ▼
┌─────────────────┐
│  QUESTIONNAIRE  │ ← Send within 24h, await response
└────────┬────────┘
         │ Questionnaire completed
         ▼
┌─────────────────┐
│  KYC_PENDING    │ ← Identity verification
└────────┬────────┘
         │ KYC passed
         ▼
┌─────────────────┐
│  STRATEGY       │ ← Internal team review
└────────┬────────┘
         │ Strategy approved
         ▼
┌─────────────────┐
│  PRESENTATION   │ ← Formal onboarding meeting
└────────┬────────┘
         │ Client accepts
         ▼
┌─────────────────┐
│  DOCUMENTATION  │ ← Collect signatures, archive
└────────┬────────┘
         │ All docs signed
         ▼
┌─────────────────┐
│  ACTIVE         │ ← Client fully onboarded
└─────────────────┘
```

## Testing

Each skill can be tested independently:

```bash
# Validate all financial advisor skills
skills-ref validate examples/_showcase/financial-advisor/

# Test specific workflow
skills-ref validate examples/_showcase/financial-advisor/_workflows/client-onboard/

# Generate prompt for testing
skills-ref to-prompt examples/_showcase/financial-advisor/_workflows/advice-delivery/
```

## Extending

To add a new jurisdiction or regulatory framework:

1. Create jurisdiction-specific compliance checks
2. Update document templates for local requirements
3. Adjust workflow triggers for regulatory deadlines
4. Map to local platform integrations

The modular architecture means core workflows remain unchanged; only compliance and document skills need jurisdiction-specific variants.
