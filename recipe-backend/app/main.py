"""FastAPI application factory for the PlatePal recipe wiki."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .admin import bootstrap_admin
from .config import get_settings
from .database import init_db
from .routers import auth, images, ingredients, recipes
from .security import cleanup_expired_tokens


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers.setdefault("Cross-Origin-Resource-Policy", "cross-origin")
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    bootstrap_admin()
    cleanup_expired_tokens()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="PlatePal Recipe Wiki API", version="1.0.0", lifespan=lifespan)

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    app.include_router(auth.router, prefix="/api")
    app.include_router(images.router, prefix="/api")
    app.include_router(ingredients.router, prefix="/api")
    app.include_router(recipes.router, prefix="/api")

    @app.get("/api/health", tags=["health"])
    async def health():
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8091, reload=True)
