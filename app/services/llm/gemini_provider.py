# import os
# import time
# from typing import AsyncIterator

# from google import genai
# from google.genai import errors

# from app.services.llm.base import LLMProvider
# from app.services.llm_cost_service import LLMCostService


# class GeminiProvider(LLMProvider):
#     """
#     Gemini LLM provider with async streaming
#     and optional token-cost tracking.
#     """

#     def __init__(
#         self,
#         cost_service: LLMCostService | None = None,
#     ) -> None:

#         api_key = os.getenv("GEMINI_API_KEY")

#         if not api_key:
#             raise RuntimeError(
#                 "GEMINI_API_KEY is not configured"
#             )

#         self.client = genai.Client(
#             api_key=api_key
#         )

#         self.model = os.getenv(
#             "GEMINI_MODEL",
#             "gemini-3.5-flash-lite",
#         )

#         self.cost_service = cost_service

#         print(
#             f"[GEMINI DEBUG] Provider initialized "
#             f"model={self.model}"
#         )

#     # ==================================================
#     # NON-STREAMING GENERATION
#     # ==================================================

#     async def generate(
#         self,
#         messages: list[dict],
#     ) -> str:
#         """
#         Generate a complete response from Gemini.
#         """

#         prompt = self._build_prompt(messages)

#         start_time = time.perf_counter()

#         try:

#             response = (
#                 await self.client.aio.models.generate_content(
#                     model=self.model,
#                     contents=prompt,
#                 )
#             )

#         except errors.ServerError as exc:

#             print(
#                 f"[GEMINI ERROR] Server error "
#                 f"model={self.model}: {exc}"
#             )

#             raise RuntimeError(
#                 "Gemini service is temporarily "
#                 "unavailable. Please try again."
#             ) from exc

#         except Exception as exc:

#             print(
#                 f"[GEMINI ERROR] Generation failed: "
#                 f"{exc}"
#             )

#             raise RuntimeError(
#                 "Gemini generation failed."
#             ) from exc

#         latency_ms = (
#             time.perf_counter()
#             - start_time
#         ) * 1000

#         if not response.text:
#             raise RuntimeError(
#                 "Gemini returned an empty response"
#             )

#         self._record_usage(
#             response=response,
#             latency_ms=latency_ms,
#         )

#         return response.text

#     # ==================================================
#     # ASYNC STREAMING
#     # ==================================================

#     async def stream(
#         self,
#         messages: list[dict],
#     ) -> AsyncIterator[str]:
#         """
#         Stream Gemini response asynchronously.

#         Handles temporary Gemini 503 errors without
#         allowing the ASGI streaming response to crash.
#         """

#         prompt = self._build_prompt(messages)

#         start_time = time.perf_counter()

#         first_chunk = True

#         print(
#             f"[GEMINI DEBUG] Starting stream "
#             f"model={self.model}"
#         )

#         try:

#             response = (
#                 await self.client.aio.models
#                 .generate_content_stream(
#                     model=self.model,
#                     contents=prompt,
#                 )
#             )

#             async for chunk in response:

#                 if not chunk.text:
#                     continue

#                 if first_chunk:

#                     first_chunk = False

#                     ttft_ms = (
#                         time.perf_counter()
#                         - start_time
#                     ) * 1000

#                     print(
#                         f"[GEMINI DEBUG] "
#                         f"First chunk: "
#                         f"{ttft_ms:.2f} ms"
#                     )

#                 yield chunk.text

#         except errors.ServerError as exc:

#             print(
#                 f"[GEMINI ERROR] "
#                 f"Gemini server unavailable: "
#                 f"{exc}"
#             )

#             # The HTTP streaming response has already
#             # started with status 200, so we cannot
#             # change the HTTP status here.
#             #
#             # Return a controlled message instead of
#             # crashing the ASGI streaming response.

#             yield (
#                 "\n[AI service temporarily unavailable. "
#                 "Please try again in a moment.]\n"
#             )

#             return

#         except Exception as exc:

