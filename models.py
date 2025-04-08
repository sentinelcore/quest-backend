from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Quest(Base):
    __tablename__ = 'quests'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    submissions_limit = Column(String)
    points_per_submission = Column(Integer)
    points_mode = Column(String)
    config = Column(JSON)
