"""SteadyVox Database Session and Connection Manager.

Provides async SQLAlchemy sessions with automated SQLite fallback if PostgreSQL is offline.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from backend.app.core.config import settings

Base = declarative_base()

# Determine initial database engine URL
db_url = settings.DATABASE_URL
engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

_db_initialized = False


async def init_db():
    """Initializes tables on startup with seamless SQLite fallback."""
    global engine, AsyncSessionLocal, _db_initialized
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Connected to PostgreSQL and verified schema.")
        _db_initialized = True
    except Exception as e:
        print(f"PostgreSQL unreachable ({e}). Initializing SQLite async database fallback.")
        sqlite_url = "sqlite+aiosqlite:///./steadyvox_dev.db"
        engine = create_async_engine(sqlite_url, echo=False, future=True)
        AsyncSessionLocal.configure(bind=engine)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("SQLite fallback database initialized successfully.")
        _db_initialized = True


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for yielding database session with auto-init safety."""
    global _db_initialized
    if not _db_initialized:
        await init_db()

    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
