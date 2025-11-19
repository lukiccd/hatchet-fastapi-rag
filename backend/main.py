from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil

from workflows.kb import (
    kb_create,
    kb_get,
    kb_upload,
    kb_query,
    KnowledgeBaseUploadInput,
    KnowledgeBaseCreateRequest,
    KnowledgeBaseQuery
)
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

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Hey there, Hatchet API running"}


@app.get("/knowledge-bases")
async def list_knowledge_bases():
    return {"data": kb_get.run()}

@app.post("/knowledge-bases")
async def create_knowledge_base(payload: KnowledgeBaseCreateRequest):
    return {"data": kb_create.run(payload)}

@app.post("/knowledge-bases/upload")
async def upload_document(
    kb_id: str = Form(...),
    file: UploadFile = File(...)
):
    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = await kb_upload.aio_run(
        KnowledgeBaseUploadInput(kb_id=kb_id, file_path=str(file_path))
    )

    return {"data": result}

@app.post("/chat/query")
async def chat_query(payload: KnowledgeBaseQuery):
    response = await kb_query.aio_run(payload)
    return {"data": response}
