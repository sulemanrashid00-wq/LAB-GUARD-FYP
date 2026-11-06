from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger("labguard.errors")


class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, resource: str, resource_id: any):
        super().__init__(
            message=f"{resource} with identifier '{resource_id}' was not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": str(resource_id)}
        )


class ConflictError(AppException):
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details or {}
        )


class PermissionDeniedError(AppException):
    def __init__(self, message: str = "Permission denied for this operation"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


async def app_exception_handler(request: Request, exc: AppException):
    logger.warning(f"AppException: {exc.message} on {request.method} {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "type": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details,
            }
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "type": "HTTPException",
                "message": exc.detail if isinstance(exc.detail, str) else "An HTTP error occurred",
                "details": exc.detail if isinstance(exc.detail, dict) else {},
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " -> ".join([str(loc) for loc in err.get("loc", [])])
        errors.append({
            "field": field,
            "message": err.get("msg"),
            "type": err.get("type")
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "type": "ValidationError",
                "message": "Input validation failed",
                "details": errors
            }
        }
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled server error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected server error occurred",
                "details": str(exc) if str(exc) else "Internal server error"
            }
        }
    )

