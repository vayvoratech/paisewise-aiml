from unittest.mock import MagicMock

import pytest

from app.services.ai_prompt_service import (
    AIPromptService,
)


@pytest.fixture
def repository():
    return MagicMock()


@pytest.fixture
def service(repository):
    return AIPromptService(
        repository=repository
    )


def test_get_active_prompt(service, repository):
    repository.get_active_prompt.return_value = {
        "prompt_key": "chat_system_prompt",
        "version": 2,
        "prompt_text": "Active prompt",
        "is_active": True,
    }

    result = service.get_active_prompt(
        "chat_system_prompt"
    )

    assert result.prompt_key == "chat_system_prompt"
    assert result.version == 2
    assert result.prompt_text == "Active prompt"
    assert result.is_active is True

    repository.get_active_prompt.assert_called_once_with(
        "chat_system_prompt"
    )


def test_create_prompt_version_without_activation(
    service,
    repository,
):
    repository.get_next_version.return_value = 3

    repository.create_prompt.return_value = {
        "prompt_key": "chat_system_prompt",
        "version": 3,
        "prompt_text": "New prompt",
        "is_active": False,
    }

    result = service.create_prompt_version(
        prompt_key="chat_system_prompt",
        prompt_text="  New prompt  ",
    )

    assert result.version == 3
    assert result.prompt_text == "New prompt"
    assert result.is_active is False

    repository.get_next_version.assert_called_once_with(
        "chat_system_prompt"
    )

    repository.create_prompt.assert_called_once_with(
        prompt_key="chat_system_prompt",
        version=3,
        prompt_text="New prompt",
        is_active=False,
    )


def test_create_prompt_version_with_activation(
    service,
    repository,
):
    repository.get_next_version.return_value = 2

    repository.create_prompt.return_value = {
        "prompt_key": "chat_system_prompt",
        "version": 2,
        "prompt_text": "New active prompt",
        "is_active": False,
    }

    repository.activate_prompt.return_value = {
        "prompt_key": "chat_system_prompt",
        "version": 2,
        "prompt_text": "New active prompt",
        "is_active": True,
    }

    result = service.create_prompt_version(
        prompt_key="chat_system_prompt",
        prompt_text="New active prompt",
        activate=True,
    )

    assert result.version == 2
    assert result.is_active is True

    repository.activate_prompt.assert_called_once_with(
        prompt_key="chat_system_prompt",
        version=2,
    )


def test_activate_prompt(service, repository):
    repository.activate_prompt.return_value = {
        "prompt_key": "chat_system_prompt",
        "version": 4,
        "prompt_text": "Version 4",
        "is_active": True,
    }

    result = service.activate_prompt(
        prompt_key="chat_system_prompt",
        version=4,
    )

    assert result.version == 4
    assert result.is_active is True

    repository.activate_prompt.assert_called_once_with(
        prompt_key="chat_system_prompt",
        version=4,
    )


def test_get_prompt_version(service, repository):
    repository.get_prompt_version.return_value = {
        "prompt_key": "chat_system_prompt",
        "version": 3,
        "prompt_text": "Version 3",
        "is_active": False,
    }

    result = service.get_prompt_version(
        prompt_key="chat_system_prompt",
        version=3,
    )

    assert result.version == 3
    assert result.prompt_text == "Version 3"
    assert result.is_active is False


@pytest.mark.parametrize(
    "prompt_key",
    ["", "   "],
)
def test_empty_prompt_key_is_rejected(
    service,
    prompt_key,
):
    with pytest.raises(
        ValueError,
        match="prompt_key cannot be empty",
    ):
        service.get_active_prompt(prompt_key)


def test_non_string_prompt_key_is_rejected(service):
    with pytest.raises(
        TypeError,
        match="prompt_key must be a string",
    ):
        service.get_active_prompt(None)


@pytest.mark.parametrize(
    "prompt_text",
    ["", "   "],
)
def test_empty_prompt_text_is_rejected(
    service,
    prompt_text,
):
    with pytest.raises(
        ValueError,
        match="prompt_text cannot be empty",
    ):
        service.create_prompt_version(
            prompt_key="chat_system_prompt",
            prompt_text=prompt_text,
        )


def test_non_string_prompt_text_is_rejected(service):
    with pytest.raises(
        TypeError,
        match="prompt_text must be a string",
    ):
        service.create_prompt_version(
            prompt_key="chat_system_prompt",
            prompt_text=None,
        )


@pytest.mark.parametrize(
    "version",
    [0, -1],
)
def test_invalid_version_is_rejected(
    service,
    version,
):
    with pytest.raises(
        ValueError,
        match="version must be greater than 0",
    ):
        service.activate_prompt(
            prompt_key="chat_system_prompt",
            version=version,
        )


def test_non_integer_version_is_rejected(service):
    with pytest.raises(
        TypeError,
        match="version must be an integer",
    ):
        service.activate_prompt(
            prompt_key="chat_system_prompt",
            version="2",
        )