---
name: archive-extract
description: Extract files from compressed archives (tar, zip, gzip). Wraps tar/unzip commands. Use when unpacking downloaded archives or backups.
level: 1
operation: WRITE
license: Apache-2.0
---

# Archive Extract

Extract files from compressed archives.

## When to Use

Use this skill when:
- Unpacking downloaded software archives
- Restoring files from backups
- Extracting specific files from an archive
- Listing archive contents before extraction

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `archive` | string | Yes | Path to archive file |
| `destination` | string | No | Extraction destination (default: current directory) |
| `files` | string[] | No | Specific files to extract (default: all) |
| `list_only` | boolean | No | List contents without extracting (default: false) |
| `strip_components` | integer | No | Remove N leading path components |
| `overwrite` | boolean | No | Overwrite existing files (default: false) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `extracted` | string[] | List of extracted files |
| `count` | integer | Number of files extracted |
| `destination` | string | Extraction directory |
| `archive_type` | string | Detected archive format |

## Usage

```
Extract backup.tar.gz to /home/user/restored/
```

```
List contents of package.zip without extracting
```

```
Extract only config/ directory from archive.tar.xz
```

## Example Response

```json
{
  "extracted": [
    "project/README.md",
    "project/src/main.py",
    "project/src/utils.py",
    "project/tests/test_main.py"
  ],
  "count": 4,
  "destination": "/home/user/projects/project",
  "archive_type": "tar.gz"
}
```

## Supported Formats

| Extension | Format | Command Used |
|-----------|--------|--------------|
| `.tar` | Uncompressed tar | tar |
| `.tar.gz`, `.tgz` | Gzip-compressed tar | tar + gzip |
| `.tar.bz2`, `.tbz2` | Bzip2-compressed tar | tar + bzip2 |
| `.tar.xz`, `.txz` | XZ-compressed tar | tar + xz |
| `.zip` | ZIP archive | unzip |
| `.gz` | Gzip single file | gunzip |

## Why This Matters for Composition

As an archive handling primitive, `archive-extract` enables deployment:
- **deploy-package** (Level 2) downloads + extracts + installs
- **backup-restore** (Level 3) fetches backup + extracts + validates

## Notes

- Wraps POSIX `tar`, GNU `gzip`, `bzip2`, `xz`, `unzip`
- Auto-detects archive format from extension
- Use `list_only: true` to preview before extracting
- Creates destination directory if it doesn't exist
