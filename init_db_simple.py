"""
Simple PostgreSQL database initialization script
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://maisembang_user:maisembang123@localhost:5432/dosmchatbot?schema=public")

# Base class for models
Base = declarative_base()

class ChatSession(Base):
    """Chat session model"""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(String(255), nullable=True)
    title = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Chat message model"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")


class ChatAnalytics(Base):
    """Chat analytics model"""
    __tablename__ = "chat_analytics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("chat_sessions.session_id", ondelete="SET NULL"), nullable=True)
    query_type = Column(String(100), nullable=True)
    response_time = Column(Integer, nullable=True)
    message_count = Column(Integer, default=1)
    sources_used = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


async def create_tables():
    """Create all tables in the database"""

    try:
        # Create engine
        engine = create_async_engine(
            DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
            echo=True
        )

        print("Creating database tables...")

        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        print("Database tables created successfully!")

        # Verify tables were created
        async with engine.begin() as conn:
            result = await conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = [row[0] for row in result.fetchall()]

            print(f"Created tables: {tables}")

        await engine.dispose()

    except Exception as e:
        print(f"Error creating tables: {e}")
        return False

    return True


async def main():
    """Main initialization function"""

    print("=== PostgreSQL Database Initialization ===")
    print(f"Database URL: {DATABASE_URL}")

    # Create tables
    if await create_tables():
        print("\n🎉 Database initialization complete!")
        print("Tables created:")
        print("- chat_sessions")
        print("- chat_messages")
        print("- chat_analytics")
        print("\nYou can now start the FastAPI application")
    else:
        print("\n❌ Database initialization failed")


if __name__ == "__main__":
    asyncio.run(main())