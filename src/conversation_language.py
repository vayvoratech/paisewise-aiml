# ============================================================
# PAISEWISE CONVERSATIONAL LANGUAGE SUPPORT
# ============================================================

from .language_support import (
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE,
    is_supported_language,
    normalize_language,
)


# ============================================================
# IN-MEMORY CONVERSATION STORAGE
# ============================================================

CONVERSATIONS = {}


def get_conversation(conversation_id: str):
    """
    Get an existing conversation.

    If the conversation does not exist,
    create a new one.
    """

    if conversation_id not in CONVERSATIONS:
        CONVERSATIONS[conversation_id] = {
            "conversation_id": conversation_id,
            "language": DEFAULT_LANGUAGE,
            "messages": []
        }

    return CONVERSATIONS[conversation_id]


# ============================================================
# LANGUAGE SWITCHING
# ============================================================

def switch_language(
    conversation_id: str,
    new_language: str
):
    """
    Switch the language of an existing conversation.
    """

    if not is_supported_language(new_language):
        raise ValueError(
            f"Unsupported language '{new_language}'. "
            f"Supported languages: "
            f"{list(SUPPORTED_LANGUAGES.keys())}"
        )

    new_language = normalize_language(new_language)

    conversation = get_conversation(
        conversation_id
    )

    previous_language = conversation["language"]

    language_changed = (
        previous_language != new_language
    )

    conversation["language"] = new_language

    return {
        "previous_language": previous_language,
        "current_language": new_language,
        "language_changed": language_changed
    }


# ============================================================
# ADD MESSAGE
# ============================================================

def add_message(
    conversation_id: str,
    role: str,
    message: str,
    language: str
):
    """
    Add a user or assistant message
    to the conversation history.
    """

    conversation = get_conversation(
        conversation_id
    )

    conversation["messages"].append({
        "role": role,
        "message": message,
        "language": language
    })


# ============================================================
# GET CONVERSATION HISTORY
# ============================================================

def get_conversation_history(
    conversation_id: str
):
    """
    Return all messages in a conversation.
    """

    conversation = get_conversation(
        conversation_id
    )

    return conversation["messages"]


# ============================================================
# GET CURRENT LANGUAGE
# ============================================================

def get_current_language(
    conversation_id: str
):
    """
    Return the current language of the conversation.
    """

    conversation = get_conversation(
        conversation_id
    )

    return conversation["language"]


# ============================================================
# GET LAST USER MESSAGE
# ============================================================

def get_last_user_message(
    conversation_id: str
):
    """
    Get the most recent user message.
    """

    history = get_conversation_history(
        conversation_id
    )

    for message in reversed(history):

        if message["role"] == "user":
            return message["message"]

    return None


# ============================================================
# GET LAST ASSISTANT MESSAGE
# ============================================================

def get_last_assistant_message(
    conversation_id: str
):
    """
    Get the most recent assistant response.
    """

    history = get_conversation_history(
        conversation_id
    )

    for message in reversed(history):

        if message["role"] == "assistant":
            return message["message"]

    return None


# ============================================================
# CHECK WHETHER MESSAGE NEEDS CONTEXT
# ============================================================

def needs_conversation_context(
    message: str
):
    """
    Detect whether the current message is likely
    referring to something from the previous conversation.
    """

    if not message:
        return False

    message_lower = message.lower().strip()

    context_phrases = [

        # Pronouns
        "it",
        "its",
        "this",
        "that",
        "these",
        "those",

        # Follow-up requests
        "tell me more",
        "explain more",
        "more about",
        "what are its",
        "what is its",
        "what are the",
        "what is the",

        # Benefits / drawbacks
        "benefits",
        "advantages",
        "disadvantages",
        "drawbacks",
        "pros",
        "cons",

        # Explanation
        "explain it",
        "explain this",
        "explain that",

        # Language switching
        "in telugu",
        "in hindi",
        "in tamil",
        "in kannada",
        "in malayalam",
        "in english",

        # Continuation
        "continue",
        "go on",
        "tell me more about it",
        "what about it",
    ]

    for phrase in context_phrases:

        if phrase in message_lower:
            return True

    return False


# ============================================================
# EXTRACT SIMPLE TOPIC
# ============================================================

def extract_topic_from_question(
    previous_question: str
):
    """
    Extract a simple topic from the previous question.

    Examples:

        What is a mutual fund?
        -> mutual fund

        What is SIP?
        -> SIP

        Explain portfolio diversification.
        -> portfolio diversification
    """

    if not previous_question:
        return ""

    question = previous_question.strip()

    prefixes = [
        "what is ",
        "what are ",
        "explain ",
        "tell me about ",
        "define ",
        "meaning of ",
        "how does ",
        "how do "
    ]

    question_lower = question.lower()

    for prefix in prefixes:

        if question_lower.startswith(prefix):

            topic = question[
                len(prefix):
            ].strip()

            topic = topic.rstrip(
                "?.!"
            )

            if topic:
                return topic

    return question.rstrip("?.!")


# ============================================================
# BUILD CONTEXTUAL QUESTION
# ============================================================

def build_contextual_question(
    conversation_id: str,
    current_message: str
):
    """
    Build a better RAG query for follow-up questions.
    """

    current_message = current_message.strip()

    if not current_message:
        return current_message

    previous_question = get_last_user_message(
        conversation_id
    )

    # First message
    if not previous_question:
        return current_message

    # Normal independent question
    if not needs_conversation_context(
        current_message
    ):
        return current_message

    topic = extract_topic_from_question(
        previous_question
    )

    if not topic:
        return current_message

    current_lower = current_message.lower()

    # ========================================================
    # BENEFITS
    # ========================================================

    if (
        "benefits" in current_lower
        or "advantages" in current_lower
        or "pros" in current_lower
    ):
        return (
            f"What are the benefits and advantages "
            f"of {topic}?"
        )

    # ========================================================
    # DISADVANTAGES
    # ========================================================

    if (
        "disadvantages" in current_lower
        or "drawbacks" in current_lower
        or "cons" in current_lower
    ):
        return (
            f"What are the disadvantages and "
            f"drawbacks of {topic}?"
        )

    # ========================================================
    # EXPLAIN IT
    # ========================================================

    if (
        "explain it" in current_lower
        or "explain this" in current_lower
        or "explain that" in current_lower
    ):
        return (
            f"Explain {topic} clearly and simply. "
            f"{current_message}"
        )

    # ========================================================
    # TELL ME MORE
    # ========================================================

    if (
        "tell me more" in current_lower
        or "explain more" in current_lower
        or "more about" in current_lower
        or "go on" in current_lower
        or "continue" in current_lower
    ):
        return (
            f"Tell me more about {topic}. "
            f"{current_message}"
        )

    # ========================================================
    # LANGUAGE REQUEST
    # ========================================================

    language_phrases = [
        "in telugu",
        "in hindi",
        "in tamil",
        "in kannada",
        "in malayalam",
        "in english",
    ]

    for phrase in language_phrases:

        if phrase in current_lower:

            return (
                f"Explain {topic}. "
                f"{current_message}"
            )

    # ========================================================
    # GENERAL FOLLOW-UP
    # ========================================================

    return (
        f"Regarding {topic}: "
        f"{current_message}"
    )