# Walkthrough - Professional Portfolio Backend Implementation

We have successfully developed a robust, production-grade FastAPI backend using SQLModel and asyncpg to connect to a Neon PostgreSQL database.

## Changes Made

### 1. Project Directory Structure
All backend source files are organized inside the `backend/` directory:
```
backend/
├── requirements.txt      # Project dependencies
├── run.py                # Server entry point script
├── test_app.py           # Idempotent integration test suite
└── app/
    ├── config.py         # Reads .env variables using Pydantic Settings
    ├── database.py       # Manages async engine, sessions, and table initialization
    ├── main.py           # FastAPI application startup, CORS, lifespan, and routers registration
    ├── models/           # SQLModel database representation and validation schemas
    │   ├── achievements.py
    │   ├── cgpa.py
    │   ├── chitchat.py
    │   ├── profile.py
    │   ├── project.py
    │   ├── sgpa.py
    │   └── student_details.py
    ├── routers/          # FastAPI routes handling request/response logic
    │   ├── achievements.py
    │   ├── chatbot.py
    │   ├── cgpa.py
    │   ├── chitchat.py
    │   ├── profile.py
    │   ├── project.py
    │   ├── sgpa.py
    │   └── student_details.py
    └── utils/
        ├── db_helpers.py # Synchronizes student_details.updated_at
        └── validators.py # Reusable link validators
```

### 2. Implemented Database Schema & Validation Constraints
- **Dynamic Tables** (Full CRUD supported):
  - `sgpa_tracker`: Validates float grades (0.00 to 10.00 inclusive) and rounds precision to exactly 2 decimal places.
  - `profiles`: Checks that `logo` is a valid Google Drive link and `link` is a valid URL string.
  - `projects`: Ensures `video_link` is a Google Drive link, `github_repo` is a GitHub link, `linkedin_post` is a LinkedIn link, and sorting returns the newest project first (`date_added DESC`).
  - `achievements`: Validates that `picture` and `view_certificate` are Google Drive links, `linkedin_post` is a LinkedIn link, and sorts by newest first.
  - `chit_chat`: Auto-generates naive UTC creation/update timestamps. Has a max description length constraint of 280 characters. List retrieval filters out posts whose `vanishing_date` is in the past.
- **Static Tables** (Update-only, initialized automatically with row `id = 1` if empty):
  - `cgpa_tracker`: Default CGPA key label. Validates float grade (0.00 to 10.00) with 2 decimal places precision.
  - `student_details`: Standard details schema with max name length of 100 characters, max bio of 1000 characters, Pydantic email validation on `gmail`, and a system-managed timezone-naive UTC `updated_at` timestamp.

### 3. Global update sync for `student_details.updated_at`
A centralized helper `touch_student_details(db: AsyncSession)` was implemented. It is automatically called by mutating operations (create, update, delete) in all other routers, updating the `updated_at` field of the static student details record to the current timezone-naive UTC timestamp.

---

## Verification & Test Results

We wrote and executed a comprehensive automated integration test suite in [test_app.py](file:///c:/Users/MyPC/OneDrive/Documents/professional/backend/test_app.py).

### Integration Test Output Log
```
Starting automated integration tests for Portfolio Backend...
Initializing test database tables...
Seeding test database static records...
OK: Root endpoint responsive
OK: Student Details seeded successfully
OK: CGPA Tracker seeded successfully
OK: SGPA creation and precision rounding (9.456 -> 9.46) PASSED
OK: Global student_details.updated_at modification sync PASSED
OK: SGPA boundary check (> 10.0 rejected) PASSED
OK: SGPA boundary check (< 0.0 rejected) PASSED
OK: SGPA list retrieval PASSED
OK: SGPA update PASSED
OK: SGPA delete PASSED
OK: CGPA static update PASSED
OK: Profile logo Google Drive check (invalid rejected) PASSED
OK: Profile logo Google Drive check (valid accepted) PASSED
OK: Profile delete PASSED
OK: Student details static update PASSED
OK: Project link validators (invalid drive link rejected) PASSED
OK: Project link validators (invalid github URL rejected) PASSED
OK: Project creation with valid links accepted PASSED
OK: Projects descending sort order (newest first) PASSED
OK: Project deletion and cleanup PASSED
OK: Achievement creation PASSED
OK: Achievement deletion PASSED
OK: Chit-chat creation PASSED
OK: Chit-chat vanishing filter (hides expired posts) PASSED
OK: Chit-chat deletion PASSED
OK: Chatbot placeholder endpoint PASSED

ALL INTEGRATION TESTS PASSED SUCCESSFULLY!
Disposing database connection pool...
```
All tests passed successfully, confirming correct implementation of constraints, dynamic/static route access limits, ordering rules, global timestamp updates, and validator filters.
