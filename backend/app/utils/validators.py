import re

DRIVE_REGEX = re.compile(r"^https?://(drive|docs)\.google\.com/", re.IGNORECASE)
GITHUB_REGEX = re.compile(r"^https?://(www\.)?github\.com/", re.IGNORECASE)
LINKEDIN_REGEX = re.compile(r"^https?://(www\.)?linkedin\.com/", re.IGNORECASE)
YOUTUBE_REGEX = re.compile(r"^https?://(www\.)?(youtube\.com|youtu\.be|m\.youtube\.com)/", re.IGNORECASE)

def validate_youtube(v: str) -> str:
    if not v:
        return v
    if not YOUTUBE_REGEX.match(v):
        raise ValueError("Must be a valid YouTube link containing youtube.com or youtu.be")
    return v

def validate_google_drive(v: str) -> str:
    if not v:
        return v
    if not DRIVE_REGEX.match(v):
        raise ValueError("Must be a valid Google Drive link containing drive.google.com or docs.google.com")
    return v

def validate_github(v: str) -> str:
    if not v:
        return v
    if not GITHUB_REGEX.match(v):
        raise ValueError("Must be a valid GitHub link containing github.com")
    return v

def validate_linkedin(v: str) -> str:
    if not v:
        return v
    if not LINKEDIN_REGEX.match(v):
        raise ValueError("Must be a valid LinkedIn link containing linkedin.com")
    return v
