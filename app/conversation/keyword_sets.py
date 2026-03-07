"""Keyword sets for conversational fallback detection."""

POSITIVE_KEYWORDS = {
    # basic praise
    "perfect", "great", "good", "awesome", "nice", "amazing",
    "excellent", "fantastic", "wonderful", "brilliant", "super",
    "cool", "neat", "lovely", "impressive", "solid", "sweet",

    # appreciation
    "thanks", "thank you", "thankyou", "thx", "ty", "tysm",
    "appreciate", "appreciate it", "much appreciated",

    # satisfaction
    "love it", "love this", "love that", "this is great",
    "this is perfect", "that's great", "that's perfect",
    "that's awesome", "that works", "this works",

    # approval
    "well done", "nice work", "good job", "great job",
    "perfect thanks", "great thanks",

    # conversational praise
    "you are awesome", "you're awesome", "you are great",
    "you're great", "you rock", "legend", "genius",

    # casual internet
    "nice one", "solid work", "good stuff", "amazing work",
    "fantastic work", "great stuff", "good stuff",

    # short acknowledgements
    "nice", "great!", "perfect!", "awesome!", "cool!",

    # slang / informal
    "lit", "dope", "fire", "based",

    # emoji style
    "👍", "👌", "🔥"
}


NEUTRAL_KEYWORDS = {
    # acknowledgements
    "ok", "okay", "okey", "okk", "okkk", "ok cool",
    "okay cool", "okay sure", "ok sure",

    # confirmations
    "got it", "i got it", "gotcha", "understood",
    "makes sense", "makes sense thanks",

    # agreement
    "alright", "fine", "sure", "sure thing", "sounds good",
    "sounds right", "fair enough",

    # conversational
    "yep", "yeah", "ya", "yah", "yup", "mm", "hmm",

    # short chat replies
    "k", "kk", "k thanks", "ok thanks", "ok got it",

    # continuation signals
    "go on", "continue", "carry on",

    # closure
    "cool thanks", "cool got it", "cool ok",

    # filler
    "right", "okay then", "noted",

    # emoji
    "👍", "👌"
}


NEGATIVE_KEYWORDS = {
    # insults
    "stupid", "idiot", "dumb", "moron", "imbecile", "fool",

    # capability criticism
    "useless", "worthless", "pointless", "broken",
    "this is useless", "you are useless", "you're useless",

    # direct hostility
    "you suck", "this sucks", "that sucks", "suck",

    # anger
    "wtf", "what the fuck", "fuck", "fuck this",
    "fuck you", "fucking useless",

    # profanity
    "shit", "bullshit", "damn", "goddamn",

    # insults / abusive
    "bastard", "asshole", "jerk", "loser",

    # dissatisfaction
    "terrible", "worst", "awful", "bad", "really bad",

    # frustration
    "annoying", "so annoying", "frustrating",
    "this is frustrating",

    # rejection
    "hate this", "hate it", "i hate this", "i hate it",

    # dismissal
    "garbage", "trash", "waste", "waste of time",

    # conversational negative
    "this is dumb", "this is stupid", "this is bad",

    # short reactions
    "ugh", "meh",

    # emoji style
    "👎"
}