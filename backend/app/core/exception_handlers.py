from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    """Convert predictable application errors to the public error contract."""

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


def _safe_validation_errors(exc: RequestValidationError) -> list[dict[str, Any]]:
    """Make Pydantic validation details safe for JSON serialization."""

    sanitized: list[dict[str, Any]] = []
    for raw_error in exc.errors():
        error = dict(raw_error)
        context = error.get("ctx")
        if isinstance(context, dict):
            error["ctx"] = {
                key: str(value) if isinstance(value, Exception) else value
                for key, value in context.items()
            }
        sanitized.append(error)
    return jsonable_encoder(sanitized)


async def request_validation_error_handler(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Return FastAPI/Pydantic validation failures in the same error envelope."""

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The request contains invalid values.",
                "details": {"errors": _safe_validation_errors(exc)},
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
