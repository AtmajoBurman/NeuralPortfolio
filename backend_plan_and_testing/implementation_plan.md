# Implementation Plan - Professional Portfolio Backend

We will build a robust, production-ready FastAPI backend using **SQLModel** (which integrates SQLAlchemy and Pydantic) and PostgreSQL (Neon via **asyncpg**). The design divides tables into **Dynamic** (supporting Full CRUD) and **Static** (supporting update-only).

---

## User Review Required

Please review the following design decisions:
> [!IMPORTANT]
> - **Static Table Seeding**: Since `cgpa_tracker` and `student_details` are static (support only updates, no insertions/deletions), we will automatically seed a default row (with ID `1`) for both tables when the application starts, if they do not already exist. This ensures that the frontend can immediately fetch and update student details and CGPA.
> - **Global `updated_at` Sync**: Whenever *any* modification (Create, Update, Delete) is successfully performed on any table in the database, the backend will automatically update the `updated_at` field in the `student_details` table to the current time.
> - **Field Length Limits**:
>   - `student_details.bio`: Max 1000 characters.
>   - `student_details.name`: Max 100 characters.
>   - `chit_chat.description`: Max 280 characters.
> - **URL and Drive Validation**:
>   - **Google Drive Validator**: Assures the link contains `drive.google.com` or `docs.google.com`.
>   - **LinkedIn Validator**: Assures the link contains `linkedin.com`.
>   - **GitHub Validator**: Assures the link contains `github.com`.

---

## Open Questions

None at this time. All requirements are clear.

---

## Proposed Changes

We will organize the code inside the `backend` directory.

### Directory Structure
```
backend/
├── .env                  # Simlinked or copied from root
├── requirements.txt      # Project dependencies
├── run.py                # Server entry point
└── app/
    ├── __init__.py
    ├── config.py         # Config loader (Pydantic Settings)
    ├── database.py       # Async engine & session helper
    ├── main.py           # FastAPI app initialization & lifecycle hooks
    ├── models/           # SQLModel database models & Pydantic schemas
    │   ├── __init__.py
    │   ├── achievements.py
    │   ├── cgpa.py
    │   ├── chitchat.py
    │   ├── profile.py
    │   ├── project.py
    │   ├── sgpa.py
    │   └── student_details.py
    ├── routers/          # FastAPI routes
    │   ├── __init__.py
    │   ├── achievements.py
    │   ├── chatbot.py
    │   ├── cgpa.py
    │   ├── chitchat.py
    │   ├── profile.py
    │   ├── project.py
    │   ├── sgpa.py
    │   └── student_details.py
    └── utils/            # Helper functions and validators
        ├── __init__.py
        ├── db_helpers.py # Syncs updated_at in student_details
        └── validators.py # Reusable URL and drive link validators
```

---

### Component Details

#### 1. Models & Database Representation

We will define each entity using SQLModel. To support clean Pydantic validations (e.g. `AnyUrl`, `EmailStr`) while maintaining standard database serialization, we will separate the database representation from the request schema.

##### [NEW] [validators.py](file:///c:/Users/MyPC/OneDrive/Documents/professional/backend/app/utils/validators.py)
Implements regex validators for Google Drive files/folders, LinkedIn, and GitHub links.
- `validate_google_drive(v: str) -> str`: Checks that the string is a valid URL containing `drive.google.com` or `docs.google.com`.
- `validate_linkedin(v: str) -> str`: Checks that the URL contains `linkedin.com`.
- `validate_github(v: str) -> str`: Checks that the URL contains `github.com`.

##### [NEW] [db_helpers.py](file:///c:/Users/MyPC/OneDrive/Documents/professional/backend/app/utils/db_helpers.py)
Provides a helper `touch_student_details(db: AsyncSession)` that updates the `updated_at` field in `student_details` (where `id = 1`) to the current datetime, committing the change.

##### [NEW] [sgpa.py](file:///c:/Users/MyPC/OneDrive/Documents/professional/backend/app/models/sgpa.py)
- **Table name**: `sgpa_tracker`
- **Fields**:
  - `id`: `int` (Primary key, auto-increment)
  - `semester_name`: `str`
  - `grade`: `float` (Validated to be between `0.00` and `10.00` inclusive, rounded to 2 decimal places)

##### [NEW] [cgpa.py](file:///c:/Users/MyPC/OneDrive/Documents/professional/backend/app/models/cgpa.py)
- **Table name**: `cgpa_tracker`
- **Fields**:
  - `id`: `int` (Primary key, locked to `1` via initialization)
  - `cgpa`: `str` (Default: `"CGPA"`)
  - `grade`: `float` (Validated to be between `0.00` and `10.00` inclusive, rounded to 2 decimal places)

##### [NEW] [profile.py](file:///c:/Users/MyPC/OneDrive/Documents/professional/backend/app/models/profile.py)
- **Table name**: `profiles`
- **Fields**:
  - `id`: `int` (Primary key, auto-increment)
  - `logo`: `str` (Drive picture link, validated via Google Drive validator)
  - `link`: `str` (Valid URL schema)

