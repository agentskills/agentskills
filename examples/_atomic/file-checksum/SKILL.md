---
name: file-checksum
description: Calculate cryptographic checksums (MD5, SHA256) for files. Wraps md5sum/sha256sum commands. Use for verifying file integrity.
level: 1
operation: READ
license: Apache-2.0
---

# File Checksum

Calculate or verify cryptographic checksums for files.

## When to Use

Use this skill when:
- Verifying downloaded file integrity
- Detecting file modifications
- Creating checksums for distribution
- Comparing files by content hash

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | File path or glob pattern |
| `algorithm` | string | No | Hash algorithm: md5, sha1, sha256, sha512 (default: sha256) |
| `verify` | string | No | Expected checksum to verify against |
| `check_file` | string | No | File containing checksums to verify |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `checksums` | object[] | List of file checksums |
| `verified` | boolean | Whether verification passed (if verify specified) |
| `algorithm` | string | Algorithm used |

Each checksum entry:

| Field | Type | Description |
|-------|------|-------------|
| `file` | string | File path |
| `hash` | string | Calculated checksum |
| `match` | boolean | Whether matches expected (if verifying) |

## Usage

```
Calculate SHA256 checksum for ubuntu.iso
```

```
Verify download.zip matches checksum abc123...
```

```
Generate MD5 checksums for all files in dist/
```

## Example Response

```json
{
  "checksums": [
    {
      "file": "ubuntu-22.04.iso",
      "hash": "a4acfda10b18da50e2ec50ccaf860d7f20b389df8765611142305c0e911b4f64"
    }
  ],
  "verified": true,
  "algorithm": "sha256"
}
```

## Algorithm Comparison

| Algorithm | Output Size | Use Case |
|-----------|-------------|----------|
| MD5 | 32 chars | Legacy, fast (not secure) |
| SHA1 | 40 chars | Legacy (deprecated for security) |
| SHA256 | 64 chars | Recommended default |
| SHA512 | 128 chars | High security requirements |

## Why This Matters for Composition

As a verification primitive, `file-checksum` ensures integrity:
- **secure-download** (Level 2) fetches file + verifies checksum
- **backup-verify** (Level 3) restores + compares checksums + reports

## Notes

- Wraps coreutils `md5sum`, `sha256sum`, etc.
- SHA256 recommended for most use cases
- MD5 is fast but cryptographically weak
- Binary files are handled correctly
