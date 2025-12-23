---
name: meeting-schedule
description: Schedule client meetings with calendar integration. Supports discovery, review, strategy, and ad-hoc meeting types with appropriate durations and preparation tasks.
level: 1
operation: WRITE
license: Apache-2.0
domain: financial-advisory
tool_discovery:
  calendar:
    prefer: [outlook-calendar, google-calendar, xplan-calendar]
  video:
    prefer: [teams-meeting, zoom-meeting, google-meet]
---

# Meeting Schedule

Schedule client meetings with appropriate preparation workflows.

## When to Use

Use this skill when:
- Booking initial discovery meetings
- Scheduling annual reviews
- Setting up strategy presentation meetings
- Arranging ad-hoc consultations

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Client identifier |
| `meeting_type` | string | Yes | Type: discovery, review, strategy, advice_presentation, ad_hoc |
| `preferred_dates` | string[] | No | Preferred date/time slots |
| `duration` | integer | No | Duration in minutes (default: based on type) |
| `location` | string | No | Location: office, video, client_premises |
| `attendees` | string[] | No | Additional attendees |
| `agenda_items` | string[] | No | Custom agenda items |
| `send_invite` | boolean | No | Send calendar invite (default: true) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `meeting_id` | string | Unique meeting identifier |
| `scheduled_time` | string | Confirmed date/time |
| `duration` | integer | Meeting duration in minutes |
| `location` | object | Location details (address or video link) |
| `attendees` | object[] | Confirmed attendees |
| `preparation_tasks` | object[] | Pre-meeting tasks created |
| `documents_to_prepare` | string[] | Documents needed |
| `calendar_link` | string | Calendar event URL |

## Meeting Types

| Type | Duration | Preparation |
|------|----------|-------------|
| `discovery` | 60 min | FSG, questionnaire, prospect research |
| `review` | 90 min | Performance report, fact-find update, agenda |
| `strategy` | 60 min | Strategy paper, team briefing |
| `advice_presentation` | 90 min | SOA, implementation docs |
| `ad_hoc` | 30 min | Meeting notes template |

## Usage

```
Schedule annual review with John Smith, prefer next week Tuesday or Thursday afternoon
```

```
Book discovery meeting with new prospect Sarah Chen at our Collins St office
```

```
Set up video call with the Henderson family to present their SOA
```

## Example Response

```json
{
  "meeting_id": "MTG-2024-12-23-001234",
  "scheduled_time": "2024-12-30T14:00:00+11:00",
  "duration": 90,
  "meeting_type": "review",
  "location": {
    "type": "office",
    "address": "Level 10, 123 Collins St, Melbourne VIC 3000",
    "room": "Meeting Room 2"
  },
  "attendees": [
    {
      "name": "John Smith",
      "email": "john.smith@email.com",
      "role": "client"
    },
    {
      "name": "Jane Doe",
      "email": "jane.doe@advisory.com",
      "role": "adviser"
    }
  ],
  "preparation_tasks": [
    {
      "task": "Update fact-find",
      "due": "2024-12-27",
      "assigned_to": "adviser"
    },
    {
      "task": "Generate performance report",
      "due": "2024-12-29",
      "assigned_to": "system"
    },
    {
      "task": "Prepare review agenda",
      "due": "2024-12-29",
      "assigned_to": "adviser"
    }
  ],
  "documents_to_prepare": [
    "FSG (if updated)",
    "Performance report",
    "Review agenda",
    "Fact-find update form"
  ],
  "calendar_link": "https://calendar.google.com/event/abc123",
  "client_notified": true,
  "confirmation_sent": true
}
```

## Preparation Workflows

### Discovery Meeting
1. Create prospect record (if new)
2. Prepare FSG
3. Prepare questionnaire
4. Research prospect background
5. Prepare discovery agenda

### Annual Review
1. Update fact-find template
2. Generate performance report
3. Check compliance status
4. Prepare fee disclosure (if renewal)
5. Review client goals progress

### Strategy Presentation
1. Finalise strategy paper
2. Internal team review
3. Prepare presentation materials
4. Book appropriate room/setup

### Advice Presentation
1. Finalise SOA
2. Compliance sign-off
3. Prepare implementation documents
4. Set up signature workflow

## Notes

- Calendar sync checks adviser availability
- Client preferences (time, location) respected
- Automatic reminder emails: 1 week, 1 day, 1 hour
- Video links generated automatically for remote meetings
- Meeting notes template created in CRM
