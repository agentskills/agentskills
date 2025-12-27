---
name: content-repurpose
description: |
  Transform long-form content (blog posts, articles, docs) into multiple
  formats for different channels: Twitter threads, LinkedIn posts,
  newsletter snippets, and social media cards.
level: 3
operation: WRITE
license: Apache-2.0
composes:
  - content-read
  - web-fetch
  - twitter-draft-create
  - linkedin-draft-create
  - buffer-schedule
  - image-generate
tool_discovery:
  content_source:
    prefer: [web-fetch, file-read, notion-page-read]
  social_scheduling:
    prefer: [buffer-schedule, hootsuite-schedule, later-schedule]
    fallback: native-drafts
  image_generation:
    prefer: [dall-e-generate, midjourney-generate]
    fallback: canva-template
---

# Content Repurpose

Transform content into multiple social media formats.

## Trigger Phrases

- "Turn this blog post into social content"
- "Create a Twitter thread from [URL]"
- "Repurpose [article] for LinkedIn"
- "Make social posts from this doc"

## Workflow Steps

```
1. FETCH: Get source content
       │
       ├── URL → Web fetch + extract
       ├── File → Read document
       └── Paste → Direct input
       │
       ▼
2. ANALYSE: Understand content structure
       │
       ├── Key thesis/argument
       ├── Supporting points
       ├── Quotable lines
       ├── Statistics/data
       └── Call to action
       │
       ▼
3. GENERATE: Create platform-specific content
       │
       ├── Twitter thread (5-10 tweets)
       │   • Hook tweet
       │   • Key points
       │   • Thread conclusion + CTA
       │
       ├── LinkedIn post (1300 chars)
       │   • Professional angle
       │   • Personal insight
       │   • Engagement question
       │
       ├── Newsletter snippet (200 words)
       │   • Summary + link
       │
       └── Social cards (optional)
           • Quote graphics
           • Stat visualisations
       │
       ▼
4. REVIEW: Present drafts for approval
       │
       ▼
5. SCHEDULE/SAVE: Based on preference
       │
       ├── Buffer/Hootsuite → Schedule
       ├── Native drafts → Save for later
       └── Return only → User posts manually
       │
       ▼
6. RETURN: All generated content + links
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source` | string | Yes | URL, file path, or raw content |
| `platforms` | string[] | No | Platforms: twitter, linkedin, newsletter (default: all) |
| `tone` | string | No | Tone: professional, casual, provocative (default: match source) |
| `schedule` | boolean | No | Schedule posts via Buffer (default: false, save drafts) |
| `generate_images` | boolean | No | Create social cards/graphics (default: false) |
| `thread_length` | integer | No | Target Twitter thread length (default: 7) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `source_summary` | string | Brief summary of source content |
| `twitter` | object | Twitter thread content |
| `linkedin` | object | LinkedIn post content |
| `newsletter` | object | Newsletter snippet |
| `images` | object[] | Generated graphics (if requested) |
| `scheduled` | object | Scheduling details (if scheduled) |
| `draft_links` | object | Links to saved drafts |

## Usage

```
Turn https://blog.example.com/ai-trends-2025 into a Twitter thread and LinkedIn post
```

```
Repurpose my latest blog post for social, casual tone, schedule for tomorrow
```

```
Create social content from this product announcement doc
```

## Example Response

```json
{
  "source_summary": "Article about 5 AI trends for 2025: agents, multimodal, enterprise adoption, regulation, and open source.",
  "twitter": {
    "thread": [
      {
        "position": 1,
        "content": "5 AI trends that will define 2025 🧵\n\nAfter talking to 50+ AI founders, here's what's actually coming (not hype):",
        "type": "hook"
      },
      {
        "position": 2,
        "content": "1/ Agents go mainstream\n\nNot chatbots. Actual autonomous agents that:\n- Book your travel\n- Handle customer support\n- Write and deploy code\n\nThe UX shift from \"chat\" to \"delegate\" is huge.",
        "type": "point"
      },
      {
        "position": 7,
        "content": "The bottom line:\n\n2025 is when AI stops being a feature and becomes infrastructure.\n\nCompanies not building on this will be like companies that ignored mobile in 2012.\n\nFull breakdown: [link]",
        "type": "conclusion"
      }
    ],
    "total_tweets": 7,
    "draft_url": "https://twitter.com/compose/tweet?draft=abc123"
  },
  "linkedin": {
    "content": "Just published my analysis of AI trends for 2025.\n\nAfter 50+ conversations with founders and researchers, one thing is clear:\n\nWe're shifting from AI as a tool to AI as a teammate.\n\nThe 5 trends I'm watching:\n\n→ Autonomous agents (beyond chatbots)\n→ Multimodal by default\n→ Enterprise finally adopts\n→ Regulation gets real\n→ Open source catches up\n\nThe companies that adapt will thrive. The rest will scramble.\n\nWhat trend are you most excited (or worried) about?\n\n#AI #FutureTech #2025Trends",
    "char_count": 547,
    "draft_url": "https://linkedin.com/post/draft/xyz789"
  },
  "newsletter": {
    "snippet": "This week I published a deep dive on AI trends for 2025. TL;DR: agents go mainstream, multimodal becomes default, and enterprises finally get serious. Read the full analysis →",
    "word_count": 35
  },
  "images": [],
  "scheduled": null,
  "draft_links": {
    "twitter": "https://twitter.com/compose/tweet?draft=abc123",
    "linkedin": "https://linkedin.com/post/draft/xyz789"
  }
}
```

## Platform Formats

| Platform | Format | Length | Style |
|----------|--------|--------|-------|
| **Twitter** | Thread | 5-15 tweets | Hook → Points → CTA |
| **LinkedIn** | Single post | 1300 chars | Professional, story-driven |
| **Newsletter** | Snippet | 50-200 words | Summary + tease |
| **Instagram** | Carousel | 10 slides | Visual + caption |

## Why Level 3

This workflow demonstrates:
1. **Content understanding**: Extracts structure and key points
2. **Multi-format generation**: Same content, different platforms
3. **Platform-native style**: Adapts tone and format per channel
4. **Scheduling integration**: Optional auto-scheduling
5. **Image generation**: Creates visual assets (optional)
6. **Draft management**: Saves for review before posting

## Composition Graph

```
content-repurpose (L3)
    │
    ├─── content-read (L1) ───────► Fetch source
    │    [URL | File | Paste]
    │
    ├──► [Analyse Content]
    │     • Extract thesis
    │     • Identify quotes
    │     • Find statistics
    │
    ├─┬─ [Generate - Parallel]
    │ │
    │ ├── [Twitter Thread Generator]
    │ ├── [LinkedIn Post Generator]
    │ └── [Newsletter Snippet Generator]
    │
    ├─── image-generate (L1) ────► Social cards (optional)
    │
    └─┬─ [Deliver - Tool Discovery]
      │
      ├── buffer-schedule (L1) ──► Schedule
      ├── twitter-draft-create (L1)
      └── linkedin-draft-create (L1)
```

## Notes

- Preserves author's voice when possible
- Adds platform-appropriate hashtags/formatting
- Respects character limits per platform
- Thread hooks optimised for engagement
- Images require API keys for generation
