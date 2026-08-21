import os
from fastapi import Request, HTTPException
from dotenv import load_dotenv


load_dotenv()

SHARED_SECRET = os.getenv("SHARED_SECRET")


async def authenticate_request(request: Request):
    """
    Validate requests coming from Spring Boot service
    using shared secret header.
    """

    request_secret = request.headers.get("X-API-KEY")

    if not request_secret:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication header"
        )

    if request_secret != SHARED_SECRET:
        raise HTTPException(
            status_code=403,
            detail="Invalid authentication credentials"
        )

    return True