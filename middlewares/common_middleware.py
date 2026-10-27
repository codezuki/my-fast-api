import logging
import time
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger("NexusAPI")


class CommonMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        request.state.correlation_id = correlation_id

        client_ip = request.client.host if request.client else None
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        method = request.method
        path = request.url.path
        start = time.perf_counter()

        logger.info(
            "Request started | %s %s | IP=%s | CorrelationId=%s",
            method,
            path,
            client_ip,
            correlation_id,
        )

        try:
            response = await call_next(request)
        except Exception as ex:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            logger.exception(
                "Unhandled exception | %s %s | %s ms | CorrelationId=%s | Error=%s",
                method,
                path,
                elapsed_ms,
                correlation_id,
                str(ex),
            )
            return JSONResponse(
                status_code=500,
                content={
                    "StatusCode": 500,
                    "ErrorType": "Internal Server Error",
                    "ErrorMessage": "An unexpected error occurred.",
                    "ReferenceId": correlation_id,
                },
                headers={"X-Correlation-ID": correlation_id},
            )

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        response.headers["X-Correlation-ID"] = correlation_id
        logger.info(
            "Request completed | %s %s | %s ms | Status=%s | CorrelationId=%s",
            method,
            path,
            elapsed_ms,
            response.status_code,
            correlation_id,
        )
        return response