#             print(
#                 f"[GEMINI ERROR] "
#                 f"Streaming failed: "
#                 f"{exc}"
#             )

#             yield (
#                 "\n[AI response could not be generated. "
#                 "Please try again.]\n"
#             )

#             return

#     # ==================================================
#     # USAGE / COST TRACKING
#     # ==================================================

#     def _record_usage(
#         self,
#         response,
#         latency_ms: float | None = None,
#     ) -> None:
#         """
#         Record Gemini token usage and latency.
#         """

#         if self.cost_service is None:
#             return

#         usage = response.usage_metadata

#         if usage is None:
#             return

#         self.cost_service.record_usage(
#             model=self.model,
#             prompt_tokens=(
#                 usage.prompt_token_count or 0
#             ),
#             completion_tokens=(
#                 usage.candidates_token_count or 0
#             ),
#             thoughts_tokens=(
#                 usage.thoughts_token_count or 0
#             ),
#             tool_use_prompt_tokens=(
#                 usage.tool_use_prompt_token_count or 0
#             ),
#             total_tokens=(
#                 usage.total_token_count or 0
#             ),
#             latency_ms=latency_ms,
#         )

#     # ==================================================
#     # PROMPT BUILDER
#     # ==================================================

#     @staticmethod
#     def _build_prompt(
#         messages: list[dict],
#     ) -> str:
#         """
#         Convert chat messages into Gemini prompt.
#         """

#         parts = []

#         for message in messages:

#             role = message.get(
#                 "role",
#                 "user",
#             )

#             content = message.get(
#                 "content",
#                 "",
#             )

#             parts.append(
#                 f"{role.upper()}: {content}"
#             )

#         return "\n".join(parts)

# import os
# import time
# from typing import AsyncIterator

# from google import genai
# from google.genai import errors
# from google.genai import types

# from app.services.llm.base import LLMProvider
# from app.services.llm_cost_service import LLMCostService


# class GeminiProvider(LLMProvider):
#     """
#     Optimized Gemini LLM provider.

#     Features:
#     - Reuses one Gemini client
#     - Async streaming
#     - Minimal generation configuration
#     - Explicitly disables unnecessary tools/function calling
#     - TTFT measurement
#     - Total generation timing
#     - Token/cost tracking
#     - Controlled provider failures
#     """

#     def __init__(
#         self,
#         cost_service: LLMCostService | None = None,
#     ) -> None:

#         api_key = os.getenv("GEMINI_API_KEY")

#         if not api_key:
#             raise RuntimeError(
#                 "GEMINI_API_KEY is not configured"
#             )

#         # --------------------------------------------------
#         # Reuse ONE client for the lifetime of the provider.
#         # --------------------------------------------------

#         self.client = genai.Client(
#             api_key=api_key,
#         )

#         # --------------------------------------------------
#         # Current model
#         # --------------------------------------------------

#         self.model = os.getenv(
#             "GEMINI_MODEL",
#             "gemini-3.5-flash-lite",
#         )

#         self.cost_service = cost_service

#         # --------------------------------------------------
#         # Generation limits
#         # --------------------------------------------------

#         self.max_output_tokens = int(
#             os.getenv(
#                 "GEMINI_MAX_OUTPUT_TOKENS",
#                 "512",
#             )
#         )

#         self.temperature = float(
#             os.getenv(
#                 "GEMINI_TEMPERATURE",
#                 "0.2",
#             )
#         )

#         print(
#             "[GEMINI DEBUG] Provider initialized "
#             f"model={self.model} "
#             f"max_output_tokens={self.max_output_tokens} "
#             f"temperature={self.temperature}"
#         )

#     # ==================================================
#     # NON-STREAMING GENERATION
#     # ==================================================

#     async def generate(
#         self,
#         messages: list[dict],
#     ) -> str:
#         """
#         Generate a complete response from Gemini.
#         """

#         prompt = self._build_prompt(messages)

#         start_time = time.perf_counter()

#         print(
#             "[GEMINI DEBUG] Starting generation "
#             f"model={self.model} "
#             f"prompt_chars={len(prompt)}"
#         )

