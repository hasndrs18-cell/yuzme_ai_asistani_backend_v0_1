"""
Phase 6: Redis Distributed Lock (Redlock Architecture)
Prevents concurrent execution race-conditions across multi-pod deployments.
"""
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from app.core.config import get_settings
from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)


class DistributedLockError(Exception):
    """Kilit alinamadiginda veya zaman asimina ugradiginda firlatilir."""
    pass


class DistributedLockManager:
    """
    Async Redis tabanli dagitik kilit mekanizmasi.
    Redis bulunmadiginda dev/test ortami icin in-memory fallback sunar.
    """

    def __init__(self):
        self._in_memory_locks = {}

    @asynccontextmanager
    async def acquire_lock(
        self,
        resource_id: str,
        ttl_seconds: int = 10,
        timeout_seconds: float = 2.0
    ) -> AsyncGenerator[bool, None]:
        """
        Belirtilen kaynak (orn: session_id/thread_id) icin kilit edinir.
        """
        settings = get_settings()
        lock_acquired = False
        redis_client = None

        if settings.checkpoint_provider == "redis":
            try:
                redis_client = get_redis_client()
                if redis_client is None:
                    raise RuntimeError("Redis pool is not initialized")

                lock_key = f"lock:{resource_id}"
                start_time = asyncio.get_event_loop().time()
                while (asyncio.get_event_loop().time() - start_time) < timeout_seconds:
                    acquired = await redis_client.set(lock_key, "locked", ex=ttl_seconds, nx=True)
                    if acquired:
                        lock_acquired = True
                        break
                    await asyncio.sleep(0.05)

            except Exception as e:
                logger.warning("Redis Lock baglantisi kurulamadi (%s), fallback kullaniliyor.", e)

        # Fallback: InMemory Asyncio Lock (Dev / Test)
        if not lock_acquired:
            if resource_id not in self._in_memory_locks:
                self._in_memory_locks[resource_id] = asyncio.Lock()
            
            mem_lock = self._in_memory_locks[resource_id]
            try:
                await asyncio.wait_for(mem_lock.acquire(), timeout=timeout_seconds)
                lock_acquired = True
            except asyncio.TimeoutError:
                raise DistributedLockError(f"Resource lock timed out for key: {resource_id}")

        try:
            yield lock_acquired
        finally:
            if redis_client and settings.checkpoint_provider == "redis":
                try:
                    await redis_client.delete(f"lock:{resource_id}")
                    await redis_client.aclose()
                except Exception:
                    pass
            elif resource_id in self._in_memory_locks and self._in_memory_locks[resource_id].locked():
                self._in_memory_locks[resource_id].release()


lock_manager = DistributedLockManager()