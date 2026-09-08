from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Abstract interface for an LLM provider.

    ChatService depends on this interface rather than
    a specific LLM vendor.
    """

    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:
        """
        Generate a response from the supplied messages.
        """
        raise NotImplementedError
from abc import ABC, abstractmethod
from typing import AsyncIterator


class LLMProvider(ABC):
    """
    Abstract interface for an LLM provider.

    ChatService depends on this interface rather than
    a specific LLM vendor.
    """

    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:
        """
        Generate a complete response.
        """
        raise NotImplementedError

    @abstractmethod
    async def stream(
        self,
        messages: list[dict[str, str]],
    ) -> AsyncIterator[str]:
        """
        Stream the response incrementally.
        """
        raise NotImplementedError