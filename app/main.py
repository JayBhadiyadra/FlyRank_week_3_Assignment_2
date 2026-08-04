"""FastAPI application entrypoint."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.routes import api_router

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Normalize HTTPException bodies to `{\"error\": \"...\"}` when possible."""
    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        content = detail
    elif isinstance(detail, str):
        content = {"error": detail}
    else:
        content = {"error": str(detail)}

    return JSONResponse(status_code=exc.status_code, content=content)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Map Pydantic/FastAPI validation failures to a clean 400 JSON error."""
    errors = exc.errors()
    message = "Invalid request"

    if errors:
        first = errors[0]
        loc = first.get("loc", ())
        err_msg = first.get("msg", message)
        field = loc[-1] if loc else None

        # Prefer a clear title-related message for empty/missing titles.
        if field == "title" or "title" in str(err_msg).lower():
            if "required" in err_msg.lower() or first.get("type") == "missing":
                message = "title is required"
            else:
                message = "title cannot be empty"
        else:
            message = err_msg

    return JSONResponse(
        status_code=400,
        content={"error": message},
    )


app.include_router(api_router)
