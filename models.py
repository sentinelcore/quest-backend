from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
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

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    quest_id = Column(Integer, ForeignKey('quests.id'))
    title = Column(String)
    description = Column(Text)
    image_urls = Column(JSON)
    video_urls = Column(JSON)
    points = Column(Integer)
    active = Column(Boolean, default=True)
    issue_points = Column(Boolean, default=True)

class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(Integer, primary_key=True)
    quest_id = Column(Integer, ForeignKey('quests.id'))
    task_id = Column(Integer, ForeignKey('tasks.id'))
    user_wallet = Column(String)
    submission_data = Column(JSON)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default='pending')  # 'pending', 'accepted', 'rejected'
    points_allocated = Column(Integer, default=0)
