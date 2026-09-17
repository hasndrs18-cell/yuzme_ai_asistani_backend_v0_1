from collections.abc import AsyncIterator

from app.core.config import get_settings
from app.db.database import get_db_session
from app.domain.repository import DomainRepository
from app.domain.postgres_repository import PostgresDomainRepository


_memory_repository = DomainRepository()


def get_memory_repository() -> DomainRepository:
    return _memory_repository


async def get_domain_repository() -> AsyncIterator[DomainRepository | PostgresDomainRepository]:
    settings = get_settings()
    if settings.environment.lower() in {"test", "testing"} or settings.repository_backend.lower() == "memory":
        yield _memory_repository
        return
    async for session in get_db_session():
        yield PostgresDomainRepository(session)
