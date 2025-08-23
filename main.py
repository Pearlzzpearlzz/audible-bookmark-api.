from fastapi import FastAPI
from pydantic import BaseModel
from gtts import gTTS
import json, os

app = FastAPI()

BOOKMARK_FILE = "bookmarks.json"

# Make sure bookmark storage exists
if not os.path.exists(BOOKMARK_FILE):
    with open(BOOKMARK_FILE, "w") as f:
        json.dump({}, f)

# Request models
class SaveRequest(BaseModel):
    user: str
    book: str
    position: int

class ReadRequest(BaseModel):
    user: str
    book: str
    text: str
    position: int

# --- Helpers ---
def save_bookmark(user, book, position):
    with open(BOOKMARK_FILE, "r") as f:
        data = json.load(f)
    if user not in data:
        data[user] = {}
    data[user][book] = position
    with open(BOOKMARK_FILE, "w") as f:
        json.dump(data, f)

def load_bookmark(user, book):
    with open(BOOKMARK_FILE, "r") as f:
        data = json.load(f)
    return data.get(user, {}).get(book, 0)

# --- Endpoints ---
@app.post("/saveBookmark")
def save(req: SaveRequest):
    save_bookmark(req.user, req.book, req.position)
    return {"status": "saved", "user": req.user, "book": req.book, "position": req.position}

@app.get("/getBookmark/{user}/{book}")
def get(user: str, book: str):
    position = load_bookmark(user, book)
    return {"user": user, "book": book, "last_position": position}

@app.post("/read")
def read(req: ReadRequest):
    # Generate audio for given text
    tts = gTTS(req.text)
    filename = f"{req.user}_{req.book}_{req.position}.mp3"
    tts.save(filename)
    audio_url = f"/audio/{filename}"
    return {
        "user": req.user,
        "book": req.book,
        "position": req.position,
        "audio_url": audio_url
    }

# Serve audio files
from fastapi.staticfiles import StaticFiles
app.mount("/audio", StaticFiles(directory="."), name="audio")
