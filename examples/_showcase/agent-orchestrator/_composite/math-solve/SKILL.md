# math-solve

Parse natural language math problems, generate Python code, execute, and return auditable results.

## Description

This skill provides end-to-end strict math problem solving:

1. **Parse** - Understand the natural language math problem
2. **Generate** - Create Python code to solve it
3. **Execute** - Run the code via `math-execute`
4. **Validate** - Check result reasonableness
5. **Audit** - Return full trace for verification

## CRITICAL RULES

**This skill MUST be invoked for ANY math calculation request.**

When a user asks:
- "What is 25 times 47?"
- "Calculate the compound interest..."
- "If I have 3 apples and buy 5 more..."
- "What's the average of these numbers?"

The LLM MUST use this skill. NEVER attempt mental math.

**Detection triggers:**
- Numbers with operations (+, -, *, /, ^, %)
- Words: calculate, compute, what is, how much, total, sum, average, etc.
- Financial: interest, payment, amortization, ROI
- Statistical: mean, median, standard deviation, correlation

## Metadata

```yaml
domain: math
level: 2
type: composite
version: 1.0.0
operation: TRANSFORM
tags:
  - math
  - calculation
  - python
  - audit
  - nlp
  - strict
```

## Composes

- `math-execute` - Executes the generated Python code

## Input Schema

```yaml
inputSchema:
  type: object
  required:
    - problem
  properties:
    problem:
      type: string
      description: |
        Natural language description of the math problem.
        Can be a question, calculation request, or word problem.
      examples:
        - "What is 25 times 47?"
        - "Calculate 15% tip on $85.50"
        - "If I invest $10,000 at 5% annual interest for 10 years, what's the final amount?"
        - "What's the average of 23, 45, 67, and 89?"
    context:
      type: object
      description: Additional context or variable values
      additionalProperties: true
      examples:
        - { "tax_rate": 0.08, "currency": "USD" }
    precision:
      type: integer
      description: Decimal places for floating point results
      default: 2
    show_steps:
      type: boolean
      description: Include step-by-step breakdown in response
      default: true
    verify:
      type: boolean
      description: Perform sanity checks on result
      default: true
```

## Output Schema

```yaml
outputSchema:
  type: object
  required:
    - success
    - answer
    - python_code
    - execution_result
  properties:
    success:
      type: boolean
      description: Whether the problem was solved successfully
    answer:
      type: string
      description: Human-readable answer to the problem
    answer_value:
      type: any
      description: The numerical/computed result
    python_code:
      type: string
      description: |
        Complete Python code generated to solve the problem.
        THIS IS THE AUDIT TRAIL - users can verify by running this code.
    execution_result:
      type: object
      description: Full output from math-execute skill
    problem_analysis:
      type: object
      description: How the problem was interpreted
      properties:
        problem_type:
          type: string
          enum:
            - arithmetic
            - percentage
            - financial
            - statistical
            - algebraic
            - geometric
            - word_problem
            - conversion
        identified_values:
          type: object
          description: Numbers and variables extracted from problem
        formula_used:
          type: string
          description: Mathematical formula or approach used
    steps:
      type: array
      description: Step-by-step breakdown (if show_steps=true)
      items:
        type: object
        properties:
          step_number:
            type: integer
          description:
            type: string
          calculation:
            type: string
          result:
            type: any
    validation:
      type: object
      description: Sanity checks performed (if verify=true)
      properties:
        checks_passed:
          type: array
          items:
            type: string
        warnings:
          type: array
          items:
            type: string
    error:
      type: object
      description: Error details if success is false
```

## Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         math-solve                               │
├─────────────────────────────────────────────────────────────────┤
│  1. PARSE: Analyze natural language problem                     │
│     ├─ Extract numbers, operations, variables                  │
│     ├─ Identify problem type (arithmetic, financial, etc.)     │
│     └─ Map to mathematical formula                              │
│                                                                  │
│  2. GENERATE: Create Python code                                │
│     ├─ Import required modules (math, statistics, decimal)     │
│     ├─ Define variables from extracted values                  │
│     ├─ Implement formula as Python expression                  │
│     └─ Add comments for clarity                                 │
│                                                                  │
│  3. EXECUTE: Call math-execute                                  │
│     ├─ Pass generated code                                      │
│     ├─ Set precision and safety options                        │
│     └─ Capture full execution trace                             │
│                                                                  │
│  4. VALIDATE: Check result (if verify=true)                    │
│     ├─ Reasonableness checks (not negative when shouldn't be) │
│     ├─ Magnitude checks (result in expected range)             │
│     └─ Type checks (integer vs float as expected)              │
│                                                                  │
│  5. FORMAT: Build response                                      │
│     ├─ Human-readable answer                                    │
│     ├─ Include Python code (audit trail)                       │
│     ├─ Add steps if requested                                   │
│     └─ Include validation results                               │
└─────────────────────────────────────────────────────────────────┘
```

## Problem Type Patterns

### Arithmetic
```yaml
triggers:
  - "what is X + Y"
  - "calculate X * Y"
  - "X divided by Y"
  - "X to the power of Y"

code_template: |
  result = {expression}
```

### Percentage
```yaml
triggers:
  - "X% of Y"
  - "what percentage is X of Y"
  - "increase/decrease by X%"
  - "X% tip on Y"

code_template: |
  # Percentage calculation
  value = {value}
  percentage = {percentage}
  result = value * (percentage / 100)
```

### Financial
```yaml
triggers:
  - "compound interest"
  - "loan payment"
  - "ROI"
  - "amortization"

code_template: |
  from decimal import Decimal

  principal = Decimal('{principal}')
  rate = Decimal('{rate}')
  time = {time}

  # Compound interest formula: A = P(1 + r)^t
  result = float(principal * (1 + rate) ** time)
```

### Statistical
```yaml
triggers:
  - "average/mean of"
  - "median of"
  - "standard deviation"
  - "sum of"

code_template: |
  import statistics

  data = {data}
  result = {{
      'mean': statistics.mean(data),
      'median': statistics.median(data),
      'stdev': statistics.stdev(data) if len(data) > 1 else 0,
      'sum': sum(data),
      'count': len(data)
  }}
```

## Examples

### Simple Multiplication
```yaml
input:
  problem: "What is 25 times 47?"

output:
  success: true
  answer: "25 × 47 = 1,175"
  answer_value: 1175
  python_code: |
    # Calculate: 25 times 47
    a = 25
    b = 47
    result = a * b
  execution_result:
    success: true
    result: 1175
    result_type: "int"
    code_executed: "a = 25\nb = 47\nresult = a * b"
    execution_time_ms: 0.012
  problem_analysis:
    problem_type: "arithmetic"
    identified_values:
      a: 25
      b: 47
    formula_used: "a × b"
  steps:
    - step_number: 1
      description: "Multiply 25 by 47"
      calculation: "25 × 47"
      result: 1175
  validation:
    checks_passed:
      - "Result is positive (expected for positive inputs)"
      - "Result magnitude reasonable (between 1000-1500)"
```

### Percentage Calculation
```yaml
input:
  problem: "Calculate 15% tip on $85.50"
  precision: 2

output:
  success: true
  answer: "15% tip on $85.50 = $12.83"
  answer_value: 12.83
  python_code: |
    # Calculate: 15% tip on $85.50
    from decimal import Decimal, ROUND_HALF_UP

    bill_amount = Decimal('85.50')
    tip_percentage = Decimal('15')

    # Tip = bill × (percentage / 100)
    tip = bill_amount * (tip_percentage / 100)
    result = float(tip.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
  execution_result:
    success: true
    result: 12.83
    result_type: "float"
    code_executed: "..."
    execution_time_ms: 0.034
  problem_analysis:
    problem_type: "percentage"
    identified_values:
      bill_amount: 85.50
      tip_percentage: 15
    formula_used: "tip = bill × (percentage ÷ 100)"
  steps:
    - step_number: 1
      description: "Convert percentage to decimal"
      calculation: "15 ÷ 100 = 0.15"
      result: 0.15
    - step_number: 2
      description: "Multiply bill by decimal"
      calculation: "85.50 × 0.15"
      result: 12.825
    - step_number: 3
      description: "Round to cents"
      calculation: "round(12.825, 2)"
      result: 12.83
  validation:
    checks_passed:
      - "Tip is positive"
      - "Tip is less than bill amount"
      - "Tip percentage matches expected (12.83/85.50 ≈ 15%)"
```

### Compound Interest
```yaml
input:
  problem: "If I invest $10,000 at 5% annual interest compounded yearly for 10 years, what's the final amount?"
  precision: 2

output:
  success: true
  answer: "After 10 years at 5% compound interest, $10,000 grows to $16,288.95"
  answer_value: 16288.95
  python_code: |
    # Compound Interest Calculation
    # Formula: A = P(1 + r)^t
    # Where: P = principal, r = annual rate, t = time in years

    from decimal import Decimal

    principal = Decimal('10000.00')
    annual_rate = Decimal('0.05')  # 5%
    years = 10

    # Calculate compound interest
    final_amount = principal * (1 + annual_rate) ** years
    result = float(final_amount.quantize(Decimal('0.01')))
  execution_result:
    success: true
    result: 16288.95
    result_type: "float"
    code_executed: "..."
    execution_time_ms: 0.089
  problem_analysis:
    problem_type: "financial"
    identified_values:
      principal: 10000
      rate: 0.05
      years: 10
    formula_used: "A = P(1 + r)^t"
  steps:
    - step_number: 1
      description: "Convert rate to decimal"
      calculation: "5% = 0.05"
      result: 0.05
    - step_number: 2
      description: "Calculate growth factor"
      calculation: "(1 + 0.05)^10"
      result: 1.6288946268
    - step_number: 3
      description: "Apply to principal"
      calculation: "10000 × 1.6288946268"
      result: 16288.95
  validation:
    checks_passed:
      - "Final amount greater than principal"
      - "Growth rate reasonable for 5% over 10 years (~63%)"
      - "Result matches independent calculation"
```

### Statistical Analysis
```yaml
input:
  problem: "What's the average of 23, 45, 67, 89, 12, 34, 56, and 78?"
  show_steps: true

output:
  success: true
  answer: "The average of the 8 numbers is 50.5"
  answer_value: 50.5
  python_code: |
    # Statistical Analysis
    import statistics

    data = [23, 45, 67, 89, 12, 34, 56, 78]

    result = {
        'mean': statistics.mean(data),
        'sum': sum(data),
        'count': len(data)
    }
  execution_result:
    success: true
    result:
      mean: 50.5
      sum: 404
      count: 8
    result_type: "dict"
    code_executed: "..."
    execution_time_ms: 0.045
  problem_analysis:
    problem_type: "statistical"
    identified_values:
      data: [23, 45, 67, 89, 12, 34, 56, 78]
    formula_used: "mean = sum(data) / len(data)"
  steps:
    - step_number: 1
      description: "Sum all numbers"
      calculation: "23 + 45 + 67 + 89 + 12 + 34 + 56 + 78"
      result: 404
    - step_number: 2
      description: "Count numbers"
      calculation: "len([23, 45, 67, 89, 12, 34, 56, 78])"
      result: 8
    - step_number: 3
      description: "Divide sum by count"
      calculation: "404 ÷ 8"
      result: 50.5
```

## Validation Rules

```yaml
validations:
  - name: "positive_inputs_positive_output"
    condition: "all inputs positive AND operation is +/*"
    check: "result > 0"
    warning: "Result should be positive for positive inputs with + or *"

  - name: "percentage_bounds"
    condition: "calculating X% of Y"
    check: "0 <= result <= Y (for 0-100%)"
    warning: "Percentage result should be between 0 and original value"

  - name: "compound_interest_growth"
    condition: "compound interest calculation"
    check: "final > principal (for positive rate)"
    warning: "Compound interest should grow the principal"

  - name: "average_bounds"
    condition: "calculating mean/average"
    check: "min(data) <= result <= max(data)"
    warning: "Average must be between min and max values"
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `PARSE_ERROR` | Cannot understand the problem | Rephrase more clearly |
| `AMBIGUOUS_PROBLEM` | Multiple interpretations possible | Add clarification |
| `MISSING_VALUES` | Not all required numbers provided | Provide missing values |
| `CALCULATION_ERROR` | Python execution failed | Check values (division by zero, etc.) |
| `VALIDATION_FAILED` | Result failed sanity checks | Review problem statement |

## Integration Pattern

To enforce strict math across an LLM system:

```yaml
system_prompt_addition: |
  ## MANDATORY: Strict Math Protocol

  For ANY calculation or math question, you MUST:
  1. NEVER perform mental arithmetic
  2. ALWAYS use the math-solve skill
  3. INCLUDE the python_code in your response for auditability

  Examples of what triggers math-solve:
  - "What is 25 times 47?" → math-solve
  - "Calculate the tip..." → math-solve
  - "If I have 3 apples..." → math-solve
  - "What's the average..." → math-solve

  When responding with math results, format as:
  "The answer is [answer].

  **Calculation (Python):**
  ```python
  [python_code from math-solve]
  ```
  Executed in [execution_time_ms]ms"
```
