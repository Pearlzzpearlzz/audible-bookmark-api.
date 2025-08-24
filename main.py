from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from gtts import gTTS
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database setup (Render will give you DATABASE_URL)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")  # fallback to local sqlite
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database model
class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, index=True)
    book = Column(String, index=True)
    position = Column(Integer)

Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

# Request models
class SaveRequest(BaseModel):
    user: str
    book: str
    position: int

class ReadRequest(BaseModel):
    user: str
    book: str

class SpeakRequest(BaseModel):
    text: str

# Save bookmark
@app.post("/save")
def save_bookmark(request: SaveRequest):
    db = SessionLocal()
    bookmark = db.query(Bookmark).filter(Bookmark.user == request.user, Bookmark.book == request.book).first()
    if bookmark:
        bookmark.position = request.position
    else:
        bookmark = Bookmark(user=request.user, book=request.book, position=request.position)
        db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    db.close()
    return {"message": "Bookmark saved", "user": bookmark.user, "book": bookmark.book, "position": bookmark.position}

# Get bookmark
@app.post("/get")
def get_bookmark(request: ReadRequest):
    db = SessionLocal()
    bookmark = db.query(Bookmark).filter(Bookmark.user == request.user, Bookmark.book == request.book).first()
    db.close()
    if not bookmark:
        return {"message": "No bookmark found"}
    return {"user": bookmark.user, "book": bookmark.book, "position": bookmark.position}

# Speak text
@app.post("/speak")
def speak_text(request: SpeakRequest):
    filename = "speech.mp3"
    tts = gTTS(text=request.text, lang="en")
    tts.save(filename)
    return FileResponse(filename, media_type="audio/mpeg", filename=filename)