#         try:

#             response = (
#                 await self.client.aio.models.generate_content(
#                     model=self.model,
#                     contents=prompt,
#                     config=self._generation_config(),
#                 )
#             )

#         except errors.ServerError as exc:

#             latency_ms = (
#                 time.perf_counter()
#                 - start_time
#             ) * 1000

#             print(
#                 "[GEMINI ERROR] Server error "
#                 f"model={self.model} "
#                 f"latency={latency_ms:.2f} ms: "
#                 f"{exc}"
#             )

#             raise RuntimeError(
#                 "Gemini service is temporarily "
#                 "unavailable. Please try again."
#             ) from exc

#         except Exception as exc:

#             latency_ms = (
#                 time.perf_counter()
#                 - start_time
#             ) * 1000

#             print(
#                 "[GEMINI ERROR] Generation failed "
#                 f"latency={latency_ms:.2f} ms: "
#                 f"{exc}"
#             )

#             raise RuntimeError(
#                 "Gemini generation failed."
#             ) from exc

#         latency_ms = (
#             time.perf_counter()
#             - start_time
#         ) * 1000

#         if not response.text:
#             raise RuntimeError(
#                 "Gemini returned an empty response"
#             )

#         print(
#             "[GEMINI DEBUG] Generation completed "
#             f"latency={latency_ms:.2f} ms"
#         )

#         self._record_usage(
#             response=response,
#             latency_ms=latency_ms,
#         )

#         return response.text

#     # ==================================================
#     # ASYNC STREAMING
#     # ==================================================

#     async def stream(
#         self,
#         messages: list[dict],
#     ) -> AsyncIterator[str]:
#         """
#         Optimized asynchronous Gemini streaming.

#         The important performance path is:

#             prompt creation
#                   ↓
#             Gemini request
#                   ↓
#             first chunk / TTFT
#                   ↓
#             remaining chunks
#         """

#         prompt_start = time.perf_counter()

#         prompt = self._build_prompt(messages)

#         prompt_build_ms = (
#             time.perf_counter()
#             - prompt_start
#         ) * 1000

#         request_start = time.perf_counter()

#         first_chunk = True
#         chunk_count = 0
#         total_chars = 0

#         print(
#             "[GEMINI DEBUG] Starting stream "
#             f"model={self.model}"
#         )

#         print(
#             "[GEMINI DEBUG] Prompt prepared "
#             f"chars={len(prompt)} "
#             f"build={prompt_build_ms:.2f} ms"
#         )

#         try:

#             # --------------------------------------------------
#             # IMPORTANT:
#             #
#             # No tools are supplied.
#             # This prevents unnecessary automatic
#             # function-calling/tool overhead.
#             #
#             # We also keep generation configuration minimal.
#             # --------------------------------------------------

#             response = (
#                 await self.client.aio.models
#                 .generate_content_stream(
#                     model=self.model,
#                     contents=prompt,
#                     config=self._generation_config(),
#                 )
#             )

#             async for chunk in response:

#                 text = chunk.text

#                 if not text:
#                     continue

#                 chunk_count += 1
#                 total_chars += len(text)

#                 if first_chunk:

#                     first_chunk = False

#                     ttft_ms = (
#                         time.perf_counter()
#                         - request_start
#                     ) * 1000

#                     total_ttft_ms = (
#                         time.perf_counter()
#                         - request_start
#                     ) * 1000

#                     print(
#                         "[GEMINI DEBUG] "
#                         f"First chunk: "
#                         f"{ttft_ms:.2f} ms"
#                     )

#                     print(
#                         "[GEMINI DEBUG] "
#                         f"TTFT={total_ttft_ms:.2f} ms "
#                         f"chunk={chunk_count}"
#                     )

#                 yield text

#             total_ms = (
#                 time.perf_counter()
#                 - request_start
#             ) * 1000

#             print(
#                 "[GEMINI DEBUG] Stream completed "
#                 f"total={total_ms:.2f} ms "
#                 f"chunks={chunk_count} "
#                 f"chars={total_chars}"
#             )