##### [NEW] [student_details.py](file:///c:/Users/MyPC/OneDrive/Documents/professional/backend/app/models/student_details.py)
- **Table name**: `student_details`
- **Fields**:
  - `id`: `int` (Primary key, locked to `1` via initialization)
  - `name`: `str` (Max 100 characters)
  - `profile_pic`: `str` (Drive picture link, validated via Google Drive validator)
  - `bio`: `str` (Max 1000 characters)
  - `gmail`: `str` (Validated via Pydantic `EmailStr`)
  - `updated_at`: `datetime` (Defaults to current UTC time, updated automatically on any DB write)

##### [NEW] [project.py](file:///c:/Users/MyPC/OneDrive/Documents/professional/backend/app/models/project.py)
- **Table name**: `projects`
- **Fields**:
  - `id`: `int` (Primary key, auto-increment)
  - `project_name`: `str`
  - `project_category`: `str`
  - `tech_stack`: `str`
  - `project_description`: `str`
  - `video_link`: `str` (Google Drive link validator)
  - `github_repo`: `str` (GitHub link validator)
  - `deployed_link`: `str` (Valid URL schema)
  - `linkedin_post`: `str` (LinkedIn link validator)
  - `start_date`: `date`
  - `end_date`: `date` (Optional)
  - `date_added`: `datetime` (Default: `func.now()`)

##### [NEW] [achievement.py](file:///c:/Users/MyPC/OneDrive/Documents/professional/backend/app/models/achievement.py)
- **Table name**: `achievements`
- **Fields**:
  - `id`: `int` (Primary key, auto-increment)
  - `name`: `str`
  - `score_or_grade`: `str`
  - `description`: `str`
  - `view_certificate`: `str` (Google Drive link validator)
  - `picture`: `str` (Google Drive link validator)
  - `linkedin_post`: `str` (LinkedIn link validator)
  - `start_date`: `date`
  - `end_date`: `date` (Optional)
  - `date_added`: `datetime` (Default: `func.now()`)

##### [NEW] [chitchat.py](file:///c:/Users/MyPC/OneDrive/Documents/professional/backend/app/models/chitchat.py)
- **Table name**: `chit_chat`
- **Fields**:
  - `id`: `int` (Primary key, auto-increment)
  - `date_added`: `datetime` (Default: `func.now()`)
  - `link`: `str` (Optional, valid URL)
  - `description`: `str` (Max 280 characters)
  - `date_updated`: `datetime` (Default: `func.now()`, auto-updated on edit)
  - `vanishing_date`: `datetime` (Optional, when it expires and is excluded from GET requests)

---

### 2. Endpoints & Routers

We will build REST endpoints for each of the models:
- **SGPA Tracker**:
  - `POST /api/sgpa`: Add SGPA.
  - `GET /api/sgpa`: List all SGPA records.
  - `PUT /api/sgpa/{id}`: Update SGPA.
  - `DELETE /api/sgpa/{id}`: Delete SGPA.
- **CGPA Tracker** (Static):
  - `GET /api/cgpa`: Retrieve CGPA.
  - `PUT /api/cgpa`: Update CGPA (Always modifies the record with `id = 1`).
- **Profile** (Dynamic):
  - `POST /api/profiles`: Add profile.
  - `GET /api/profiles`: List profiles.
  - `PUT /api/profiles/{id}`: Update profile.
  - `DELETE /api/profiles/{id}`: Delete profile.
- **Student Details** (Static):
  - `GET /api/student_details`: Retrieve student details.
  - `PUT /api/student_details`: Update student details (Always modifies the record with `id = 1`).
- **Projects** (Dynamic):
  - `POST /api/projects`: Add project.
  - `GET /api/projects`: List projects (Ordered by `date_added` descending).
  - `PUT /api/projects/{id}`: Update project.
  - `DELETE /api/projects/{id}`: Delete project.
- **Achievements** (Dynamic):
  - `POST /api/achievements`: Add achievement.
  - `GET /api/achievements`: List achievements (Ordered by `date_added` descending).
  - `PUT /api/achievements/{id}`: Update achievement.
  - `DELETE /api/achievements/{id}`: Delete achievement.
- **Chit-Chat** (Dynamic):
  - `POST /api/chitchat`: Add chit-chat post.
  - `GET /api/chitchat`: List chit-chat posts (Excludes posts where `vanishing_date < now`).
  - `PUT /api/chitchat/{id}`: Update chit-chat.
  - `DELETE /api/chitchat/{id}`: Delete chit-chat.
- **Chatbot** (Future Placeholder):
  - `POST /api/chatbot`: Returns a message stating chatbot implementation is coming soon.

---

## Verification Plan

### Automated Tests
We will write a python script `test_backend.py` inside `backend/tests/` to perform automated verification of the endpoints against a mock or live Neon database.
- Verifies input validation constraints (0-10 float ranges, google drive regex, linkedin/github domains).
- Verifies that static tables only permit updates, and seed correctly.
- Verifies that any database write triggers the `student_details.updated_at` modification.
- Verifies order of Projects/Achievements is sorted by `date_added` descending.

### Manual Verification
- Run the FastAPI server locally (`uvicorn app.main:app --reload`).
- Open `/docs` (Swagger UI) in the browser to interactively test all endpoints.
