"""API dependency injection."""
from app.db.session import AsyncSessionLocal


async def get_db():
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
