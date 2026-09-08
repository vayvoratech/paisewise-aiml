import json
from typing import Any

import redis


MAX_MESSAGES = 10
CHAT_TTL_SECONDS = 14_400  # 4 hours


class ConversationService:
    """
    Handles short-lived conversation history and
    user profile context using Redis.

    Redis keys:

        chat:{user_id}:{session_id}
            -> latest 10 conversation messages

        chat:{user_id}:{session_id}:profile
            -> user profile for the session

    Both conversation history and profile have
    a 4-hour TTL.

    PostgreSQL is not used here.
    """

    def __init__(
        self,
        redis_client: redis.Redis,
    ) -> None:
        self.redis = redis_client

    # --------------------------------------------------
    # Build conversation Redis key
    # --------------------------------------------------

    @staticmethod
    def build_key(
        user_id: str,
        session_id: str,
    ) -> str:

        if not user_id or not user_id.strip():
            raise ValueError(
                "user_id cannot be empty"
            )

        if not session_id or not session_id.strip():
            raise ValueError(
                "session_id cannot be empty"
            )

        return (
            f"chat:{user_id.strip()}:"
            f"{session_id.strip()}"
        )

    # --------------------------------------------------
    # Build profile Redis key
    # --------------------------------------------------

    @staticmethod
    def build_profile_key(
        user_id: str,
        session_id: str,
    ) -> str:

        base_key = ConversationService.build_key(
            user_id=user_id,
            session_id=session_id,
        )

        return f"{base_key}:profile"

    # --------------------------------------------------
    # Validate message
    # --------------------------------------------------

    @staticmethod
    def _validate_message(
        message: dict[str, Any],
    ) -> None:

        if not isinstance(message, dict):
            raise TypeError(
                "message must be a dictionary"
            )

        if "role" not in message:
            raise ValueError(
                "message must contain role"
            )

        if "content" not in message:
            raise ValueError(
                "message must contain content"
            )

        if not isinstance(
            message["role"],
            str,
        ):
            raise TypeError(
                "message role must be a string"
            )

        if not isinstance(
            message["content"],
            str,
        ):
            raise TypeError(
                "message content must be a string"
            )

        if not message["role"].strip():
            raise ValueError(
                "message role cannot be empty"
            )

        if message["role"] not in {
            "user",
            "assistant",
        }:
            raise ValueError(
                "message role must be "
                "'user' or 'assistant'"
            )

        if not message["content"].strip():
            raise ValueError(
                "message content cannot be empty"
            )

    # --------------------------------------------------
    # Get conversation history
    # --------------------------------------------------

    def get_history(
        self,
        user_id: str,
        session_id: str,
    ) -> list[dict[str, str]]:

        key = self.build_key(
            user_id=user_id,
            session_id=session_id,
        )

        raw = self.redis.get(key)

        if raw is None:
            return []

        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")

        try:
            history = json.loads(raw)
        except (
            TypeError,
            json.JSONDecodeError,
        ) as exc:
            raise ValueError(
                "Invalid conversation data in Redis"
            ) from exc

        if not isinstance(history, list):
            raise ValueError(
                "Conversation history must be a list"
            )

        validated_history: list[
            dict[str, str]
        ] = []

        for message in history:
            self._validate_message(message)

            validated_history.append(
                {
                    "role": message["role"],
                    "content": message["content"],
                }
            )

        return validated_history[-MAX_MESSAGES:]

    # --------------------------------------------------
    # Add conversation message
    # --------------------------------------------------

    def add_message(
        self,
        user_id: str,
        session_id: str,
        role: str,
        content: str,
    ) -> list[dict[str, str]]:

        message = {
            "role": role,
            "content": content,
        }

        self._validate_message(message)

        key = self.build_key(
            user_id=user_id,
            session_id=session_id,
        )

        history = self.get_history(
            user_id=user_id,
            session_id=session_id,
        )

        history.append(message)

        # Keep only the latest 10 messages.
        history = history[-MAX_MESSAGES:]

        self.redis.set(
            key,
            json.dumps(history),
            ex=CHAT_TTL_SECONDS,
        )

        return history

    # --------------------------------------------------
    # Store user profile
    # --------------------------------------------------

    def set_profile(
        self,
        user_id: str,
        session_id: str,
        profile: dict[str, Any],
    ) -> None:
        """
        Store user profile for the current session.

        Profile is stored separately from conversation
        history and therefore does not consume one of
        the 10 conversation-message slots.
        """

        if not isinstance(profile, dict):
            raise TypeError(
                "profile must be a dictionary"
            )

        key = self.build_profile_key(
            user_id=user_id,
            session_id=session_id,
        )

        self.redis.set(
            key,
            json.dumps(profile),
            ex=CHAT_TTL_SECONDS,
        )

    # --------------------------------------------------
    # Get user profile
    # --------------------------------------------------

    def get_profile(
        self,
        user_id: str,
        session_id: str,
    ) -> dict[str, Any] | None:
        """
        Retrieve the user profile for the session.

        Returns None when no profile exists.
        """

        key = self.build_profile_key(
            user_id=user_id,
            session_id=session_id,
        )

        raw = self.redis.get(key)

        if raw is None:
            return None

        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")

        try:
            profile = json.loads(raw)
        except (
            TypeError,
            json.JSONDecodeError,
        ) as exc:
            raise ValueError(
                "Invalid user profile data in Redis"
            ) from exc

        if not isinstance(profile, dict):
            raise ValueError(
                "User profile must be a dictionary"
            )

        return profile

    # --------------------------------------------------
    # Clear profile
    # --------------------------------------------------

    def clear_profile(
        self,
        user_id: str,
        session_id: str,
    ) -> None:

        key = self.build_profile_key(
            user_id=user_id,
            session_id=session_id,
        )

        self.redis.delete(key)

    # --------------------------------------------------
    # Clear conversation history
    # --------------------------------------------------

    def clear_history(
        self,
        user_id: str,
        session_id: str,
    ) -> None:

        key = self.build_key(
            user_id=user_id,
            session_id=session_id,
        )

        self.redis.delete(key)

    # --------------------------------------------------
    # Clear complete session
    # --------------------------------------------------

    def clear_session(
        self,
        user_id: str,
        session_id: str,
    ) -> None:
        """
        Clear both conversation history and
        user profile for the session.
        """

        history_key = self.build_key(
            user_id=user_id,
            session_id=session_id,
        )

        profile_key = self.build_profile_key(
            user_id=user_id,
            session_id=session_id,
        )

        self.redis.delete(
            history_key,
            profile_key,
        )