# WhatsApp Personal Assistant - Instructions

## Overview
Your personal AI assistant that manages tasks and notes via WhatsApp.

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
