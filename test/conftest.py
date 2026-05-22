import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from database import get_db, Base
from main import app
from httpx import AsyncClient, ASGITransport

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:Madhur%402004@localhost:5432/test_blog_db"

# ─────────────────────────────────────────────
# Step 1: Create tables once for the whole session
# This is SYNCHRONOUS and OUTSIDE any async fixture
# so it has no event loop problems
# ─────────────────────────────────────────────

def pytest_configure(config):
    """
    This runs once when pytest starts.
    It's synchronous — no event loop involved.
    We use the sync version of SQLAlchemy to create tables.
    """
    from sqlalchemy import create_engine
    # Note: regular postgresql URL, not asyncpg
    sync_url = TEST_DATABASE_URL.replace(
        "postgresql+asyncpg", "postgresql+psycopg2"
    )
    sync_engine = create_engine(sync_url)
    Base.metadata.create_all(sync_engine)
    sync_engine.dispose()


def pytest_unconfigure(config):
    """
    This runs once when pytest finishes.
    Drop all tables.
    """
    from sqlalchemy import create_engine
    sync_url = TEST_DATABASE_URL.replace(
        "postgresql+asyncpg", "postgresql+psycopg2"
    )
    sync_engine = create_engine(sync_url)
    Base.metadata.drop_all(sync_engine)
    sync_engine.dispose()


# ─────────────────────────────────────────────
# Step 2: Per-test async fixtures
# Everything here is function-scoped (default)
# Each test gets its own event loop and its own
# fresh connections — no cross-loop contamination
# ─────────────────────────────────────────────

@pytest_asyncio.fixture
async def db() -> AsyncSession:
    """
    Creates a fresh async database session for each test.
    
    NullPool means no connection reuse.
    Each call to this fixture gets a brand new connection
    from scratch — completely independent of other tests.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )

    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    """
    Runs automatically before every test.
    autouse=True means you don't need to add it to test parameters.
    
    Cleans all data so each test starts fresh.
    """
    # yield first — let the test run
    yield

    # After test — wipe all data
    # We create a separate engine just for cleanup
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )

    async with engine.begin() as conn:
        await conn.execute(text(
            """
            TRUNCATE TABLE 
                notifications,
                bookmarks,
                follows,
                comment_reactions,
                reactions,
                post_tags,
                comments,
                posts,
                tags,
                users
            RESTART IDENTITY CASCADE
            """
        ))

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncClient:
    """
    Provides an HTTP test client that uses the test database.
    Overrides get_db so all routes use our test session.
    """
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ─────────────────────────────────────────────
# Helper fixtures — reusable across test files
# ─────────────────────────────────────────────

@pytest_asyncio.fixture
async def authenticated_client(client: AsyncClient) -> AsyncClient:
    """
    Returns a client that's already logged in.
    Most of your tests will use this instead of client directly.
    """
    # Register
    await client.post("/auth/register", data={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword123",
        "bio": "test bio"
    })

    # Login
    login = await client.post("/auth/login", data={
        "username": "testuser",
        "password": "testpassword123"
    })

    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    return client