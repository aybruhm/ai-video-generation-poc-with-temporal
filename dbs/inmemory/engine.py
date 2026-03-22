import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from utils.env_utils import env

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Get database URL from environment
DATABASE_URL = env.DATABASE_URL

# Create SQLAlchemy engine with improved connection handling
engine = create_async_engine(
    url=DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_reset_on_return="commit",
)

# Create an session factory with better isolation
AsyncSession = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,  # Prevent lazy loading issues
    autoflush=True,
    autocommit=False,
)


@asynccontextmanager
async def get_db_session():
    """
    Get a database session with improved error handling and connection management.
    """

    session = None
    try:
        session = AsyncSession()
        yield session

        # Explicitly commit if there are pending changes
        if session.dirty or session.new or session.deleted:
            await session.commit()

    except Exception as e:
        if session:
            try:
                await session.rollback()
                logger.warning(
                    f"Rolled back session {id(session)} due to error: {str(e)}"
                )
            except Exception as rollback_error:
                logger.error(f"Error during rollback: {rollback_error}")
        raise
    finally:
        if session:
            await session.close()


async def cleanup_connections():
    """Cleanup all connections in the pool."""
    try:
        await engine.dispose()
        logger.info("Database engine disposed successfully")
    except Exception as e:
        logger.error(f"Error disposing engine: {e}")