#         except errors.ServerError as exc:

#             elapsed_ms = (
#                 time.perf_counter()
#                 - request_start
#             ) * 1000

#             print(
#                 "[GEMINI ERROR] "
#                 "Gemini server unavailable "
#                 f"after={elapsed_ms:.2f} ms: "
#                 f"{exc}"
#             )

#             # The HTTP response has already started,
#             # therefore return a controlled message.
#             yield (
#                 "\n[AI service temporarily unavailable. "
#                 "Please try again in a moment.]\n"
#             )

#             return

#         except Exception as exc:

#             elapsed_ms = (
#                 time.perf_counter()
#                 - request_start
#             ) * 1000

#             print(
#                 "[GEMINI ERROR] "
#                 "Streaming failed "
#                 f"after={elapsed_ms:.2f} ms: "
#                 f"{type(exc).__name__}: {exc}"
#             )

#             yield (
#                 "\n[AI response could not be generated. "
#                 "Please try again.]\n"
#             )

#             return

#     # ==================================================
#     # GENERATION CONFIGURATION
#     # ==================================================

#     def _generation_config(self) -> types.GenerateContentConfig:
#         """
#         Return a deliberately small generation configuration.

#         We are optimizing for:
#         - low latency
#         - predictable output size
#         - no unnecessary tool/function calling
#         """

#         return types.GenerateContentConfig(
#             temperature=self.temperature,
#             max_output_tokens=self.max_output_tokens,
#             candidate_count=1,
#         )

#     # ==================================================
#     # USAGE / COST TRACKING
#     # ==================================================

#     def _record_usage(
#         self,
#         response,
#         latency_ms: float | None = None,
#     ) -> None:
#         """
#         Record Gemini token usage and latency.
#         """

#         if self.cost_service is None:
#             return

#         usage = getattr(
#             response,
#             "usage_metadata",
#             None,
#         )

#         if usage is None:
#             return

#         self.cost_service.record_usage(
#             model=self.model,

#             prompt_tokens=(
#                 getattr(
#                     usage,
#                     "prompt_token_count",
#                     0,
#                 )
#                 or 0
#             ),

#             completion_tokens=(
#                 getattr(
#                     usage,
#                     "candidates_token_count",
#                     0,
#                 )
#                 or 0
#             ),

#             thoughts_tokens=(
#                 getattr(
#                     usage,
#                     "thoughts_token_count",
#                     0,
#                 )
#                 or 0
#             ),

#             tool_use_prompt_tokens=(
#                 getattr(
#                     usage,
#                     "tool_use_prompt_token_count",
#                     0,
#                 )
#                 or 0
#             ),

#             total_tokens=(
#                 getattr(
#                     usage,
#                     "total_token_count",
#                     0,
#                 )
#                 or 0
#             ),

#             latency_ms=latency_ms,
#         )

#     # ==================================================
#     # PROMPT BUILDER
#     # ==================================================

#     @staticmethod
#     def _build_prompt(
#         messages: list[dict],
#     ) -> str:
#         """
#         Convert chat messages into a compact Gemini prompt.
#         """

#         parts: list[str] = []

#         for message in messages:

#             role = message.get(
#                 "role",
#                 "user",
#             )

#             content = message.get(
#                 "content",
#                 "",
#             )

#             if not content:
#                 continue

#             parts.append(
#                 f"{role.upper()}: {content}"
#             )

#         return "\n".join(parts)


import os
import time
from typing import AsyncIterator

from google import genai
from google.genai import errors

from app.services.llm.base import LLMProvider
from app.services.llm_cost_service import LLMCostService


