# WhatsApp Personal Assistant - Instructions

## Overview
Your personal AI assistant that manages tasks, notes, and calendar via WhatsApp.

---

## Available Commands

### Tasks

| Command | Description |
|---------|-------------|
| `Add [task] to my tasks` | Add a new task |
| `What are my tasks today?` | View today's tasks |
| `Show all tasks` | View all pending tasks |
| `Delete task [id]` | Delete a specific task by ID |
| `Complete task [id]` | Mark a task as completed |
| `Delete all tasks` | Delete all tasks |
| `Remind me to [task] at [time]` | Add a task with reminder time |

### Notes

| Command | Description |
|---------|-------------|
| `Note: [text]` | Save a new note |
| `Save this idea: [text]` | Save a new idea |
| `Show all notes` | View all notes with IDs |
| `Delete note [id]` | Delete a specific note by ID |
| `Delete all notes` | Delete all notes |

### Calendar (Google Calendar)

| Command | Description |
|---------|-------------|
| `Schedule meeting with [name] tomorrow at 3pm` | Create a calendar event |
| `Create all day event called [title] on Saturday` | Create all-day event |
| `Schedule weekly team sync every Monday at 10` | Create a recurring weekly meeting |
| `Cancel next Monday's team sync` | Cancel one occurrence in a recurring series |
| `Cancel the entire weekly team sync` | Cancel the whole recurring series |
| `Add [email] to tomorrow's 3pm meeting` | Add an attendee to an existing event |
| `Remove [email] from the product review` | Remove an attendee from an event |
| `Who is attending the meeting at 3pm?` | List attendees for a specific meeting |
| `Add a Google Meet link to tomorrow's meeting` | Attach a video link (Google Meet) to a meeting |
| `What is the meeting link for my 3pm call?` | Get the main meeting link for an event |
| `Remind me 10 minutes before my meeting` | Add a reminder before an upcoming meeting |
| `Change the reminder for my meeting to 1 hour before` | Update an existing reminder |
| `Remove reminder from tomorrow's meeting` | Remove one or all reminders from an event |
| `What's my schedule today?` | View today's agenda (times, titles, links, overlaps) |
| `Show my meetings tomorrow` | View tomorrow's events |
| `What events do I have this week?` | View this week's events |
| `Am I free tomorrow at 4pm?` | Check availability |
| `Find a 30 minute slot tomorrow` | Find available slots |
| `When is my next meeting with [name]?` | Search events |
| `Cancel my meeting with [name]` | Delete an event |

### Search

| Command | Description |
|---------|-------------|
| `What ideas do I have about [topic]?` | Search notes by topic |
| `Search my notes for [topic]` | Search notes by topic |

### Conversational (Auto-Responses)

These are handled automatically without invoking AI:

| Message Type | Examples |
|--------------|----------|
| Positive | `great`, `perfect`, `awesome`, `thanks`, `nice`, `amazing` |
| Neutral | `ok`, `okay`, `got it`, `cool`, `sure` |
| Negative | `stupid`, `you suck`, `useless` |

Response examples:
- Positive → "Glad that helped!"
- Neutral → "Got it."
- Negative → "I might have misunderstood. Tell me what you'd like me to do."

---

## How It Works

### Task IDs
When you view tasks, each task shows an ID in brackets:
```
• [1] Buy groceries
• [2] Finish report
```

Use this ID to delete or complete tasks:
- `Delete task 1`
- `Complete task 2`

### Note IDs
When you view notes, each note shows an ID in brackets:
```
• [1] Idea for hospital AI...
• [2] Meeting notes...
```

Use this ID to delete:
- `Delete note 1`

---

## Daily Digest

The assistant sends a daily summary at 08:00 AM (configurable) with:
- Today's tasks
- Recent notes
- Today's calendar agenda (if calendar is connected)

---

## Troubleshooting

### Messages not responding
1. Check if server is running
2. Verify WhatsApp webhook is configured correctly
3. Check logs for errors

### OpenClaw API errors
The assistant has a fallback system that works even when the AI API is unavailable. Your commands will still work using rule-based responses.

---

## Technical Details

- **Backend**: Python FastAPI
- **Database**: SQLite
- **AI**: OpenClaw (with fallback to rule-based)
- **Scheduler**: APScheduler for daily digest

---

## Last Updated
March 2026
