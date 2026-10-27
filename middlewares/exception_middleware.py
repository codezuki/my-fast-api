import time
import re
import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

import pyodbc


logger = logging.getLogger("NexusAPI")


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        # ---------------------------------------------------------
        # Correlation ID
        # ---------------------------------------------------------
        correlation_id = request.headers.get(
            "X-Correlation-ID",
            str(request.scope.get("trace_id", ""))
        )

        if not correlation_id:
            import uuid
            correlation_id = str(uuid.uuid4())

        # ---------------------------------------------------------
        # Client IP
        # ---------------------------------------------------------
        client_ip = request.client.host if request.client else None

        forwarded_for = request.headers.get("X-Forwarded-For")

        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        # ---------------------------------------------------------
        # Request information
        # ---------------------------------------------------------
        request_path = request.url.path
        method = request.method

        stopwatch = time.perf_counter()

        try:

            # -----------------------------------------------------
            # Execute Controller
            # -----------------------------------------------------
            response = await call_next(request)

            return response

        except pyodbc.Error as sql_ex:

            elapsed_ms = int(
                (time.perf_counter() - stopwatch) * 1000
            )

            request_details = self.get_request_details(
                request,
                client_ip
            )

            logger.error(
                "SQL Exception | ElapsedMs: %s | Request: %s | Error: %s",
                elapsed_ms,
                request_details,
                str(sql_ex)
            )

            return self.sql_exception_response(
                request,
                sql_ex,
                correlation_id
            )

        except Exception as ex:

            elapsed_ms = int(
                (time.perf_counter() - stopwatch) * 1000
            )

            request_details = self.get_request_details(
                request,
                client_ip
            )

            logger.exception(
                "Unhandled Exception | ElapsedMs: %s | "
                "Request: %s | Error: %s",
                elapsed_ms,
                request_details,
                str(ex)
            )

            return self.exception_response(
                request,
                ex,
                correlation_id
            )

        finally:

            # -----------------------------------------------------
            # Response time
            # -----------------------------------------------------
            elapsed_ms = int(
                (time.perf_counter() - stopwatch) * 1000
            )

            logger.info(
                "%s %s | %s ms | CorrelationId=%s | IP=%s",
                method,
                request_path,
                elapsed_ms,
                correlation_id,
                client_ip
            )

    # =============================================================
    # SQL EXCEPTION
    # =============================================================

    def sql_exception_response(
        self,
        request: Request,
        exception: pyodbc.Error,
        correlation_id: str
    ):

        error_message = str(exception)

        # ---------------------------------------------------------
        # UNIQUE KEY constraint
        # ---------------------------------------------------------
        if "UNIQUE KEY constraint" in error_message:

            match = re.search(
                r"UNIQUE KEY constraint.*\(([^)]+)\)",
                error_message
            )

            constraint_match = re.search(
                r"UNIQUE KEY constraint '([^']+)'",
                error_message
            )

            fallback_value = (
                match.group(1)
                if match
                else "Value"
            )

            constraint_value = (
                constraint_match.group(1)
                if constraint_match
                else "Value"
            )

            error_message = self.get_error_message(
                constraint_value,
                fallback_value
            )

        return JSONResponse(
            status_code=400,
            content={
                "StatusCode": 400,
                "ErrorType": "SqlException",
                "ErrorMessage": error_message,
                "ReferenceId": correlation_id
            },
            headers={
                "X-Correlation-ID": correlation_id
            }
        )

    # =============================================================
    # SQL ERROR MESSAGE
    # =============================================================

    @staticmethod
    def get_error_message(
        constraint_value: str,
        fallback_value: str
    ):

        error_messages = {

            "UQ_Booking_MarkedDate":
                "The specified LRNo is already marked as damaged.",

            "UQ_Dev_Booking_SK":
                "The specified LRNo is already Delivered",

            "UQ_Dev_LRNo":
                "The specified LRNo is already Delivered"
        }

        return error_messages.get(
            constraint_value,
            f"{fallback_value} already exists"
        )

    # =============================================================
    # GENERAL EXCEPTION
    # =============================================================

    @staticmethod
    def exception_response(
        request: Request,
        exception: Exception,
        correlation_id: str
    ):

        return JSONResponse(
            status_code=500,
            content={
                "StatusCode": 500,
                "ErrorType": "Internal Server Error",
                "ErrorMessage": "An unexpected error occurred.",
                "ReferenceId": correlation_id
            },
            headers={
                "X-Correlation-ID": correlation_id
            }
        )

    # =============================================================
    # REQUEST DETAILS
    # =============================================================

    @staticmethod
    def get_request_details(
        request: Request,
        client_ip: str
    ):

        return {
            "Method": request.method,
            "Path": request.url.path,
            "Query": str(request.query_params),
            "IP": client_ip
        }