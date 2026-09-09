from unittest.mock import MagicMock, patch

import pytest

from app.services.llm.gemini_provider import GeminiProvider


@pytest.mark.anyio
async def test_gemini_provider_returns_response():

    mock_response = MagicMock()
    mock_response.text = "An ETF is an exchange-traded fund."

    with patch(
        "app.services.llm.gemini_provider.genai.Client"
    ) as mock_client_class:

        mock_client = mock_client_class.return_value

        mock_client.models.generate_content.return_value = (
            mock_response
        )

        provider = GeminiProvider()

        result = await provider.generate(
            [
                {
                    "role": "user",
                    "content": "What is an ETF?",
                }
            ]
        )

        assert result == (
            "An ETF is an exchange-traded fund."
        )

        mock_client.models.generate_content.assert_called_once()