---
name: pdf-save
description: Save a webpage as a PDF file with metadata. Use when you need to archive web content, create evidence snapshots, or preserve sources for offline access.
level: 1
operation: WRITE
license: Apache-2.0
---

# PDF Save

Save any URL as a PDF document with capture metadata.

## When to Use

Use this skill when:
- Archiving web pages for evidence or records
- Preserving sources for research
- Creating offline copies of important pages
- Building a reference library from web sources

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | The URL to save |
| `output_path` | string | Yes | Where to save the PDF |
| `include_metadata` | boolean | No | Add capture timestamp header (default: true) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `pdf_path` | string | Path to the saved PDF |
| `metadata` | object | Capture details (url, timestamp, method) |

## Usage

```
Save https://example.com/article as PDF to sources/article.pdf
```

## Metadata Header

When `include_metadata` is true, the PDF includes:
- Original URL
- Capture timestamp (UTC)
- Method used for conversion

## Notes

- Some dynamic sites may not render completely
- JavaScript-heavy pages may need special handling
- Large pages may take longer to process
