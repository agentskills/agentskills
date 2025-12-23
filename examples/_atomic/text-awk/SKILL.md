---
name: text-awk
description: Pattern scanning and processing language for structured text. Wraps the awk command. Use for column extraction, calculations, and text reports.
level: 1
operation: READ
license: Apache-2.0
---

# Text Awk

Process structured text with field extraction and pattern matching.

## When to Use

Use this skill when:
- Extracting specific columns from tabular data
- Calculating sums, averages, or counts
- Filtering rows based on field values
- Generating formatted reports from data

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `program` | string | Yes | Awk program (e.g., `{print $1, $3}`) |
| `input` | string | Yes | Input file path or text content |
| `field_separator` | string | No | Field delimiter (default: whitespace) |
| `output_separator` | string | No | Output field separator (default: space) |
| `variables` | object | No | Variables to pass to awk program |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `output` | string | Processed output |
| `lines_processed` | integer | Number of input lines processed |

## Usage

```
Extract the first and third columns from data.csv (comma-separated)
```

```
Sum the values in the second column of numbers.txt
```

```
Print lines where the third field is greater than 100
```

## Example Response

```json
{
  "output": "alice 50\nbob 75\ncharlie 100\n",
  "lines_processed": 3
}
```

## Common Programs

| Program | Description |
|---------|-------------|
| `{print $1}` | Print first field |
| `{print $NF}` | Print last field |
| `{sum += $2} END {print sum}` | Sum second column |
| `$3 > 100` | Print lines where field 3 > 100 |
| `{print NR, $0}` | Add line numbers |
| `!seen[$1]++` | Remove duplicates by first field |
| `BEGIN {FS=","} {print $2}` | Set comma as separator |

## Why This Matters for Composition

As a data processing primitive, `text-awk` enables analytics:
- **log-stats** (Level 2) extracts fields + calculates metrics
- **csv-transform** (Level 2) reads CSV + transforms + outputs
- **report-generate** (Level 3) collects data + awk processes + formats

## Notes

- Wraps GNU `gawk` / POSIX `awk`
- Fields are numbered from $1; $0 is entire line
- NF = number of fields; NR = line number
- For CSV with quotes, consider dedicated CSV tools
