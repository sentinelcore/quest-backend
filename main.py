from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime



app = FastAPI()

# CORS setup for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://PPP.vercel.app", "*"],  # for now allow all
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
from fastapi.responses import JSONResponse

@app.get("/quests")
def get_quests():
    session = Session()
    quests = session.query(Quest).all()
    return [
        {
            "id": q.id,
            "name": q.name,
            "description": q.description
        } for q in quests
    ]

@app.post("/quests")
async def create_quest(request: Request):
    try:
        session = Session()
        data = await request.json()

        q = Quest(
            name=data.get("name", ""),
            description=data.get("description", ""),
            start_time=datetime.fromisoformat(data.get("start_time").replace("Z", "")),
            end_time=datetime.fromisoformat(data.get("end_time").replace("Z", "")),
            is_active=data.get("is_active", True),
            submissions_limit=data.get("submissions_limit", "1_per_user"),
            points_per_submission=data.get("points_per_submission", 0),
            points_mode=data.get("points_mode", "auto"),
            config=data.get("config", {}),
        )

        session.add(q)
        session.commit()
        session.refresh(q)

        return {
            "id": q.id,
            "name": q.name,
            "description": q.description
        }

    except Exception as e:
        print("❌ Backend error:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})



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
