import json
from typing import Any

import redis.asyncio as redis


MAX_MESSAGES = 10
CHAT_TTL_SECONDS = 14_400  # 4 hours


class ConversationService:
    """
    Handles temporary conversation history and user profile
    using asynchronous Redis.

    Redis keys:

        chat:{user_id}:{session_id}
            -> latest 10 conversation messages

        chat:{user_id}:{session_id}:profile
            -> user profile

    Both use a 4-hour TTL.
    """

    def __init__(self, redis_client: redis.Redis) -> None:
        self.redis = redis_client

    # ==========================================================
    # KEY BUILDERS
    # ==========================================================

    @staticmethod
    def build_key(
        user_id: str,
        session_id: str,
    ) -> str:

        if not isinstance(user_id, str):
            raise TypeError("user_id must be a string")

        if not isinstance(session_id, str):
            raise TypeError("session_id must be a string")

        if not user_id.strip():
            raise ValueError("user_id cannot be empty")

        if not session_id.strip():
            raise ValueError("session_id cannot be empty")

        return f"chat:{user_id.strip()}:{session_id.strip()}"

    @staticmethod
    def build_profile_key(
        user_id: str,
        session_id: str,
    ) -> str:

        return (
            ConversationService.build_key(
                user_id=user_id,
                session_id=session_id,
            )
            + ":profile"
        )

    # ==========================================================
    # MESSAGE VALIDATION
    # ==========================================================

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

        role = message["role"]
        content = message["content"]

        if not isinstance(role, str):
            raise TypeError(
                "message role must be a string"
            )

        if not isinstance(content, str):
            raise TypeError(
                "message content must be a string"
            )

        if not role.strip():
            raise ValueError(
                "message role cannot be empty"
            )

        if role not in {"user", "assistant"}:
            raise ValueError(
                "message role must be "
                "'user' or 'assistant'"
            )

        if not content.strip():
            raise ValueError(
                "message content cannot be empty"
            )

    # ==========================================================
    # GET HISTORY
    # ==========================================================

    async def get_history(
        self,
        user_id: str,
        session_id: str,
    ) -> list[dict[str, str]]:

        key = self.build_key(
            user_id=user_id,
            session_id=session_id,
        )

        raw = await self.redis.get(key)

        if raw is None:
            return []

        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")

        if not isinstance(raw, str):
            raise ValueError(
                "Invalid conversation data in Redis"
            )

        try:
            history = json.loads(raw)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Invalid conversation data in Redis"
            ) from exc

        if not isinstance(history, list):
            raise ValueError(
                "Conversation history must be a list"
            )

        validated_history: list[dict[str, str]] = []

        for message in history:

            self._validate_message(message)

            validated_history.append(
                {
                    "role": message["role"],
                    "content": message["content"],
                }
            )

        return validated_history[-MAX_MESSAGES:]

    # ==========================================================
    # ADD MESSAGE
    # ==========================================================

    async def add_message(
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

        history = await self.get_history(
            user_id=user_id,
            session_id=session_id,
        )

        history.append(
            {
                "role": role,
                "content": content,
            }
        )

        # Keep only latest 10 messages.
        history = history[-MAX_MESSAGES:]

        await self.redis.set(
            key,
            json.dumps(history),
            ex=CHAT_TTL_SECONDS,
        )

        return history

    # ==========================================================
    # SET PROFILE
    # ==========================================================

    async def set_profile(
        self,
        user_id: str,
        session_id: str,
        profile: dict[str, Any],
    ) -> None:

        if not isinstance(profile, dict):
            raise TypeError(
                "profile must be a dictionary"
            )

        key = self.build_profile_key(
            user_id=user_id,
            session_id=session_id,
        )

        await self.redis.set(
            key,
            json.dumps(profile),
            ex=CHAT_TTL_SECONDS,
        )

    # ==========================================================
    # GET PROFILE
    # ==========================================================

    async def get_profile(
        self,
        user_id: str,
        session_id: str,
    ) -> dict[str, Any] | None:

        key = self.build_profile_key(
            user_id=user_id,
            session_id=session_id,
        )

        raw = await self.redis.get(key)

        if raw is None:
            return None

        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")

        if not isinstance(raw, str):
            raise ValueError(
                "Invalid user profile data in Redis"
            )

        try:
            profile = json.loads(raw)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Invalid user profile data in Redis"
            ) from exc

        if not isinstance(profile, dict):
            raise ValueError(
                "User profile must be a dictionary"
            )

        return profile

    # ==========================================================
    # CLEAR PROFILE
    # ==========================================================

    async def clear_profile(
        self,
        user_id: str,
        session_id: str,
    ) -> None:

        key = self.build_profile_key(
            user_id=user_id,
            session_id=session_id,
        )

        await self.redis.delete(key)

    # ==========================================================
    # CLEAR HISTORY
    # ==========================================================

    async def clear_history(
        self,
        user_id: str,
        session_id: str,
    ) -> None:

        key = self.build_key(
            user_id=user_id,
            session_id=session_id,
        )

        await self.redis.delete(key)

    # ==========================================================
    # CLEAR SESSION
    # ==========================================================

    async def clear_session(
        self,
        user_id: str,
        session_id: str,
    ) -> None:

        history_key = self.build_key(
            user_id=user_id,
            session_id=session_id,
        )

        profile_key = self.build_profile_key(
            user_id=user_id,
            session_id=session_id,
        )

        await self.redis.delete(
            history_key,
            profile_key,
        )

    # ==========================================================
    # HEALTH CHECK
    # ==========================================================

    async def ping(self) -> bool:

        try:
            result = await self.redis.ping()
            return bool(result)

        except Exception:
            return False