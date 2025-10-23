from typing import Union
import os
import shutil
from fastapi import FastAPI, File, UploadFile
from dsrag_wrapper import DSRagClient
from pydantic import BaseModel
from dsrag.rse import RSE_PARAMS_PRESETS
from dsrag.knowledge_base import KnowledgeBase
from pathlib import Path
from workflows.kb import kb_create, KnowledgeBaseUploadInput, KnowledgeBaseCreateRequest
from agent import agent

app = FastAPI()

class ChatRequest(BaseModel):
    kb_id: str
    query: list[str]

@app.get("/")
def read_root():
    return {"Hey": "Hatchet"}


@app.post("/knowledge-base/create")
async def create_knowledge_base(kb: KnowledgeBaseCreateRequest):
    result = kb_create.run(KnowledgeBaseCreateRequest(kb_id="test"))
    return {"response": result}

# @app.post("/knowledge-base/{knowledge_base}/document/upload")
# async def upload_file_to_knowledge_base(
#     knowledge_base: str, file: UploadFile = File(...)
# ):
#     result = await kb_upload.aio_run(KnowledgeBaseUploadInput(knowledge_base=knowledge_base, file=file))


@app.post("/chat/update")
async def generate_dsrag_chat_completion(chat_req: ChatRequest):
    # kb_id = chat_req.kb_id
    # query = chat_req.query
    # config = {"configurable": {"thread_id": "1"}}
    # kb = KnowledgeBase(kb_id=kb_id, exists_ok=True)
    # rag_output = kb.query(query, rse_params=RSE_PARAMS_PRESETS["find_all"])
    # context = dsrag.format_context(rag_output=rag_output)
    # prompt = f"Context:\n{context}\n\nQuestion: {query[0]}"
    # response = agent.invoke(
    #     {"messages": [{"role": "user", "content": prompt}]},
    #     config=config
    # )
    return {"response": "1"}
