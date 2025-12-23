---
name: http-request
description: Make HTTP requests to any URL. Supports GET, POST, PUT, PATCH, DELETE methods with custom headers and body. Use for API calls, webhooks, or fetching web content.
level: 1
operation: READ
license: Apache-2.0
---

# HTTP Request

Make HTTP requests to REST APIs, webhooks, or any URL endpoint.

## When to Use

Use this skill when:
- Calling a REST API that doesn't have a dedicated skill
- Fetching data from a URL
- Sending webhooks or callbacks
- Testing API endpoints

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | The URL to request |
| `method` | string | No | HTTP method: GET, POST, PUT, PATCH, DELETE (default: GET) |
| `headers` | object | No | Custom HTTP headers |
| `body` | object | No | Request body for POST/PUT/PATCH |
| `query_params` | object | No | URL query parameters |
| `timeout` | integer | No | Request timeout in seconds (default: 30) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `status_code` | integer | HTTP response status code |
| `headers` | object | Response headers |
| `body` | any | Response body (parsed JSON if applicable) |
| `content_type` | string | Response content type |

## Usage

```
Make an HTTP GET request to https://api.github.com/users/octocat
```

```
POST to https://httpbin.org/post with body {"name": "test", "value": 123}
```

## Example Response

```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/json"
  },
  "body": {
    "login": "octocat",
    "id": 583231,
    "type": "User"
  },
  "content_type": "application/json"
}
```

## Why This Matters for Composition

As the most versatile Level 1 skill, `http-request` enables integration with any HTTP-based service:
- **api-wrapper** (Level 2) can use http-request to interact with any REST API
- **webhook-handler** (Level 3) orchestrates receiving and responding to webhooks

## Notes

- For authenticated APIs, include auth tokens in headers
- Large responses may be truncated
- Consider using dedicated skills (github-*, slack-*) when available for better validation
- Inspired by n8n's HTTP Request node
