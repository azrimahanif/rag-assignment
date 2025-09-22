"""
Database initialization script for PostgreSQL
"""

import asyncio
import sys
from pathlib import Path

# Add the FastAPI app to the path
fastapi_path = str(Path(__file__).parent / "service2" / "fastapi")
sys.path.insert(0, fastapi_path)

# Set PYTHONPATH environment variable for subprocess imports
import os
os.environ["PYTHONPATH"] = fastapi_path + os.pathsep + os.environ.get("PYTHONPATH", "")

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.core.config import settings
from app.core.database import Base, engine

# Import models to register them with Base
from app.models.chat import ChatSession, ChatMessage, ChatAnalytics

# Ensure models are registered with Base
print(f"Registered models: {len(Base.metadata.tables)} tables")
for table_name in Base.metadata.tables:
    print(f"  - {table_name}")

# Verify models are properly registered
if len(Base.metadata.tables) == 0:
    print("⚠️  No models registered! This indicates an import issue.")
    print("   Make sure all model files are properly imported.")
    sys.exit(1)


async def create_database_if_not_exists():
    """Create the database if it doesn't exist"""

    # Parse the database URL to get connection details
    import urllib.parse as urlparse
    url = urlparse.urlparse(settings.DATABASE_URL)

    db_name = url.path[1:]  # Remove leading slash

    # Connect to postgres database to create our database
    postgres_url = settings.DATABASE_URL.replace(f'/{db_name}', '/postgres')

    try:
        # Connect to postgres
        engine = create_async_engine(
            postgres_url.replace("postgresql://", "postgresql+asyncpg://"),
            echo=True
        )

        async with engine.begin() as conn:
            # Check if database exists
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": db_name}
            )

            if not result.scalar():
                print(f"Creating database: {db_name}")
                await conn.execute(
                    text(f'CREATE DATABASE "{db_name}"')
                )
                print(f"Database '{db_name}' created successfully")
            else:
                print(f"Database '{db_name}' already exists")

        await engine.dispose()

    except Exception as e:
        print(f"Error creating database: {e}")
        return False

    return True


async def create_tables():
    """Create all tables in the database"""

    try:
        print("Creating database tables...")

        # Create all tables using the engine from database.py
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        print("Database tables created successfully!")

        # Verify tables were created
        async with engine.begin() as conn:
            result = await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
            tables = [row[0] for row in result.fetchall()]

            print(f"Created tables: {tables}")

            # Check if our expected tables were created
            expected_tables = {'chat_sessions', 'chat_messages', 'chat_analytics'}
            created_tables = set(tables)
            missing_tables = expected_tables - created_tables

            if missing_tables:
                print(f"⚠️  Missing tables: {missing_tables}")
                print("   This indicates the models weren't properly registered.")
                return False
            else:
                print("✅ All expected tables created successfully!")

    except Exception as e:
        print(f"Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


async def test_connection():
    """Test database connection"""

    try:
        engine = create_async_engine(
            settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
            echo=True
        )

        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("Database connection successful!")

        await engine.dispose()
        return True

    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


async def main():
    """Main initialization function"""

    print("=== PostgreSQL Database Initialization ===")
    print(f"Database URL: {settings.DATABASE_URL}")

    # Test connection first
    print("\n1. Testing database connection...")
    if await test_connection():
        print("✅ Connection successful")
    else:
        print("❌ Connection failed")
        return

    # Create database if needed
    print("\n2. Checking/creating database...")
    if await create_database_if_not_exists():
        print("✅ Database ready")
    else:
        print("❌ Database creation failed")
        return

    # Create tables
    print("\n3. Creating tables...")
    if await create_tables():
        print("✅ Tables created successfully")
    else:
        print("❌ Table creation failed")
        return

    print("\n🎉 Database initialization complete!")
    print("You can now start the FastAPI application")


if __name__ == "__main__":
    asyncio.run(main())