from collections.abc import AsyncGenerator
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


def _build_engine_url(database_url: str) -> tuple[str, dict]:
    """Strip sslmode from the URL (asyncpg rejects it) and return connect_args for SSL."""
    parsed = urlparse(database_url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    ssl_mode = params.pop("sslmode", ["disable"])[0]
    clean_query = urlencode({k: v[0] for k, v in params.items()})
    clean_url = urlunparse(parsed._replace(query=clean_query))
    connect_args = {"ssl": True} if ssl_mode in ("require", "verify-ca", "verify-full") else {}
    return clean_url, connect_args


_db_url, _connect_args = _build_engine_url(settings.database_url)
engine = create_async_engine(_db_url, echo=False, pool_pre_ping=True, connect_args=_connect_args)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
