# WhatsApp Personal Assistant MVP

A production-quality WhatsApp AI assistant built with modular architecture for managing tasks and notes.

## Features

- **Task Management**: Add tasks, set reminders, view today's tasks
- **Notes**: Save quick notes and ideas, search through notes
- **Daily Digest**: Receive a morning summary of tasks and recent notes
- **WhatsApp Integration**: Fully integrated with WhatsApp Cloud API

## Architecture

```
project_root/
app/
├── main.py              # FastAPI application
├── config.py            # Configuration management
├── whatsapp/            # WhatsApp integration
│   ├── webhook.py       # Webhook endpoints
│   ├── client.py        # WhatsApp API client
│   └── parser.py        # Message parser
├── agent/               # AI Agent
│   ├── agent.py         # Main agent logic
│   ├── prompts.py       # System prompts
│   └── tools_registry.py # Tool registry
├── tools/               # Tool implementations
│   ├── task_tools.py    # Task management tools
│   └── note_tools.py   # Note management tools
├── services/            # Business logic
│   ├── task_service.py
│   ├── note_service.py
│   └── search_service.py
├── database/            # Database layer
│   ├── db.py           # Database connection
│   └── models.py       # SQLAlchemy models
├── scheduler/          # Background jobs
│   ├── scheduler.py
│   ├── reminders.py
│   └── digest.py
└── utils/              # Utilities
    ├── logger.py
    └── helpers.py
```

## Setup

1. **Clone the repository**

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Configure WhatsApp Cloud API**
   - Create a Meta Developer account
   - Create a new app
   - Set up WhatsApp product
   - Get your Phone Number ID and Access Token
   - Configure webhook URL to your deployed server

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Verify webhook**
   - Open WhatsApp Manager
   - Configure webhook with your URL + `/webhook`
   - Verify the webhook

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENCLAW_API_KEY` | OpenClaw API key for AI agent |
| `WHATSAPP_TOKEN` | WhatsApp Cloud API access token |
| `WHATSAPP_PHONE_ID` | WhatsApp Phone Number ID |
| `AUTHORIZED_USER` | Authorized phone number (+1234567890) |
| `DATABASE_URL` | SQLite database URL |
| `DIGEST_TIME` | Daily digest time (HH:MM, default: 08:00) |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, etc.) |

## Usage

### Task Management
- "Add buy groceries to my tasks"
- "Remind me to call doctor at 14:00"
- "What are my tasks today?"

### Notes
- "Note: idea for hospital voice AI"
- "Save this idea: meeting notes from today"

### Search
- "What ideas do I have about healthcare?"
- "Search my notes for project X"

## Development

### Running Tests
```bash
pytest
```

### Running Linting
```bash
ruff check app/
```

## Production Deployment

1. Use a production-grade database (PostgreSQL recommended)
2. Set up proper logging and monitoring
3. Configure HTTPS for webhook endpoints
4. Use a process manager (e.g., gunicorn, supervisor)

## License

MIT
# openclaw
