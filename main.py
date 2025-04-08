from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

engine = create_engine("sqlite:///./quests.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@app.get("/")
def read_root():
    return {"message": "DeCharge Spark is live"}

@app.post("/quests")
def create_quest(quest: dict):
    session = Session()
    q = Quest(**quest)
    session.add(q)
    session.commit()
    return {"message": "Quest created", "id": q.id}

@app.get("/quests")
def list_quests():
    session = Session()
    return session.query(Quest).all()

@app.post("/quests/{quest_id}/tasks")
def create_task(quest_id: int, task: dict):
    session = Session()
    task['quest_id'] = quest_id
    t = Task(**task)
    session.add(t)
    session.commit()
    return {"message": "Task created", "id": t.id}

@app.get("/quests/{quest_id}/tasks")
def get_tasks_for_quest(quest_id: int):
    session = Session()
    return session.query(Task).filter(Task.quest_id == quest_id).all()

@app.post("/tasks/{task_id}/submit")
def submit_task(task_id: int, submission: dict):
    session = Session()
    task = session.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    s = Submission(**submission, task_id=task_id, quest_id=task.quest_id)
    if task.issue_points:
        s.points_allocated = task.points
        s.status = "accepted"
    session.add(s)
    session.commit()
    return {"message": "Submission received"}

@app.get("/quests/{quest_id}/submissions")
def get_submissions(quest_id: int):
    session = Session()
    return session.query(Submission).filter(Submission.quest_id == quest_id).all()

@app.post("/submissions/{submission_id}/status")
def update_submission_status(submission_id: int, status: str, points: int = 0):
    session = Session()
    s = session.query(Submission).filter(Submission.id == submission_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Submission not found")
    s.status = status
    s.points_allocated = points
    session.commit()
    return {"message": f"Submission marked as {status}"}
