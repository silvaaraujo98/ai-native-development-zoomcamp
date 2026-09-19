from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routers import auth, canvas, export, metadata, participants, sessions


def create_app() -> FastAPI:
    app = FastAPI(title="System Design Interview Platform API", version="1.0.0")

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"message": "System Design Interview Platform API"}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail
        if not isinstance(detail, dict) or "code" not in detail or "message" not in detail:
            detail = {"code": "http_error", "message": str(exc.detail)}
        return JSONResponse(status_code=exc.status_code, content=detail, headers=getattr(exc, "headers", None))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"code": "validation_error", "message": "Request validation failed.", "details": exc.errors()},
        )

    app.include_router(auth.router, prefix="/v1")
    app.include_router(metadata.router, prefix="/v1")
    app.include_router(sessions.router, prefix="/v1")
    app.include_router(participants.router, prefix="/v1")
    app.include_router(canvas.router, prefix="/v1")
    app.include_router(export.router, prefix="/v1")
    return app


app = create_app()
