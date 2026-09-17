from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.websocket import router as websocket_router
from app.api.v1.domain import router as domain_router
from app.api.v1.onboarding import router as onboarding_router
from app.api.v1.academy import router as academy_router
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.core.redis import close_redis_pool, init_redis_pool


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
	await init_redis_pool()
	try:
		yield
	finally:
		await close_redis_pool()


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
allowed_frontend_origins = [settings.frontend_url, *settings.frontend_urls.split(",")]
allowed_frontend_origins = list(dict.fromkeys(origin.strip() for origin in allowed_frontend_origins if origin.strip()))
app.add_middleware(
	CORSMiddleware,
	allow_origins=[
		*allowed_frontend_origins,
		"https://yuzmeaiasistanibackendv01.vercel.app",
		"http://localhost:3000",
		"http://127.0.0.1:3000",
	],
	allow_origin_regex=r"^https://[A-Za-z0-9-]+\.vercel\.app$",
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.exception_handler(SQLAlchemyError)
async def database_unavailable(_: Request, __: SQLAlchemyError) -> JSONResponse:
	return JSONResponse(status_code=503, content={"detail": "Database unavailable"})


@app.exception_handler(ConnectionRefusedError)
async def database_connection_refused(_: Request, __: ConnectionRefusedError) -> JSONResponse:
	return JSONResponse(status_code=503, content={"detail": "Database unavailable"})


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(domain_router, prefix="/api/v1")
app.include_router(onboarding_router, prefix="/api/v1")
app.include_router(academy_router, prefix="/api/v1")
app.include_router(websocket_router)
