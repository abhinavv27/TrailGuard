import time
from collections import defaultdict
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.DEMO_MODE:
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="TrailGuard AI",
    description="Financial Crime Investigation Platform",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEMO_MODE else None,
    redoc_url="/redoc" if settings.DEMO_MODE else None,
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Cache-Control"] = "no-store"
    if settings.DEMO_MODE:
        response.headers["X-Demo-Mode"] = "true"
    return response


request_counts: dict = defaultdict(list)

@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    if request.url.path in ("/api/v1/auth/login", "/api/v1/datasets/upload"):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        request_counts[client_ip] = [t for t in request_counts[client_ip] if now - t < 60]
        max_requests = 10 if "/login" in request.url.path else 30
        if len(request_counts[client_ip]) >= max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests", "code": "RATE_LIMITED"},
            )
        request_counts[client_ip].append(now)
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "code": "INTERNAL_ERROR"},
    )
