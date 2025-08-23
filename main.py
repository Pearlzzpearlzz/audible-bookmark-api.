from fastapi import FastAPI, Request
from pydantic import BaseModel
from gtts import gTTS
import json, os, datetime

# Initialize FastAPI
app = FastAPI()

# Bookmark storage file
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

# Middleware for logging all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    user_agent = request.headers.get("user-agent", "unknown")
    path = request.url.path
    timestamp = datetime.datetime.now().isoformat()

    # Print to Render logs
    print(f"[{timestamp}] User Agent: {user_agent} | Path: {path}")

    response = await call_next(request)
    return response

# Save bookmark
@app.post("/save")
def save_bookmark(req: SaveRequest):
    with open(BOOKMARK_FILE, "r") as f:
        bookmarks = json.load(f)

    key = f"{req.user}_{req.book}"
    bookmarks[key] = req.position

    with open(BOOKMARK_FILE, "w") as f:
        json.dump(bookmarks, f)

    return {"message": "Bookmark saved", "key": key, "position": req.position}

# Get bookmark
@app.post("/get")
def get_bookmark(req: ReadRequest):
    with open(BOOKMARK_FILE, "r") as f:
        bookmarks = json.load(f)

    key = f"{req.user}_{req.book}"
    position = bookmarks.get(key)

    if position is None:
        return {"message": "No bookmark found"}

    return {"user": req.user, "book": req.book, "position": position}

# Generate speech
@app.post("/speak")
def speak_text(req: ReadRequest):
    text = f"{req.user}, your last position in {req.book} is saved."
    tts = gTTS(text)
    filename = f"{req.user}_{req.book}.mp3"
    tts.save(filename)

    return {"message": "Audio generated", "file": filename}

