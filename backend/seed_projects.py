import sys
import os
import asyncio
from datetime import date

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import select
from app.database import engine, async_session_maker, init_db
from app.models.project import Project

async def seed():
    print("Initializing database schemas...")
    await init_db()

    print("Opening database session...")
    async with async_session_maker() as db:
        # Clear existing projects
        print("Clearing existing projects...")
        existing_result = await db.execute(select(Project))
        existing_projects = existing_result.scalars().all()
        for proj in existing_projects:
            await db.delete(proj)
        await db.commit()
        print("Cleared projects successfully.")

        # Prepare mock projects
        projects_to_seed = [
            # 1. Full Project (all fields entered, uses Youtube video link)
            Project(
                project_name="Real-Time Hand Gesture Recognition",
                project_category="Machine Learning Project",
                tech_stack="Python, OpenCV, MediaPipe, NumPy",
                project_description="A real-time hand gesture recognition system that uses computer vision to detect and classify hand gestures via webcam. The system leverages MediaPipe for hand tracking and OpenCV for image processing, enabling applications like touchless control, virtual interfaces, and assistive technologies.",
                video_link="https://youtu.be/tgbNymZ7vqY?si=9KLY3GO1THBqOHp7",
                github_repo="https://github.com/username/gesture-recognition",
                deployed_link="https://gesture-app-demo.streamlit.app",
                linkedin_post="https://www.linkedin.com/posts/gesture-recognition-ev",
                start_date=date(2026, 1, 1),
                end_date=date(2026, 2, 15)
            ),
            # 2. Ongoing Project (no video, no end date -> show ongoing "Present" tag and video placeholder)
            Project(
                project_name="Stock Price Prediction Dashboard",
                project_category="Data Science Project",
                tech_stack="Python, Pandas, Scikit-learn, Streamlit, Matplotlib",
                project_description="An interactive dashboard that predicts stock prices using historical data and machine learning models. Users can visualize trends, forecast future prices, and analyze performance metrics through a clean Streamlit interface.",
                video_link=None,
                github_repo="https://github.com/username/stock-prediction",
                deployed_link="https://stock-dashboard.streamlit.app",
                linkedin_post="https://www.linkedin.com/posts/stock-prediction-dashboard",
                start_date=date(2026, 2, 20),
                end_date=None
            ),
            # 3. Private Code & Deployment (has video, but no GitHub / Deployed Link -> shows code/deployment placeholders)
            Project(
                project_name="Smart Home Automation System",
                project_category="Embedded Systems Project",
                tech_stack="Arduino, C++, ESP8266, Blynk, IoT",
                project_description="A smart home system that allows users to control appliances remotely using a mobile app. It integrates IoT modules with Arduino and ESP8266, enabling automation, scheduling, and real-time monitoring of home devices.",
                video_link="https://www.youtube.com/watch?v=tgbNymZ7vqY",
                github_repo=None,
                deployed_link=None,
                linkedin_post="https://www.linkedin.com/posts/smart-home-automation",
                start_date=date(2026, 3, 1),
                end_date=date(2026, 4, 10)
            ),
            # 4. Analytics Report (no video, no LinkedIn post -> shows video/LinkedIn placeholders)
            Project(
                project_name="Customer Segmentation using Clustering",
                project_category="Data Analytics Project",
                tech_stack="Python, K-Means, Seaborn, Pandas, PowerBI",
                project_description="A customer segmentation project that applies clustering techniques to group customers based on purchasing behavior. The insights are visualized using PowerBI dashboards to support business decision-making and targeted marketing strategies.",
                video_link=None,
                github_repo="https://github.com/username/customer-segmentation",
                deployed_link="https://powerbi.com/report/customer-segmentation",
                linkedin_post=None,
                start_date=date(2026, 4, 15),
                end_date=date(2026, 5, 1)
            ),
            # 5. Minimal Project (all optional fields omitted -> shows all placeholders)
            Project(
                project_name="Autonomous Maze Solver Robot",
                project_category="Robotics Project",
                tech_stack="C++, Arduino, Ultrasonic Sensors, Motors",
                project_description="An autonomous robot designed to solve arbitrary 2D grid mazes using micro-mouse algorithms. Built using custom Arduino controllers, dual DC motor gearboxes, and distance sensors to calculate shortest paths in real-time.",
                video_link=None,
                github_repo=None,
                deployed_link=None,
                linkedin_post=None,
                start_date=date(2026, 5, 5),
                end_date=None
            )
        ]

        print("Adding projects to database session...")
        for proj in projects_to_seed:
            db.add(proj)
        
        await db.commit()
        print("Successfully seeded all 5 test projects!")

async def main():
    try:
        await seed()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
