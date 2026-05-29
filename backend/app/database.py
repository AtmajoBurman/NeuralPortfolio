from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from app.config import settings

# If the URL from .env doesn't specify +asyncpg, we add it to make it compatible with async execution
database_url = settings.postgres_url
if "postgresql://" in database_url and "+asyncpg" not in database_url:
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

# Create the async engine with prepared statement caching disabled (required for PgBouncer/Neon pooler)
engine = create_async_engine(
    database_url, 
    echo=False, 
    future=True, 
    connect_args={"statement_cache_size": 0}
)

# Sessionmaker for async sessions
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    """Create all database tables."""
    import app.models  # Populate SQLModel metadata
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        # Drop NOT NULL constraints for optional fields in projects table
        try:
            await conn.execute(text("ALTER TABLE projects ALTER COLUMN video_link DROP NOT NULL;"))
            await conn.execute(text("ALTER TABLE projects ALTER COLUMN github_repo DROP NOT NULL;"))
            await conn.execute(text("ALTER TABLE projects ALTER COLUMN deployed_link DROP NOT NULL;"))
            await conn.execute(text("ALTER TABLE projects ALTER COLUMN linkedin_post DROP NOT NULL;"))
            
            # Drop NOT NULL constraints for optional fields in achievements table
            await conn.execute(text("ALTER TABLE achievements ALTER COLUMN score_or_grade DROP NOT NULL;"))
            await conn.execute(text("ALTER TABLE achievements ALTER COLUMN view_certificate DROP NOT NULL;"))
            await conn.execute(text("ALTER TABLE achievements ALTER COLUMN picture DROP NOT NULL;"))
            await conn.execute(text("ALTER TABLE achievements ALTER COLUMN linkedin_post DROP NOT NULL;"))
            
            # Add order_index columns
            await conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS order_index INTEGER NOT NULL DEFAULT 0;"))
            await conn.execute(text("ALTER TABLE achievements ADD COLUMN IF NOT EXISTS order_index INTEGER NOT NULL DEFAULT 0;"))
            
            # Migrate bio column to TEXT type for unlimited length
            await conn.execute(text("ALTER TABLE student_details ALTER COLUMN bio TYPE TEXT USING bio::text;"))
            
            # Automatically restore/seed Elena Vance's details if overwritten by tests
            result_student = await conn.execute(text("SELECT name FROM student_details WHERE id = 1;"))
            row = result_student.first()
            if not row or row[0] in ("John Doe", "Updated John Doe"):
                await conn.execute(text("""
                    INSERT INTO student_details (id, name, profile_pic, bio, gmail, updated_at)
                    VALUES (1, 'Elena Vance', 'https://drive.google.com/file/d/default-profile-pic', 
                    'An enthusiastic computer science student and software developer passionate about building web applications, machine learning, and design.', 
                    'elena.vance@gmail.com', NOW())
                    ON CONFLICT (id) DO UPDATE SET 
                    name = EXCLUDED.name,
                    profile_pic = EXCLUDED.profile_pic,
                    bio = EXCLUDED.bio,
                    gmail = EXCLUDED.gmail,
                    updated_at = NOW();
                """))
        except Exception as e:
            print(f"Migration warning: altering database fields failed: {e}")

async def get_session() -> AsyncSession:
    """Dependency to provide an async DB session to routes."""
    async with async_session_maker() as session:
        yield session
