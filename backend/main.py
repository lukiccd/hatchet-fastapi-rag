from typing import Union
import os
import shutil
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dsrag_wrapper import DSRagClient
from pydantic import BaseModel
from dsrag.rse import RSE_PARAMS_PRESETS
from dsrag.knowledge_base import KnowledgeBase
from pathlib import Path
from workflows.kb import kb_create, kb_get, kb_upload, kb_query, KnowledgeBaseUploadInput, KnowledgeBaseCreateRequest, KnowledgeBaseQuery
from agent import agent

app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return {"Hey": "Hatchet"}


@app.get("/knowledge-base/get")
async def get_knowledge_bases():
    knowledge_bases = kb_get.run()
    return {"response": knowledge_bases}

@app.post("/knowledge-base/create")
async def create_knowledge_base(kb: KnowledgeBaseCreateRequest):
    result = kb_create.run(KnowledgeBaseCreateRequest(kb_id=kb.kb_id))
    return {"response": result}

@app.post("/knowledge-base/document/upload")
async def upload_file_to_knowledge_base(
    kb_id: str = Form(...),
    file: UploadFile = File(...),
):
    upload_dir = "./uploads"
    Path(upload_dir).mkdir(parents=True, exist_ok=True)

    # Save file temporarily
    file_location = os.path.join(upload_dir, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Pass only JSON-serializable fields to Hatchet
    result = kb_upload.run(
        KnowledgeBaseUploadInput(kb_id=kb_id, file_path=file_location)
    )

    return result


@app.post("/chat/update")
async def generate_dsrag_chat_completion():
    # kb_id = input.kb_id
    # query = input.query
    response = await kb_query.aio_run()
    return response
