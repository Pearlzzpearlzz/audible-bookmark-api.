from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
from gtts import gTTS
from fastapi.responses import FileResponse

# ======================
# Database setup
# ======================
DATABASE_URL = os.getenv("DATABASE_URL")  # Render Env Var
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    book = Column(String, index=True)
    position = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# ======================
# FastAPI app
# ======================
app = FastAPI()

class SaveRequest(BaseModel):
    user: str
    book: str
    position: int

class ReadRequest(BaseModel):
    user: str
    book: str

class SpeakRequest(BaseModel):
    user: str
    book: str
    text: str

@app.post("/save")
def save_bookmark(req: SaveRequest):
    db = SessionLocal()
    bookmark = Bookmark(user_id=req.user, book=req.book, position=req.position)
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    db.close()
    return {"message": "Bookmark saved", "bookmark": {
        "user": req.user, "book": req.book, "position": req.position
    }}

@app.post("/get")
def get_bookmark(req: ReadRequest):
    db = SessionLocal()
    bookmark = db.query(Bookmark).filter_by(user_id=req.user, book=req.book).order_by(Bookmark.created_at.desc()).first()
    db.close()
    if bookmark:
        return {"user": bookmark.user_id, "book": bookmark.book, "position": bookmark.position}
    return {"message": "No bookmark found"}

@app.post("/speak")
def speak_text(req: SpeakRequest):
    filename = f"{req.user}_{req.book}_spoken.mp3"
    tts = gTTS(req.text)
    tts.save(filename)
    return FileResponse(filename, media_type="audio/mpeg", filename=filename)
