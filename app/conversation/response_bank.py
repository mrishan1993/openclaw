"""Response bank for conversational fallback."""

from random import choice

POSITIVE_RESPONSES = [
    "Glad that helped!",
    "Happy to hear that!",
    "Nice! Let me know if you need anything else.",
    "Appreciate it!",
    "Glad to hear that!",
    "Thanks! Let me know if you need anything else.",
]

NEUTRAL_RESPONSES = [
    "Got it.",
    "Sounds good.",
    "Anytime.",
    "Sure thing!",
    "Alright!",
    "Okay, noted.",
    "Consider it done.",
]

NEGATIVE_RESPONSES = [
    "I might have misunderstood. Tell me what you'd like me to do.",
    "Sorry about that — how can I help?",
    "Let's try that again. What would you like me to do?",
    "I apologize. What can I help you with?",
]

GREETING_RESPONSES = [
    "Hello! How can I help you today?",
    "Hi there! What's on your mind?",
    "Hey! What would you like me to do?",
    "Greetings! How can I assist you?",
    "Hello! Ready when you are.",
    "Hi! Need help with anything?",
]


def get_response(category: str) -> str:
    """Get a random response for the given category."""
    if category == "positive":
        return choice(POSITIVE_RESPONSES)
    elif category == "neutral":
        return choice(NEUTRAL_RESPONSES)
    elif category == "negative":
        return choice(NEGATIVE_RESPONSES)
    elif category == "greeting":
        return choice(GREETING_RESPONSES)
    return "Got it."
