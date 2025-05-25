import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

with open("q-vercel-python.json", "r") as file:
    data = json.load(file)

marks = {student["name"]: student["marks"] for student in data}


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/api")
def get_marks(names: List[str] = Query(..., alias="name")):
    marks_data = []
    for name in names:
        marks_data.append(marks.get(name))

    return {"marks": marks_data}