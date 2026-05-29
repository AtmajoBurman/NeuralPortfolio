from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select

from app.database import init_db, async_session_maker
from app.models.cgpa import CGPATracker
from app.models.student_details import StudentDetails
from app.models.admin import AdminUser
from app.models.settings import Settings
from app.authentication.auth_utils import get_password_hash
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import os

from app.routers import sgpa, cgpa, profile, student_details, project, achievement, chitchat, chatbot, auth, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database schemas
    await init_db()
    
    # Seed static tables (id = 1) if they don't already exist
    async with async_session_maker() as db:
        # Seed CGPA Tracker
        result_cgpa = await db.execute(select(CGPATracker).where(CGPATracker.id == 1))
        if not result_cgpa.scalar_one_or_none():
            db.add(CGPATracker(id=1, cgpa="CGPA", grade=0.0))
            
        # Seed Student Details
        result_student = await db.execute(select(StudentDetails).where(StudentDetails.id == 1))
        if not result_student.scalar_one_or_none():
            db.add(StudentDetails(
                id=1,
                name="John Doe",
                profile_pic="https://drive.google.com/file/d/default-profile-pic",
                bio="An enthusiastic computer science student passionate about software engineering.",
                gmail="student@gmail.com"
            ))
            
        # Seed Admin User
        result_admin = await db.execute(select(AdminUser).where(AdminUser.username == "admin"))
        if not result_admin.scalar_one_or_none():
            db.add(AdminUser(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                role="admin"
            ))
            
            
        # Seed Settings
        result_settings = await db.execute(select(Settings).where(Settings.id == 1))
        if not result_settings.scalar_one_or_none():
            db.add(Settings(id=1, smart_mode=True))
            
        await db.commit()
        
    yield

app = FastAPI(
    title="Professional Student Portfolio Backend",
    description="FastAPI, SQLModel, and Neon PostgreSQL Backend",
    version="1.0.0",
    lifespan=lifespan
)

from app.config import settings

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(sgpa.router, prefix="/api")
app.include_router(cgpa.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(student_details.router, prefix="/api")
app.include_router(project.router, prefix="/api")
app.include_router(achievement.router, prefix="/api")
app.include_router(chitchat.router, prefix="/api")
app.include_router(chatbot.router, prefix="/api")

app.include_router(auth.router)
app.include_router(admin.router)

# Mount the frontend folder for static assets (CSS, JS)
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend-admin")), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/login", status_code=303)
