#  Spoken API
 

This is a Fast API project that provides audible bookmarking for digital text.

## Features
- Save bookmark: store a user's last read position in a book.
- Get bookmark: retrieve the saved position.
- Read aloud: convert text to speech and generate an audio file with a resume point.

## Endpoints
- `POST /saveBookmark` → Save last position.
- `GET /getBookmark/{user}/{book}` → Retrieve bookmark.
- `POST /read` → Convert text to speech and return audio file link.

## Requirements
- Python 3.9+
- Dependencies (see `requirements.txt`):
  - fastapi
  - uvicorn
  - gtts

## Running locally
```bash
uvicorn main:app --reload
