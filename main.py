from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

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
