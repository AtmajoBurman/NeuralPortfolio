import asyncio
import sys
import os
from datetime import datetime, date, timezone

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from httpx import AsyncClient, ASGITransport
from app.main import app

async def run_tests():
    print("Starting automated integration tests for Portfolio Backend...")
    
    # Explicitly run database migrations and seeding for the test
    from app.database import engine, init_db, async_session_maker
    from app.models.cgpa import CGPATracker
    from app.models.student_details import StudentDetails
    from sqlmodel import select

    print("Initializing test database tables...")
    await init_db()

    # Clear projects table to prevent validation failures from leftover dirty records
    from app.models.project import Project
    async with async_session_maker() as db:
        existing_result = await db.execute(select(Project))
        for p in existing_result.scalars().all():
            await db.delete(p)
        await db.commit()

    # Save original student details and CGPA grade to restore them after the tests
    orig_student_data = None
    orig_cgpa_grade = None
    async with async_session_maker() as db:
        # Save original student details if they exist
        result_student = await db.execute(select(StudentDetails).where(StudentDetails.id == 1))
        student_obj = result_student.scalar_one_or_none()
        if student_obj:
            orig_student_data = {
                "name": student_obj.name,
                "profile_pic": student_obj.profile_pic,
                "bio": student_obj.bio,
                "gmail": student_obj.gmail
            }
        # Save original CGPA if it exists
        result_cgpa = await db.execute(select(CGPATracker).where(CGPATracker.id == 1))
        cgpa_obj = result_cgpa.scalar_one_or_none()
        if cgpa_obj:
            orig_cgpa_grade = cgpa_obj.grade

    try:
        print("Seeding test database static records...")
        async with async_session_maker() as db:
            result_cgpa = await db.execute(select(CGPATracker).where(CGPATracker.id == 1))
            cgpa = result_cgpa.scalar_one_or_none()
            if not cgpa:
                db.add(CGPATracker(id=1, cgpa="CGPA", grade=0.0))
            else:
                cgpa.grade = 0.0
                db.add(cgpa)
                
            result_student = await db.execute(select(StudentDetails).where(StudentDetails.id == 1))
            student = result_student.scalar_one_or_none()
            if not student:
                db.add(StudentDetails(
                    id=1,
                    name="John Doe",
                    profile_pic="https://drive.google.com/file/d/default-profile-pic",
                    bio="An enthusiastic computer science student passionate about software engineering.",
                    gmail="student@gmail.com"
                ))
            else:
                student.name = "John Doe"
                student.profile_pic = "https://drive.google.com/file/d/default-profile-pic"
                student.bio = "An enthusiastic computer science student passionate about software engineering."
                student.gmail = "student@gmail.com"
                db.add(student)
            await db.commit()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Test root endpoint
            response = await client.get("/")
            assert response.status_code == 200
            print("OK: Root endpoint responsive")

            # 2. Test Student Details and CGPA Tracker seeding (lifespan runs automatically)
            # Verify student details seeded
            response = await client.get("/api/student_details")
            assert response.status_code == 200
            student = response.json()
            assert student["id"] == 1
            assert student["name"] == "John Doe"
            print("OK: Student Details seeded successfully")

            # Verify CGPA tracker seeded
            response = await client.get("/api/cgpa")
            assert response.status_code == 200
            cgpa_data = response.json()
            assert cgpa_data["id"] == 1
            assert cgpa_data["cgpa"] == "CGPA"
            print("OK: CGPA Tracker seeded successfully")

            # Get initial updated_at timestamp
            def parse_dt(dt_str: str) -> datetime:
                if dt_str.endswith("Z"):
                    dt_str = dt_str[:-1]
                if "+" in dt_str:
                    dt_str = dt_str.split("+")[0]
                return datetime.fromisoformat(dt_str)

            initial_updated_at = parse_dt(student["updated_at"])

            # 3. Test SGPA Tracker
            # Create SGPA (grade rounded to 2 decimals)
            response = await client.post("/api/sgpa", json={"semester_name": "Semester 1", "grade": 9.456})
            assert response.status_code == 201
            sgpa_data = response.json()
            assert sgpa_data["grade"] == 9.46
            sgpa_id = sgpa_data["id"]
            print("OK: SGPA creation and precision rounding (9.456 -> 9.46) PASSED")

            # Verify that student_details.updated_at got updated
            response = await client.get("/api/student_details")
            student = response.json()
            new_updated_at = parse_dt(student["updated_at"])
            assert new_updated_at > initial_updated_at
            print("OK: Global student_details.updated_at modification sync PASSED")
            
            # Test SGPA grade boundaries
            response = await client.post("/api/sgpa", json={"semester_name": "Semester 2", "grade": 11.0})
            assert response.status_code == 422 # Pydantic validation error
            print("OK: SGPA boundary check (> 10.0 rejected) PASSED")

            response = await client.post("/api/sgpa", json={"semester_name": "Semester 2", "grade": -0.5})
            assert response.status_code == 422 # Pydantic validation error
            print("OK: SGPA boundary check (< 0.0 rejected) PASSED")

            # List SGPA
            response = await client.get("/api/sgpa")
            assert response.status_code == 200
            assert len(response.json()) >= 1
            print("OK: SGPA list retrieval PASSED")

            # Update SGPA
            response = await client.put(f"/api/sgpa/{sgpa_id}", json={"grade": 8.5})
            assert response.status_code == 200
            assert response.json()["grade"] == 8.5
            print("OK: SGPA update PASSED")

            # Delete SGPA
            response = await client.delete(f"/api/sgpa/{sgpa_id}")
            assert response.status_code == 204
            print("OK: SGPA delete PASSED")

            # 4. Test CGPA Tracker Update
            response = await client.put("/api/cgpa", json={"grade": 9.25})
            assert response.status_code == 200
            assert response.json()["grade"] == 9.25
            print("OK: CGPA static update PASSED")

            # 5. Test Profiles Tracker (Google Drive validation)
            # Test invalid logo URL
            response = await client.post("/api/profiles", json={"logo": "https://notdrive.com/file", "link": "https://google.com"})
            assert response.status_code == 422
            print("OK: Profile logo Google Drive check (invalid rejected) PASSED")

            # Test valid logo URL
            response = await client.post("/api/profiles", json={"logo": "https://drive.google.com/file/d/abc", "link": "https://mywebsite.com"})
            assert response.status_code == 201
            profile_id = response.json()["id"]
            print("OK: Profile logo Google Drive check (valid accepted) PASSED")

            # Delete Profile
            response = await client.delete(f"/api/profiles/{profile_id}")
            assert response.status_code == 204
            print("OK: Profile delete PASSED")

            # 6. Test Student Details Update
            response = await client.put("/api/student_details", json={
                "name": "Updated John Doe",
                "profile_pic": "https://docs.google.com/file/d/pic",
                "bio": "New Bio description",
                "gmail": "new_email@gmail.com"
            })
            assert response.status_code == 200
            assert response.json()["name"] == "Updated John Doe"
            print("OK: Student details static update PASSED")

            # 7. Test Projects Tracker (LinkedIn/GitHub/YouTube validation)
            # Test invalid links
            response = await client.post("/api/projects", json={
                "project_name": "Test Project",
                "project_category": "ML",
                "tech_stack": "Python",
                "project_description": "Descr",
                "video_link": "https://notyoutube.com/xyz", # Invalid YouTube link
                "github_repo": "https://github.com/myusername/repo",
                "deployed_link": "https://google.com",
                "linkedin_post": "https://linkedin.com/posts/xyz",
                "start_date": "2026-01-01"
            })
            assert response.status_code == 422
            print("OK: Project link validators (invalid youtube link rejected) PASSED")

            response = await client.post("/api/projects", json={
                "project_name": "Test Project",
                "project_category": "ML",
                "tech_stack": "Python",
                "project_description": "Descr",
                "video_link": "https://youtube.com/watch?v=tgbNymZ7vqY",
                "github_repo": "https://notgithub.com/myrepo", # Invalid github link
                "deployed_link": "https://google.com",
                "linkedin_post": "https://linkedin.com/posts/xyz",
                "start_date": "2026-01-01"
            })
            assert response.status_code == 422
            print("OK: Project link validators (invalid github URL rejected) PASSED")

            # Test valid links
            response = await client.post("/api/projects", json={
                "project_name": "Test Project",
                "project_category": "ML",
                "tech_stack": "Python",
                "project_description": "Descr",
                "video_link": "https://youtu.be/tgbNymZ7vqY?si=9KLY3GO1THBqOHp7",
                "github_repo": "https://github.com/myusername/myrepo",
                "deployed_link": "https://my-demo.com",
                "linkedin_post": "https://www.linkedin.com/posts/xyz",
                "start_date": "2026-01-01"
            })
            assert response.status_code == 201
            proj_id = response.json()["id"]
            print("OK: Project creation with valid links accepted PASSED")

            # Test optional fields omitted
            response = await client.post("/api/projects", json={
                "project_name": "Minimal Project",
                "project_category": "Mobile",
                "tech_stack": "Flutter",
                "project_description": "A minimal project to test optional fields",
                "start_date": "2026-03-01"
            })
            assert response.status_code == 201
            min_proj_id = response.json()["id"]
            assert response.json()["video_link"] is None
            assert response.json()["github_repo"] is None
            assert response.json()["deployed_link"] is None
            assert response.json()["linkedin_post"] is None
            assert response.json()["end_date"] is None
            print("OK: Project creation with omitted optional fields PASSED")

            # Verify descending order sort
            await asyncio.sleep(1)  # ensure different date_added
            response = await client.post("/api/projects", json={
                "project_name": "Test Project 2",
                "project_category": "Web",
                "tech_stack": "FastAPI",
                "project_description": "Descr 2",
                "video_link": "https://www.youtube.com/watch?v=tgbNymZ7vqY",
                "github_repo": "https://github.com/myusername/myrepo2",
                "deployed_link": "https://my-demo2.com",
                "linkedin_post": "https://www.linkedin.com/posts/xyz2",
                "start_date": "2026-02-01"
            })
            assert response.status_code == 201
            proj_id2 = response.json()["id"]

            response = await client.get("/api/projects")
            projects_list = response.json()
            assert len(projects_list) >= 3
            # Project 2 was added after Project 1 and Minimal Project, so it should be at index 0 (descending order)
            indices = [p["id"] for p in projects_list]
            idx1 = indices.index(proj_id)
            idx2 = indices.index(proj_id2)
            idx_min = indices.index(min_proj_id)
            assert idx2 < idx_min < idx1
            print("OK: Projects descending sort order (newest first) PASSED")

            # Cleanup
            await client.delete(f"/api/projects/{proj_id}")
            await client.delete(f"/api/projects/{proj_id2}")
            await client.delete(f"/api/projects/{min_proj_id}")
            print("OK: Project deletion and cleanup PASSED")

            # 8. Test Achievements Tracker
            response = await client.post("/api/achievements", json={
                "name": "Class 10 ICSE",
                "score_or_grade": "92.4/100",
                "description": "Completed ICSE board",
                "view_certificate": "https://drive.google.com/file/d/cert",
                "picture": "https://drive.google.com/file/d/pic",
                "linkedin_post": "https://www.linkedin.com/posts/ach",
                "start_date": "2021-01-01"
            })
            assert response.status_code == 201
            ach_id = response.json()["id"]
            print("OK: Achievement creation PASSED")

            # Test achievements with optional fields omitted
            response = await client.post("/api/achievements", json={
                "name": "Minimal Achievement",
                "description": "Completed minimal achievement",
                "start_date": "2022-01-01"
            })
            assert response.status_code == 201
            min_ach_id = response.json()["id"]
            assert response.json()["score_or_grade"] is None
            assert response.json()["view_certificate"] is None
            assert response.json()["picture"] is None
            assert response.json()["linkedin_post"] is None
            assert response.json()["end_date"] is None
            print("OK: Achievement creation with optional fields omitted PASSED")

            # Cleanup Achievements
            await client.delete(f"/api/achievements/{ach_id}")
            await client.delete(f"/api/achievements/{min_ach_id}")
            print("OK: Achievement deletion and cleanup PASSED")

            # 9. Test Chit-Chat Tracker
            response = await client.post("/api/chitchat", json={
                "description": "My first chit-chat!",
                "link": "https://mywebsite.com"
            })
            assert response.status_code == 201
            cc_id = response.json()["id"]
            print("OK: Chit-chat creation PASSED")

            # Test vanishing posts filtering
            past_time = "2020-01-01T00:00:00Z"
            response = await client.post("/api/chitchat", json={
                "description": "Vanished chit-chat",
                "vanishing_date": past_time
            })
            assert response.status_code == 201
            vanished_id = response.json()["id"]

            # List chit-chats
            response = await client.get("/api/chitchat")
            posts = response.json()
            post_ids = [p["id"] for p in posts]
            assert cc_id in post_ids
            assert vanished_id not in post_ids
            print("OK: Chit-chat vanishing filter (hides expired posts) PASSED")

            # Cleanup
            await client.delete(f"/api/chitchat/{cc_id}")
            await client.delete(f"/api/chitchat/{vanished_id}")
            print("OK: Chit-chat deletion PASSED")

            # 10. Test Chatbot Placeholder
            response = await client.post("/api/chatbot", json={"message": "Hello chatbot"})
            assert response.status_code == 200
            assert response.json()["reply"] == "Chatbot implementation is coming soon!"
            print("OK: Chatbot placeholder endpoint PASSED")

            print("\nALL INTEGRATION TESTS PASSED SUCCESSFULLY!")

    finally:
        # Restore original student details and CGPA to live database state
        async with async_session_maker() as db:
            if orig_student_data:
                res_stud = await db.execute(select(StudentDetails).where(StudentDetails.id == 1))
                student_obj = res_stud.scalar_one_or_none()
                if student_obj:
                    student_obj.name = orig_student_data["name"]
                    student_obj.profile_pic = orig_student_data["profile_pic"]
                    student_obj.bio = orig_student_data["bio"]
                    student_obj.gmail = orig_student_data["gmail"]
                    db.add(student_obj)
            if orig_cgpa_grade is not None:
                res_cgpa = await db.execute(select(CGPATracker).where(CGPATracker.id == 1))
                cgpa_obj = res_cgpa.scalar_one_or_none()
                if cgpa_obj:
                    cgpa_obj.grade = orig_cgpa_grade
                    db.add(cgpa_obj)
            await db.commit()
        print("OK: Cleaned up and restored database state to original values")

    print("\nALL INTEGRATION TESTS PASSED SUCCESSFULLY!")

async def main():
    try:
        await run_tests()
    finally:
        from app.database import engine
        print("Disposing database connection pool...")
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
