from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from gtts import gTTS

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Setup database engine
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
    text = Column(Text, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

# Pydantic models
class SaveRequest(BaseModel):
    user: str
    book: str
    position: int
    text: str = None

class GetRequest(BaseModel):
    user: str
    book: str

class SpeakRequest(BaseModel):
    text: str

# Endpoints
@app.post("/save")
def save_bookmark(request: SaveRequest):
    db = SessionLocal()
    bookmark = db.query(Bookmark).filter_by(user=request.user, book=request.book).first()
    if bookmark:
        bookmark.position = request.position
        bookmark.text = request.text
    else:
        bookmark = Bookmark(user=request.user, book=request.book, position=request.position, text=request.text)
        db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    db.close()
    return {"message": "Bookmark saved", "user": request.user, "book": request.book, "position": request.position}

@app.post("/get")
def get_bookmark(request: GetRequest):
    db = SessionLocal()
    bookmark = db.query(Bookmark).filter_by(user=request.user, book=request.book).first()
    db.close()
    if not bookmark:
        return {"message": "No bookmark found"}
    return {"user": bookmark.user, "book": bookmark.book, "position": bookmark.position, "text": bookmark.text}

@app.post("/speak")
def speak_text(request: SpeakRequest):
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required")
    filename = "spoken.mp3"
    tts = gTTS(request.text)
    tts.save(filename)
    return {"message": "Text converted to speech", "file": filename}
