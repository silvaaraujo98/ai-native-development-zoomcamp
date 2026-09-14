from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import hash_password
from app.routers import auth, board, tasks
from app.store import store


def create_app() -> FastAPI:
    app = FastAPI(title="FocusBoard API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(board.router)
    app.include_router(tasks.router)
    return app


store.reset(password_hash=hash_password("demo"))
app = create_app()
