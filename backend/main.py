from typing import Union
import os
import shutil
from fastapi import FastAPI, File, UploadFile
from dsrag_wrapper import DSRagClient
from pydantic import BaseModel
from dsrag.rse import RSE_PARAMS_PRESETS
from dsrag.knowledge_base import KnowledgeBase
from pathlib import Path

app = FastAPI()
dsrag = DSRagClient()


class ChatRequest(BaseModel):
    kb_id: str
    query: list[str]


class KnowledgeBaseCreateRequest(BaseModel):
    kb_id: str


class KnowledgeBaseDocumentUpload(BaseModel):
    kb_id: str
    file: UploadFile = File(...)


@app.get("/")
def read_root():
    return {"Hello": "Hatchet"}


@app.post("/knowledge-base/create")
def create_knowledge_base(kb: KnowledgeBaseCreateRequest):
    return dsrag.create_knowledge_base(kb_id=kb.kb_id).kb_id


@app.post("/knowledge-base/{knowledge_base}/document/upload")
async def upload_file_to_knowledge_base(
    knowledge_base: str, file: UploadFile = File(...)
):
    try:
        # Create a directory for storing the files (if it doesn't exist)
        upload_dir = "uploads"
        Path(upload_dir).mkdir(parents=True, exist_ok=True)

        file_location = os.path.join(upload_dir, file.filename)

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        kb = dsrag.upload_file_to_knowledge_base(
            kb_id=knowledge_base, file_path=file_location
        )

        os.remove(file_location)

        return {
            "filename": file.filename,
            "message": "File uploaded successfully.",
            "kb": kb.kb_metadata,
        }

    except Exception as e:
        print(e)
        return {"err": e}


@app.post("/chat/update")
async def generate_dsrag_chat_completion(chat_req: ChatRequest):
    kb_id = chat_req.kb_id
    query = chat_req.query
    kb = KnowledgeBase(kb_id=kb_id, exists_ok=True)
    rag_output = kb.query(query, rse_params=RSE_PARAMS_PRESETS["find_all"])
    context = dsrag.format_context(rag_output=rag_output)
    prompt = f"Context:\n{context}\n\nQuestion: {query[0]}"
    response = dsrag.get_llm_response(prompt=prompt)
    return {"response": response}
