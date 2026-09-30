from __future__ import annotations

import asyncio
import logging
import os
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.routes.chat import get_chat_service
from app.core.redis import redis_client
from app.schemas.chat import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ai/chat/jobs",
    tags=["AI Chat Jobs"],
)

STREAM_KEY = "ai:chat:jobs"
GROUP_NAME = "ai-chat-workers"
JOB_KEY_PREFIX = "ai:chat:job:"
JOB_TTL_SECONDS = 60 * 60 * 24

# A pending job can be reclaimed after this many idle milliseconds.
# Set CHAT_JOB_CLAIM_IDLE_MS in the environment to change the value.
CLAIM_IDLE_MS = max(
    60_000,
    int(os.getenv("CHAT_JOB_CLAIM_IDLE_MS", "600000")),
)


class ChatJobAccepted(BaseModel):
    job_id: str
    status: str


class ChatJobStatus(BaseModel):
    job_id: str
    status: str
    result: ChatResponse | None = None
    error: str | None = None


def _job_key(job_id: str) -> str:
    return f"{JOB_KEY_PREFIX}{job_id}"


@router.post(
    "",
    response_model=ChatJobAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_chat_job(request: ChatRequest) -> ChatJobAccepted:
    job_id = str(uuid4())
    job_key = _job_key(job_id)

    # Save the initial state before publishing the job.
    await redis_client.hset(
        job_key,
        mapping={
            "job_id": job_id,
            "status": "queued",
            "result": "",
            "error": "",
        },
    )
    await redis_client.expire(job_key, JOB_TTL_SECONDS)

    try:
        await redis_client.xadd(
            STREAM_KEY,
            {
                "job_id": job_id,
                "payload": request.model_dump_json(),
            },
            maxlen=10000,
            approximate=True,
        )
    except Exception:
        await redis_client.delete(job_key)
        raise

    return ChatJobAccepted(
        job_id=job_id,
        status="queued",
    )


@router.get(
    "/{job_id}",
    response_model=ChatJobStatus,
)
async def get_chat_job(job_id: str) -> ChatJobStatus:
    data = await redis_client.hgetall(_job_key(job_id))

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat job was not found or has expired.",
        )

    result = None
    if data.get("result"):
        result = ChatResponse.model_validate_json(data["result"])

    return ChatJobStatus(
        job_id=data.get("job_id", job_id),
        status=data.get("status", "unknown"),
        result=result,
        error=data.get("error") or None,
    )


class ChatJobWorker:
    """Consumes chat jobs from a Redis stream consumer group."""

    def __init__(
        self,
        redis: Any,
        *,
        stream_key: str = STREAM_KEY,
        group_name: str = GROUP_NAME,
        claim_idle_ms: int = CLAIM_IDLE_MS,
    ) -> None:
        self.redis = redis
        self.stream_key = stream_key
        self.group_name = group_name
        self.claim_idle_ms = claim_idle_ms
        self.consumer_name = str(uuid4())
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        try:
            await self.redis.xgroup_create(
                name=self.stream_key,
                groupname=self.group_name,
                id="0",
                mkstream=True,
            )
        except Exception as exc:
            # Another API instance may already have created the group.
            if "BUSYGROUP" not in str(exc):
                raise

        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task is None:
            return

        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        finally:
            self._task = None

    async def _run(self) -> None:
        while True:
            try:
                # First recover an old pending job, if one exists.
                recovered = await self._claim_pending_job()

                if recovered:
                    stream_id, fields = recovered
                    await self._process(stream_id, fields)
                    continue

                # Otherwise, wait for a new job.
                batches = await self.redis.xreadgroup(
                    groupname=self.group_name,
                    consumername=self.consumer_name,
                    streams={self.stream_key: ">"},
                    count=1,
                    block=2000,
                )

                for _, entries in batches:
                    for stream_id, fields in entries:
                        await self._process(stream_id, fields)

            except asyncio.CancelledError:
                raise
            except Exception:
                # Leave unacknowledged jobs in the pending list so they can
                # be reclaimed and retried after the idle threshold.
                logger.exception("Chat job worker loop encountered an error")
                await asyncio.sleep(1)

    async def _claim_pending_job(
        self,
    ) -> tuple[str, dict[str, str]] | None:
        """
        Claim one message left pending by a stopped or failed worker.

        Redis XAUTOCLAIM requires Redis 6.2 or newer.
        """
        result = await self.redis.xautoclaim(
            name=self.stream_key,
            groupname=self.group_name,
            consumername=self.consumer_name,
            min_idle_time=self.claim_idle_ms,
            start_id="0-0",
            count=1,
        )

        # redis-py returns (next_start_id, messages, deleted_ids).
        if not result or len(result) < 2:
            return None

        messages = result[1]
        if not messages:
            return None

        stream_id, fields = messages[0]
        return stream_id, fields

    async def _process(
        self,
        stream_id: str,
        fields: dict[str, str],
    ) -> None:
        job_id = fields.get("job_id")
        payload = fields.get("payload")

        if not job_id or not payload:
            logger.error("Discarding malformed chat job %s", stream_id)
            await self.redis.xack(
                self.stream_key,
                self.group_name,
                stream_id,
            )
            return

        job_key = _job_key(job_id)

        try:
            await self.redis.hset(
                job_key,
                mapping={
                    "status": "processing",
                    "error": "",
                },
            )

            request = ChatRequest.model_validate_json(payload)
            response = await get_chat_service().process_chat(request)

            await self.redis.hset(
                job_key,
                mapping={
                    "status": "completed",
                    "result": response.model_dump_json(),
                    "error": "",
                },
            )
            await self.redis.expire(job_key, JOB_TTL_SECONDS)

        except asyncio.CancelledError:
            # Do not acknowledge on shutdown; another worker can reclaim it.
            raise
        except Exception as exc:
            logger.exception("Chat job %s failed", job_id)

            await self.redis.hset(
                job_key,
                mapping={
                    "status": "failed",
                    "result": "",
                    "error": str(exc)[:1000],
                },
            )
            await self.redis.expire(job_key, JOB_TTL_SECONDS)

        # Acknowledge only after the job's final status was saved.
        await self.redis.xack(
            self.stream_key,
            self.group_name,
            stream_id,
        )