class GeminiProvider(LLMProvider):
    """
    Gemini LLM provider with:

    - Async non-streaming generation
    - Async streaming generation
    - Low-latency streaming configuration
    - Token/cost tracking
    - Latency tracking
    - Graceful Gemini 503 handling
    - Reusable Gemini client
    """

    def __init__(
        self,
        cost_service: LLMCostService | None = None,
    ) -> None:

        # --------------------------------------------------
        # API KEY
        # --------------------------------------------------

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured"
            )

        # --------------------------------------------------
        # REUSABLE GEMINI CLIENT
        # --------------------------------------------------

        self.client = genai.Client(
            api_key=api_key
        )

        # --------------------------------------------------
        # MODEL
        # --------------------------------------------------

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite",
        )

        # --------------------------------------------------
        # COST SERVICE
        # --------------------------------------------------

        self.cost_service = cost_service

        print(
            f"[GEMINI DEBUG] Provider initialized "
            f"model={self.model}"
        )

    # ======================================================
    # NON-STREAMING GENERATION
    # ======================================================

    async def generate(
        self,
        messages: list[dict],
    ) -> str:
        """
        Generate a complete Gemini response.

        Used when streaming is not required.
        """

        prompt_start = time.perf_counter()

        prompt = self._build_prompt(messages)

        prompt_build_ms = (
            time.perf_counter() - prompt_start
        ) * 1000

        print(
            f"[GEMINI DEBUG] Prompt prepared "
            f"chars={len(prompt)} "
            f"build={prompt_build_ms:.2f} ms"
        )

        start_time = time.perf_counter()

        try:

            response = (
                await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config={
                        "max_output_tokens": 512,
                        "temperature": 0.2,
                    },
                )
            )

        except errors.ServerError as exc:

            print(
                f"[GEMINI ERROR] Server error "
                f"model={self.model}: {exc}"
            )

            raise RuntimeError(
                "Gemini service is temporarily "
                "unavailable. Please try again."
            ) from exc

        except Exception as exc:

            print(
                f"[GEMINI ERROR] Generation failed: "
                f"{exc}"
            )

            raise RuntimeError(
                "Gemini generation failed."
            ) from exc

        latency_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        if not response.text:

            raise RuntimeError(
                "Gemini returned an empty response"
            )

        print(
            f"[GEMINI DEBUG] Generation completed "
            f"latency={latency_ms:.2f} ms"
        )

        # --------------------------------------------------
        # COST / TOKEN TRACKING
        # --------------------------------------------------

        self._record_usage(
            response=response,
            latency_ms=latency_ms,
        )

        return response.text

    # ======================================================
    # ASYNC STREAMING GENERATION
    # ======================================================

    async def stream(
        self,
        messages: list[dict],
    ) -> AsyncIterator[str]:
        """
        Low-latency Gemini streaming.

        Optimizations:

        1. Reuses a single Gemini client.
        2. Uses streaming generation.
        3. Limits output tokens.
        4. Uses low temperature.
        5. Avoids unnecessary generation configuration.
        6. Measures TTFT precisely.
        7. Handles Gemini 503 errors safely.
        """

        # --------------------------------------------------
        # BUILD PROMPT
        # --------------------------------------------------

        prompt_start = time.perf_counter()

        prompt = self._build_prompt(messages)

        prompt_build_ms = (
            time.perf_counter()
            - prompt_start
        ) * 1000

        print(
            f"[GEMINI DEBUG] Prompt prepared "
            f"chars={len(prompt)} "
            f"build={prompt_build_ms:.2f} ms"
        )

        # --------------------------------------------------
        # START TIMER
        # --------------------------------------------------

        start_time = time.perf_counter()

        first_chunk = True
        chunk_count = 0
        total_chars = 0

        print(
            f"[GEMINI DEBUG] Starting stream "
            f"model={self.model}"
        )

        try:

            # --------------------------------------------------
            # STREAM REQUEST
            # --------------------------------------------------

            request_start = time.perf_counter()

            response = (
                await self.client.aio.models
                .generate_content_stream(
                    model=self.model,
                    contents=prompt,
                    config={
                        "max_output_tokens": 512,
                        "temperature": 0.2,
                    },
                )
            )

            request_ms = (
                time.perf_counter()
                - request_start
            ) * 1000

            print(
                f"[GEMINI DEBUG] "
                f"Stream request created "
                f"in {request_ms:.2f} ms"
            )

            # --------------------------------------------------
            # RECEIVE STREAM
            # --------------------------------------------------

            async for chunk in response:

                text = chunk.text

                if not text:
                    continue

                chunk_count += 1
                total_chars += len(text)

                # --------------------------------------------------
                # FIRST TOKEN / TTFT
                # --------------------------------------------------

                if first_chunk:

                    first_chunk = False

                    ttft_ms = (
                        time.perf_counter()
                        - start_time
                    ) * 1000

                    print(
                        f"[GEMINI DEBUG] "
                        f"First chunk: "
                        f"{ttft_ms:.2f} ms"
                    )

                    if ttft_ms < 1000:

                        print(
                            "[GEMINI DEBUG] "
                            "TTFT TARGET MET: <1000 ms"
                        )

                    else:

                        print(
                            "[GEMINI DEBUG] "
                            "TTFT TARGET NOT MET: "
                            f"{ttft_ms:.2f} ms"
                        )

                # --------------------------------------------------
                # SEND CHUNK
                # --------------------------------------------------

                yield text

            # --------------------------------------------------
            # STREAM COMPLETE
            # --------------------------------------------------

            total_ms = (
                time.perf_counter()
                - start_time
            ) * 1000

            print(
                f"[GEMINI DEBUG] "
                f"Stream completed "
                f"total={total_ms:.2f} ms "
                f"chunks={chunk_count} "
                f"chars={total_chars}"
            )

        # ==================================================
        # GEMINI SERVER ERROR
        # ==================================================

        except errors.ServerError as exc:

            print(
                f"[GEMINI ERROR] "
                f"Gemini server unavailable: "
                f"{exc}"
            )

            # Streaming responses normally already have
            # HTTP 200 once the endpoint starts.
            #
            # Therefore we return a controlled message
            # instead of allowing the ASGI stream to crash.

            yield (
                "\n[AI service temporarily unavailable. "
                "Please try again in a moment.]\n"
            )

            return

        # ==================================================
        # OTHER ERRORS
        # ==================================================

        except Exception as exc:

            print(
                f"[GEMINI ERROR] "
                f"Streaming failed: "
                f"{type(exc).__name__}: {exc}"
            )

            yield (
                "\n[AI response could not be generated. "
                "Please try again.]\n"
            )

            return

    # ======================================================
    # TOKEN / COST TRACKING
    # ======================================================

    def _record_usage(
        self,
        response,
        latency_ms: float | None = None,
    ) -> None:
        """
        Record Gemini token usage and latency.

        Cost tracking is optional. If no cost service
        is configured, this method does nothing.
        """

        if self.cost_service is None:
            return

        usage = getattr(
            response,
            "usage_metadata",
            None,
        )

        if usage is None:
            return

        self.cost_service.record_usage(
            model=self.model,

            prompt_tokens=(
                getattr(
                    usage,
                    "prompt_token_count",
                    0,
                )
                or 0
            ),

            completion_tokens=(
                getattr(
                    usage,
                    "candidates_token_count",
                    0,
                )
                or 0
            ),

            thoughts_tokens=(
                getattr(
                    usage,
                    "thoughts_token_count",
                    0,
                )
                or 0
            ),

            tool_use_prompt_tokens=(
                getattr(
                    usage,
                    "tool_use_prompt_token_count",
                    0,
                )
                or 0
            ),

            total_tokens=(
                getattr(
                    usage,
                    "total_token_count",
                    0,
                )
                or 0
            ),

            latency_ms=latency_ms,
        )

    # ======================================================
    # PROMPT BUILDER
    # ======================================================

    @staticmethod
    def _build_prompt(
        messages: list[dict],
    ) -> str:
        """
        Convert application chat messages into
        a compact Gemini prompt.
        """

        parts: list[str] = []

        for message in messages:

            role = message.get(
                "role",
                "user",
            )

            content = message.get(
                "content",
                "",
            )

            if not content:
                continue

            parts.append(
                f"{role.upper()}: {content}"
            )

        return "\n".join(parts)