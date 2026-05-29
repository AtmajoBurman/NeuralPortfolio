import sys
import os
import asyncio
from datetime import date

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import select
from app.database import engine, async_session_maker, init_db
from app.models.achievement import Achievement

async def seed():
    print("Initializing database schemas...")
    await init_db()

    print("Opening database session...")
    async with async_session_maker() as db:
        # Clear existing achievements
        print("Clearing existing achievements...")
        existing_result = await db.execute(select(Achievement))
        existing_achievements = existing_result.scalars().all()
        for ach in existing_achievements:
            await db.delete(ach)
        await db.commit()
        print("Cleared achievements successfully.")

        # Prepare mock achievements
        achievements_to_seed = [
            # 1. Class 10 ICSE
            Achievement(
                name="Class 10 ICSE Examination 2021",
                score_or_grade="92.4/100",
                description="Successfully completed the ICSE Class 10 board examinations with strong academic performance across all subjects. Demonstrated consistency, discipline, and conceptual clarity, particularly in mathematics and science, forming a solid foundation for higher studies in technical domains.",
                view_certificate="https://drive.google.com/file/d/icse-certificate-id",
                picture="https://drive.google.com/file/d/icse-snapshot-id",
                linkedin_post="https://www.linkedin.com/posts/icse-ev",
                start_date=date(2021, 1, 1),
                end_date=date(2021, 6, 1)
            ),
            # 2. Class 12 ISC
            Achievement(
                name="Class 12 ISC Examination 2023",
                score_or_grade="88.6/100",
                description="Completed ISC Class 12 examinations with a focus on science stream subjects including Physics, Chemistry, and Mathematics. Developed analytical thinking and problem-solving skills, which contributed to further pursuit of engineering and computer science disciplines.",
                view_certificate="https://drive.google.com/file/d/isc-certificate-id",
                picture="https://drive.google.com/file/d/isc-snapshot-id",
                linkedin_post="https://www.linkedin.com/posts/isc-ev",
                start_date=date(2023, 1, 1),
                end_date=date(2023, 6, 1)
            ),
            # 3. Code for Good Hackathon 2025
            Achievement(
                name="Code for Good Hackathon 2025",
                score_or_grade="Finalist",
                description="Participated in the Code for Good Hackathon 2025, collaborating in a team environment to design and develop a technology-driven solution addressing real-world social challenges. Gained hands-on experience in rapid prototyping, problem analysis, and effective teamwork under time constraints, while interacting with industry professionals.",
                view_certificate="https://drive.google.com/file/d/codeforgood-cert-id",
                picture="https://drive.google.com/file/d/codeforgood-team-pic-id",
                linkedin_post="https://www.linkedin.com/posts/codeforgood-ev",
                start_date=date(2025, 7, 1),
                end_date=date(2025, 7, 3)
            ),
            # 4. Minimal Achievement (no optional fields provided)
            Achievement(
                name="Dean's List Academic Honor",
                score_or_grade=None,
                description="Placed on the Dean's List for outstanding academic performance during the first semester of the B.Tech program, achieving a GPA in the top percentile of the computer science department.",
                view_certificate=None,
                picture=None,
                linkedin_post=None,
                start_date=date(2025, 12, 15),
                end_date=None
            )
        ]

        print("Adding achievements to database session...")
        for ach in achievements_to_seed:
            db.add(ach)
        
        await db.commit()
        print("Successfully seeded all 4 achievements!")

async def main():
    try:
        await seed()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
