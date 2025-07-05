# main.py

import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from rag import summarize_with_rag, answer_question_with_rag

app = FastAPI()

# Allow frontend access (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to store uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Store path of last uploaded file for question-answering
file_storage = {"last_file_path": None}


@app.post("/summarize")
async def summarize(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    file_storage["last_file_path"] = file_path

    summary = summarize_with_rag(file_path)
    return {"summary": summary}


@app.post("/ask")
async def ask_question(question: str = Form(...)):
    file_path = file_storage.get("last_file_path")
    if not file_path or not os.path.exists(file_path):
        return {"answer": "No document uploaded yet. Please summarize a document first."}

    answer = answer_question_with_rag(file_path, question)
    return {"answer": answer}
