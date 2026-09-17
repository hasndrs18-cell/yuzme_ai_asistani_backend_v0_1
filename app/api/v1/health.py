import platform
import time

import psutil
from fastapi import APIRouter, Request, Response

from app.core.rate_limit import RATE_LIMIT, limiter
from app.core.redis import get_redis_client
from app.db.database import get_engine
from sqlalchemy import text

router = APIRouter()


@router.get("/health/db")
@limiter.limit(RATE_LIMIT)
async def database_health(request: Request) -> dict[str, str]:
    try:
        async with get_engine().connect() as connection:
            await connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "postgresql"}
    except Exception:
        return {"status": "unavailable", "database": "postgresql"}


@router.get("/health")
@limiter.limit(RATE_LIMIT)
async def health(request: Request) -> dict[str, object]:
    redis_client = get_redis_client()
    redis_status = "unavailable"
    if redis_client is not None:
        try:
            await redis_client.ping()
            redis_status = "ok"
        except Exception:
            redis_status = "unhealthy"

    memory = psutil.virtual_memory()
    return {
        "status": "ok" if redis_status == "ok" else "degraded",
        "redis": {"status": redis_status},
        "memory": {
            "total_bytes": memory.total,
            "available_bytes": memory.available,
            "used_bytes": memory.used,
            "usage_percent": memory.percent,
        },
        "system": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "uptime_seconds": max(0, int(time.time() - psutil.boot_time())),
        },
    }


@router.get("/metrics")
@limiter.limit(RATE_LIMIT)
async def metrics(request: Request) -> Response:
    memory = psutil.virtual_memory()
    redis_up = 0
    redis_client = get_redis_client()
    if redis_client is not None:
        try:
            await redis_client.ping()
            redis_up = 1
        except Exception:
            pass

    payload = "\n".join(
        (
            "# HELP app_memory_used_bytes Process memory used by the host.",
            "# TYPE app_memory_used_bytes gauge",
            f"app_memory_used_bytes {memory.used}",
            "# HELP app_memory_available_bytes Available host memory.",
            "# TYPE app_memory_available_bytes gauge",
            f"app_memory_available_bytes {memory.available}",
            "# HELP app_memory_usage_percent Host memory usage percentage.",
            "# TYPE app_memory_usage_percent gauge",
            f"app_memory_usage_percent {memory.percent}",
            "# HELP app_redis_up Redis connectivity status.",
            "# TYPE app_redis_up gauge",
            f"app_redis_up {redis_up}",
            "",
        )
    )
    return Response(content=payload, media_type="text/plain; version=0.0.4")
