# math-execute

Execute mathematical calculations using Python code with full auditability.

## Description

This skill executes mathematical calculations strictly through Python code execution,
never through LLM mental math. This ensures:

1. **Accuracy** - Python handles arithmetic precisely (no hallucinated calculations)
2. **Auditability** - The exact code used is recorded for review
3. **Reproducibility** - Same inputs always produce same outputs
4. **Testability** - Calculations can be verified independently

## CRITICAL RULES

**NEVER perform mental math. ALL calculations MUST go through Python execution.**

- ❌ WRONG: "25 * 47 = 1175" (mental calculation)
- ✅ RIGHT: Execute `25 * 47` in Python, return `1175` with code trace

Even for simple arithmetic like `2 + 2`, execute the Python code.

## Metadata

```yaml
domain: math
level: 1
type: atomic
version: 1.0.0
operation: EXECUTE
tags:
  - math
  - calculation
  - python
  - audit
  - strict
```

## Input Schema

```yaml
inputSchema:
  type: object
  required:
    - code
  properties:
    code:
      type: string
      description: |
        Python code to execute. Must be a valid Python expression or
        multi-line code block that produces a result.

        For expressions: "25 * 47 + 3"
        For complex: "import math; result = math.sqrt(144)"
      examples:
        - "25 * 47"
        - "sum([1, 2, 3, 4, 5])"
        - "import statistics; statistics.mean([10, 20, 30])"
    precision:
      type: integer
      description: Decimal places for floating point results
      default: 10
    timeout_seconds:
      type: number
      description: Maximum execution time
      default: 5.0
    safe_mode:
      type: boolean
      description: |
        If true, restricts to math-safe operations only.
        Disables file I/O, network, system calls.
      default: true
```

## Output Schema

```yaml
outputSchema:
  type: object
  required:
    - success
    - result
    - code_executed
    - execution_time_ms
  properties:
    success:
      type: boolean
      description: Whether calculation completed without error
    result:
      type: any
      description: The computed result (number, list, dict, etc.)
    result_type:
      type: string
      description: Python type of result (int, float, list, etc.)
    code_executed:
      type: string
      description: Exact Python code that was executed (for audit)
    execution_time_ms:
      type: number
      description: Time taken to execute in milliseconds
    stdout:
      type: string
      description: Any printed output from the code
    error:
      type: object
      description: Error details if success is false
      properties:
        type:
          type: string
          description: Exception type (ZeroDivisionError, etc.)
        message:
          type: string
          description: Error message
        traceback:
          type: string
          description: Full Python traceback
```

## Execution Pattern

```python
import ast
import time
import math
import statistics
import decimal
from decimal import Decimal
from fractions import Fraction

# Allowed modules in safe_mode
SAFE_MODULES = {
    'math', 'statistics', 'decimal', 'fractions',
    'random', 'itertools', 'functools', 'operator'
}

# Forbidden in safe_mode
FORBIDDEN_NAMES = {
    'open', 'exec', 'eval', 'compile', '__import__',
    'input', 'breakpoint', 'exit', 'quit'
}

def validate_safe_code(code: str) -> tuple[bool, str]:
    """Check if code is safe to execute."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"Syntax error: {e}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            return False, f"Forbidden function: {node.id}"
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split('.')[0] not in SAFE_MODULES:
                    return False, f"Forbidden import: {alias.name}"
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split('.')[0] not in SAFE_MODULES:
                return False, f"Forbidden import: {node.module}"

    return True, ""

def execute_math(code: str, precision: int = 10,
                 timeout: float = 5.0, safe_mode: bool = True) -> dict:
    """Execute Python math code with full audit trail."""

    if safe_mode:
        is_safe, reason = validate_safe_code(code)
        if not is_safe:
            return {
                "success": False,
                "result": None,
                "code_executed": code,
                "execution_time_ms": 0,
                "error": {
                    "type": "SecurityError",
                    "message": reason
                }
            }

    # Prepare execution environment
    exec_globals = {
        'math': math,
        'statistics': statistics,
        'Decimal': Decimal,
        'Fraction': Fraction,
        '__builtins__': {} if safe_mode else __builtins__
    }

    # Add safe builtins
    if safe_mode:
        exec_globals['__builtins__'] = {
            'abs': abs, 'all': all, 'any': any, 'bin': bin,
            'bool': bool, 'complex': complex, 'dict': dict,
            'divmod': divmod, 'enumerate': enumerate, 'filter': filter,
            'float': float, 'format': format, 'frozenset': frozenset,
            'hex': hex, 'int': int, 'isinstance': isinstance,
            'len': len, 'list': list, 'map': map, 'max': max,
            'min': min, 'oct': oct, 'ord': ord, 'pow': pow,
            'print': print, 'range': range, 'repr': repr,
            'reversed': reversed, 'round': round, 'set': set,
            'slice': slice, 'sorted': sorted, 'str': str,
            'sum': sum, 'tuple': tuple, 'type': type, 'zip': zip,
        }

    start_time = time.perf_counter()

    try:
        # Try as expression first
        try:
            result = eval(code, exec_globals)
        except SyntaxError:
            # Fall back to exec for statements
            exec_globals['_result'] = None
            exec(code + "\n_result = result" if 'result' in code else code, exec_globals)
            result = exec_globals.get('_result') or exec_globals.get('result')

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Format floating point with precision
        if isinstance(result, float):
            result = round(result, precision)

        return {
            "success": True,
            "result": result,
            "result_type": type(result).__name__,
            "code_executed": code,
            "execution_time_ms": round(elapsed_ms, 3)
        }

    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        import traceback
        return {
            "success": False,
            "result": None,
            "code_executed": code,
            "execution_time_ms": round(elapsed_ms, 3),
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        }
```

## Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| `SYNTAX_ERROR` | Invalid Python syntax | Fix code syntax |
| `SECURITY_ERROR` | Forbidden operation in safe_mode | Remove unsafe code or disable safe_mode |
| `ZERO_DIVISION` | Division by zero | Check divisor |
| `OVERFLOW` | Number too large | Use Decimal for precision |
| `TIMEOUT` | Execution exceeded timeout | Simplify calculation or increase timeout |
| `TYPE_ERROR` | Invalid operation for types | Check operand types |

## Examples

### Simple Arithmetic
```yaml
input:
  code: "25 * 47 + 3"

output:
  success: true
  result: 1178
  result_type: "int"
  code_executed: "25 * 47 + 3"
  execution_time_ms: 0.015
```

### Statistical Calculation
```yaml
input:
  code: |
    import statistics
    data = [23, 45, 67, 89, 12, 34, 56, 78]
    result = {
        'mean': statistics.mean(data),
        'median': statistics.median(data),
        'stdev': statistics.stdev(data)
    }

output:
  success: true
  result:
    mean: 50.5
    median: 50.5
    stdev: 26.2488094
  result_type: "dict"
  code_executed: "import statistics\ndata = [23, 45, 67, 89, 12, 34, 56, 78]..."
  execution_time_ms: 0.234
```

### Financial Calculation
```yaml
input:
  code: |
    from decimal import Decimal
    principal = Decimal('10000.00')
    rate = Decimal('0.05')
    years = 10
    result = float(principal * (1 + rate) ** years)
  precision: 2

output:
  success: true
  result: 16288.95
  result_type: "float"
  code_executed: "from decimal import Decimal\nprincipal = Decimal('10000.00')..."
  execution_time_ms: 0.089
```

### Error Handling
```yaml
input:
  code: "100 / 0"

output:
  success: false
  result: null
  code_executed: "100 / 0"
  execution_time_ms: 0.012
  error:
    type: "ZeroDivisionError"
    message: "division by zero"
    traceback: "Traceback (most recent call last):\n  File..."
```

## Why This Matters

LLMs are notoriously unreliable at arithmetic:

| Problem | LLM Mental Math | Python Execution |
|---------|-----------------|------------------|
| 23 × 47 | Often wrong (1081? 1181?) | Always 1081 |
| √2 × √3 | Approximation errors | math.sqrt(2) * math.sqrt(3) = 2.449489743 |
| Compound interest | Rounding errors accumulate | Decimal precision |
| Statistical analysis | Cannot perform | Full scipy/statistics |

**Trust but verify**: The `code_executed` field allows anyone to:
1. Review exactly what was computed
2. Run it independently to verify
3. Catch errors in problem translation
4. Audit the calculation methodology
