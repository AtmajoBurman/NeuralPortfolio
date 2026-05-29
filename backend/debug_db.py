import asyncio
from app.database import async_session_maker
from sqlmodel import select
from app.models.achievement import Achievement, AchievementRead

async def main():
    async with async_session_maker() as s:
        res = await s.execute(select(Achievement).order_by(Achievement.date_added.desc()))
        achievements = res.scalars().all()
        print(f"Total achievements: {len(achievements)}")
        for i, ach in enumerate(achievements):
            try:
                AchievementRead.model_validate(ach)
                print(f"[{i}] Success: {ach.name}")
            except Exception as e:
                print(f"[{i}] FAILED: {ach.name} -> {e}")

asyncio.run(main())
