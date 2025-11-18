# Gmail AI Organizer API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

All API endpoints (except `/auth/*`) require authentication via Bearer token in the Authorization header:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

## Authentication Endpoints

### Initiate Login

**GET** `/auth/login`

Returns Google OAuth2 authorization URL.

**Response:**
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?...",
  "state": "random_state_string"
}
```

### OAuth Callback

**POST** `/auth/callback`

Exchange authorization code for access token.

**Request:**
```json
{
  "code": "authorization_code_from_google"
}
```

**Response:**
```json
{
  "access_token": "ya29.a0...",
  "refresh_token": "1//0g...",
  "token_expiry": "2024-01-01T12:00:00",
  "user_email": "user@gmail.com",
  "user_name": "User Name"
}
```

### Refresh Token

**POST** `/auth/refresh`

Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "1//0g..."
}
```

---

## Gmail Endpoints

### Get Messages

**POST** `/gmail/messages`

Fetch emails from Gmail.

**Request:**
```json
{
  "max_results": 50,
  "query": "is:unread",
  "label_ids": ["INBOX"]
}
```

**Response:**
```json
{
  "messages": [
    {
      "id": "18c1234567890abcd",
      "thread_id": "18c1234567890abcd",
      "subject": "Meeting Tomorrow",
      "from": "sender@example.com",
      "to": "you@gmail.com",
      "snippet": "Let's meet tomorrow at 2pm...",
      "body_text": "Full email body...",
      "date": "Mon, 1 Jan 2024 10:00:00 -0800",
      "labels": ["INBOX", "UNREAD"]
    }
  ],
  "total": 25,
  "next_page_token": null
}
```

### Get Single Message

**GET** `/gmail/messages/{message_id}`

Get detailed information about a specific email.

### Summarize Email

**POST** `/gmail/messages/{message_id}/summarize`

Generate AI summary of email.

**Response:**
```json
{
  "message_id": "18c1234567890abcd",
  "subject": "Q4 Planning Meeting",
  "summary": "Meeting scheduled for Q4 planning on Friday at 2pm. Need to prepare presentation slides and review budget."
}
```

### Archive Message

**POST** `/gmail/messages/{message_id}/archive`

Archive an email.

### Trash Message

**POST** `/gmail/messages/{message_id}/trash`

Move email to trash.

### Process Batch

**POST** `/gmail/process-batch`

Process multiple emails with AI.

**Request:**
```json
{
  "query": "is:unread",
  "max_results": 20,
  "auto_categorize": true,
  "apply_labels": false
}
```

**Response:**
```json
{
  "total": 20,
  "emails": [
    {
      "id": "18c1234567890abcd",
      "subject": "Newsletter",
      "summary": "AI-generated summary",
      "category": "newsletter",
      "ai_tags": ["marketing", "updates"],
      "sentiment": "neutral",
      "priority_score": 30
    }
  ]
}
```

### Get Labels

**GET** `/gmail/labels`

Get all Gmail labels.

---

## Calendar Endpoints

### Get Events

**POST** `/calendar/events`

Fetch calendar events.

**Request:**
```json
{
  "calendar_id": "primary",
  "time_min": "2024-01-01T00:00:00Z",
  "time_max": "2024-01-31T23:59:59Z",
  "max_results": 50
}
```

**Response:**
```json
{
  "events": [
    {
      "id": "event123",
      "summary": "Team Meeting",
      "description": "Weekly sync",
      "start": {
        "dateTime": "2024-01-15T14:00:00-08:00",
        "timeZone": "America/Los_Angeles"
      },
      "end": {
        "dateTime": "2024-01-15T15:00:00-08:00",
        "timeZone": "America/Los_Angeles"
      },
      "location": "Conference Room A",
      "attendees": [
        { "email": "colleague@example.com" }
      ]
    }
  ],
  "total": 12
}
```

### Get Today's Events

**GET** `/calendar/events/today`

Get events for today.

### Get Week's Events

**GET** `/calendar/events/week`

Get events for the next 7 days.

### Create Event

**POST** `/calendar/events/create`

Create a new calendar event.

**Request:**
```json
{
  "summary": "Project Review",
  "start_time": "2024-01-20T14:00:00",
  "end_time": "2024-01-20T15:00:00",
  "description": "Review project progress",
  "location": "Room 101",
  "attendees": ["team@example.com"],
  "timezone": "America/Los_Angeles"
}
```

### Quick Add Event

**POST** `/calendar/events/quick-add`

Create event using natural language.

**Request:**
```json
{
  "text": "Meeting with John tomorrow at 3pm"
}
```

### Delete Event

**DELETE** `/calendar/events/{event_id}`

Delete a calendar event.

---

## Chat Endpoints

### Send Message

**POST** `/chat/message`

Send chat message and get AI response.

**Request:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Summarize my unread emails from today"
    }
  ],
  "include_email_context": true,
  "include_calendar_context": true,
  "max_context_items": 10
}
```

**Response:**
```json
{
  "message": "You have 5 unread emails today: 2 work-related, 2 newsletters, and 1 personal. The most important is from your manager about the Q1 review.",
  "actions_taken": [
    {
      "action": "summarize",
      "count": 5
    }
  ],
  "context_used": {
    "emails": {
      "total": 5,
      "items": [...]
    }
  }
}
```

### Quick Action

**POST** `/chat/quick-action`

Execute predefined quick actions.

**Request:**
```json
{
  "action": "summarize_unread",
  "parameters": null
}
```

**Available Actions:**
- `summarize_unread` - Summarize all unread emails
- `archive_newsletters` - Archive old newsletters
- `show_today_schedule` - Show today's calendar
- `find_free_time` - Find free time slots

### Get Suggestions

**GET** `/chat/suggestions`

Get AI-powered inbox management suggestions.

**Response:**
```json
{
  "suggestions": [
    {
      "type": "archive",
      "description": "You have 15 newsletters. Archive old ones?",
      "action": "archive_newsletters"
    }
  ],
  "email_stats": {
    "newsletter": 15,
    "important": 3,
    "work": 8
  }
}
```

---

## Email Categories

AI can categorize emails into:

- `important` - Urgent or high-priority
- `newsletter` - Marketing emails, newsletters
- `social` - Social media notifications
- `promotions` - Promotional offers
- `work` - Work-related
- `personal` - Personal correspondence
- `spam` - Likely spam
- `unclassified` - Cannot determine

---

## Error Responses

All endpoints may return error responses:

**400 Bad Request:**
```json
{
  "detail": "Invalid request parameters"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Invalid credentials"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error",
  "message": "Error details (in debug mode)"
}
```

---

## Rate Limits

- Free tier (project keys): 100 requests/month
- BYOK: Unlimited (subject to your AI provider's limits)

---

## Webhook Support (Coming Soon)

Future versions will support webhooks for:
- New email notifications
- Calendar event changes
- AI processing completion
