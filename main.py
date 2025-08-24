
from fastapi import FastAPI
from pydantic import BaseModel
from gtts import gTTS
import json, os
from datetime import datetime

app = FastAPI()

# Storage file
BOOKMARK_FILE = "bookmarks.json"

# Make sure bookmarks file exists
if not os.path.exists(BOOKMARK_FILE):
    with open(BOOKMARK_FILE, "w") as f:
        json.dump({}, f)

# ------------------------------
# Models
# ------------------------------
class SaveRequest(BaseModel):
    user: str
    book: str
    position: int

class ReadRequest(BaseModel):
    user: str
    book: str

class SpeakRequest(BaseModel):
    text: str

# ------------------------------
# Endpoints
# ------------------------------

@app.post("/save")
def save_bookmark(req: SaveRequest):
    """Save a bookmark for a user + book"""
    with open(BOOKMARK_FILE, "r") as f:
        bookmarks = json.load(f)

    bookmarks[f"{req.user}:{req.book}"] = req.position

    with open(BOOKMARK_FILE, "w") as f:
        json.dump(bookmarks, f)

    return {"message": "Bookmark saved", "user": req.user, "book": req.book, "position": req.position}


@app.post("/get")
def get_bookmark(req: ReadRequest):
    """Retrieve a bookmark for a user + book"""
    with open(BOOKMARK_FILE, "r") as f:
        bookmarks = json.load(f)

    key = f"{req.user}:{req.book}"
    position = bookmarks.get(key)

    if position is None:
        return {"message": "No bookmark found"}

    return {"user": req.user, "book": req.book, "position": position}


@app.post("/speak")
def speak_text(req: SpeakRequest):
    """Convert text to speech"""
    tts = gTTS(req.text)
    filename = f"speech_{datetime.now().timestamp()}.mp3"
    tts.save(filename)

    return {"message": "Speech generated", "file": filename}
