from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from databases import Database
from typing import Optional

DATABASE_URL = "postgresql://iptvchannels_user:wz0o8A385fhOQbKxjQbIdZqoMaWmTHng@dpg-clqqgcpjvg7s73e9jsq0-a:5432/iptvchannels"

database = Database(DATABASE_URL)
metadata = declarative_base()

class IPTVChannel(metadata):
    __tablename__ = "iptv_channels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    logo = Column(String)  # New column for logo URL
    genre = Column(String)
    stream_url = Column(String)
    drm_key = Column(String, nullable=True)
    lang = Column(String, default="English")  # Default language is set to English

metadata.metadata.create_all(bind=database)

class IPTVChannelCreateUpdate(BaseModel):
    name: str
    logo: str
    genre: str
    stream_url: str
    drm_key: Optional[str] = None
    lang: Optional[str] = "English"  # Default language is set to English

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new IPTV channel
@app.post("/channels/", response_model=IPTVChannel)
async def create_channel(channel: IPTVChannelCreateUpdate, db: Session = Depends(get_db)):
    db_channel = IPTVChannel(**channel.dict())
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel

# Read all IPTV channels
@app.get("/channels/", response_model=List[IPTVChannel])
async def read_channels(db: Session = Depends(get_db)):
    channels = db.query(IPTVChannel).all()
    return channels

# Read a specific IPTV channel by ID
@app.get("/channels/{channel_id}", response_model=IPTVChannel)
async def read_channel(channel_id: int, db: Session = Depends(get_db)):
    channel = db.query(IPTVChannel).filter(IPTVChannel.id == channel_id).first()
    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel

# Update an IPTV channel by ID
@app.put("/channels/{channel_id}", response_model=IPTVChannel)
async def update_channel(channel_id: int, updated_channel: IPTVChannelCreateUpdate, db: Session = Depends(get_db)):
    db_channel = db.query(IPTVChannel).filter(IPTVChannel.id == channel_id).first()
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")

    for key, value in updated_channel.dict().items():
        setattr(db_channel, key, value)

    db.commit()
    db.refresh(db_channel)
    return db_channel

# Delete an IPTV channel by ID
@app.delete("/channels/{channel_id}", response_model=IPTVChannel)
async def delete_channel(channel_id: int, db: Session = Depends(get_db)):
    channel = db.query(IPTVChannel).filter(IPTVChannel.id == channel_id).first()
    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")

    db.delete(channel)
    db.commit()
    return channel
