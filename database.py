from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings
from sqlalchemy.pool import AsyncAdaptedQueuePool


engine = create_async_engine(
    settings().DATABASE_URL,
    poolclass=AsyncAdaptedQueuePool, #default when using async engine
    pool_size=10,                    #Total connections maintained in the pool
    max_overflow=10,                 #When all connection in pool is occupied 10 new connections will open
    pool_timeout=30,                 #Seconds to wait for a connection before raising TimeoutError
    pool_recycle=1800,               #Recycle connections after 1800 s or 30  min to prevent stale connection issue
    pool_pre_ping=True,              #Before proceeding with the connection first check the connection is working or not
    echo=False,                      #Didn't print the sql commands written by sqlalchemy in console
    future=True,
    connect_args={"ssl": "require"}                     
)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db