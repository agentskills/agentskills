---
name: network-fetch
description: Download files or content from URLs via HTTP/HTTPS/FTP. Wraps curl/wget commands. Use when fetching remote resources.
level: 1
operation: READ
license: Apache-2.0
---

# Network Fetch

Download content from URLs.

## When to Use

Use this skill when:
- Downloading files from the web
- Fetching API responses
- Retrieving remote configuration
- Testing URL accessibility

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | URL to fetch |
| `output` | string | No | Save to file path (default: return content) |
| `method` | string | No | HTTP method: GET, POST, HEAD (default: GET) |
| `headers` | object | No | Custom HTTP headers |
| `data` | string | No | Request body for POST |
| `follow_redirects` | boolean | No | Follow HTTP redirects (default: true) |
| `timeout` | integer | No | Request timeout in seconds (default: 30) |
| `auth` | object | No | Authentication credentials |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `content` | string | Response body (if not saved to file) |
| `status_code` | integer | HTTP status code |
| `headers` | object | Response headers |
| `file_path` | string | Path to saved file (if output specified) |
| `size` | integer | Content size in bytes |

## Usage

```
Download https://example.com/data.json and return the content
```

```
Fetch https://releases.ubuntu.com/22.04/ubuntu-22.04-live-server-amd64.iso and save to ~/Downloads/
```

```
Make a POST request to https://api.example.com/webhook with JSON body
```

## Example Response

```json
{
  "content": "{\"status\": \"ok\", \"version\": \"1.2.3\"}",
  "status_code": 200,
  "headers": {
    "content-type": "application/json",
    "content-length": "38"
  },
  "size": 38
}
```

## Why This Matters for Composition

As a network primitive, `network-fetch` enables remote operations:
- **api-call** (Level 2) wraps fetch with auth + retry + error handling
- **file-download** (Level 2) fetches + verifies checksum + extracts
- **scrape-page** (Level 3) fetches HTML + parses + extracts data

## Notes

- Wraps `curl` and `wget`
- For large files, use `output` to save directly to disk
- HTTPS certificates are verified by default
- Consider rate limiting when making multiple requests
