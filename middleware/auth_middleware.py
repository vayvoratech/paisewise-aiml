"""Internal authentication for calls coming from trusted Spring Boot services."""

import logging
import os

from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

load_dotenv()
logger = logging.getLogger("ai-service.auth")


class InternalAuthMiddleware(BaseHTTPMiddleware):
    

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/ai/"):
            return await call_next(request)

        if request.url.path == "/ai/health":
            return await call_next(request)

        expected = os.getenv("SHARED_SECRET")
        allow_local = os.getenv("AI_AUTH_ALLOW_LOCAL", "false").lower() == "true"

        if allow_local:
            logger.warning("Local authentication bypass is enabled")
            return await call_next(request)

        if not expected:
            environment = os.getenv(
                "SENTRY_ENVIRONMENT",
                os.getenv("ENVIRONMENT", "development")
            ).lower()

            if environment in {"development", "dev", "local", "test"}:
                logger.warning(
                    "SHARED_SECRET is not configured; local auth bypass is enabled"
                )
                return await call_next(request)

            return JSONResponse(
                status_code=503,
                content={"detail": "AI service authentication is not configured"},
            )

        supplied = request.headers.get("X-API-KEY")

        if not supplied:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing authentication header"},
            )

        if supplied != expected:
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid authentication credentials"},
            )

        return await call_next(request)


async def authenticate_request(request: Request):

    expected = os.getenv("SHARED_SECRET")
    supplied = request.headers.get("X-API-KEY")

    if expected and supplied != expected:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=403,
            detail="Invalid authentication credentials",
        )

    return True
