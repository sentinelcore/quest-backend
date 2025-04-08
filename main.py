from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

app = FastAPI()

# CORS setup for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
engine = create_engine("sqlite:///./quests.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@app.get("/")
def read_root():
    return {"message": "DeCharge Spark is live"}

# ✅ Create Quest - updated to support JSON directly
@app.post("/quests")
async def create_quest(request: Request):
    session = Session()
    data = await request.json()

    q = Quest(
        name=data["name"],
        description=data["description"],
        start_time=data.get("start_time"),
        end_time=data.get("end_time"),
        is_active=data.get("is_active", True),
        submissions_limit=data.get("submissions_limit"),
        points_per_submission=data.get("points_per_submission", 0),
        points_mode=data.get("points_mode", "manual"),
        config=data.get("config", {}),
    )
    session.add(q)
    session.commit()
    return {"message": "Quest created", "id": q.id}

# ✅ Get All Quests
@app.get("/quests")
def list_quests():
    session = Session()
    return session.query(Quest).all()

# ✅ Create Task for a Quest
@app.post("/quests/{quest_id}/tasks")
async def create_task(quest_id: int, request: Request):
    session = Session()
    data = await request.json()
    task = Task(
        quest_id=quest_id,
        title=data["title"],
        description=data["description"],
        image_urls=data.get("image_urls", []),
        video_urls=data.get("video_urls", []),
        points=data.get("points", 0),
        active=data.get("active", True),
        issue_points=data.get("issue_points", True)
    )
    session.add(task)
    session.commit()
    return {"message": "Task created", "id": task.id}

# ✅ Get All Tasks for a Quest
@app.get("/quests/{quest_id}/tasks")
def get_tasks_for_quest(quest_id: int):
    session = Session()
    return session.query(Task).filter(Task.quest_id == quest_id).all()

# ✅ Submit a Task (as user)
@app.post("/tasks/{task_id}/submit")
async def submit_task(task_id: int, request: Request):
    session = Session()
    data = await request.json()

    task = session.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    s = Submission(
        task_id=task_id,
        quest_id=task.quest_id,
        user_wallet=data.get("user_wallet"),
        submission_data=data.get("submission_data", {}),
        submitted_at=datetime.utcnow(),
        status="accepted" if task.issue_points else "pending",
        points_allocated=task.points if task.issue_points else 0,
    )
    session.add(s)
    session.commit()
    return {"message": "Submission received", "id": s.id}

# ✅ Get All Submissions for a Quest
@app.get("/quests/{quest_id}/submissions")
def get_submissions(quest_id: int):
    session = Session()
    return session.query(Submission).filter(Submission.quest_id == quest_id).all()

# ✅ Update Submission Status (accept/reject)
@app.post("/submissions/{submission_id}/status")
async def update_submission_status(submission_id: int, request: Request):
    session = Session()
    data = await request.json()

    s = session.query(Submission).filter(Submission.id == submission_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Submission not found")

    s.status = data["status"]
    s.points_allocated = data.get("points", 0)
    session.commit()
    return {"message": f"Submission marked as {s.status}"}
