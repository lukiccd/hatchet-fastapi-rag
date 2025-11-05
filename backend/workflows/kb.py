from typing import Union, Optional
import os
import shutil
from dsrag_wrapper import DSRagClient
from dsrag.rse import RSE_PARAMS_PRESETS
from dsrag.knowledge_base import KnowledgeBase
from pathlib import Path
from hatchet_sdk import Context, EmptyModel, Hatchet
from pydantic import BaseModel
import json
from fastapi import File, UploadFile
from agent import agent

dsrag = DSRagClient()
hatchet = Hatchet(debug=True)
class KnowledgeBaseCreateRequest(BaseModel):
    kb_id: str

class KnowledgeBaseCreateResponse(BaseModel):
    kb_id: str
    message: str
    error: Optional[str] = None

class KnowledgeBaseUploadInput(BaseModel):
    kb_id: str
    file_path: str

class KnowledgeBaseUploadOutput(BaseModel):
    filename: str
    message: str
    err: Optional[str] = None

class KnowledgeBaseQuery(BaseModel):
    kb_id: str
    query: str

@hatchet.task(name="kb-create", input_validator=KnowledgeBaseCreateRequest)
def kb_create(input: KnowledgeBaseCreateRequest, ctx: Context):
    try:
        kb = dsrag.create_knowledge_base(kb_id=input.kb_id)
        return {
            "message": "Knowledge base created successfully.",
            "kb_id": kb.kb_id
        }
    except Exception as e:
        return {
            "message": "Failed to create knowledge base.",
            "error": str(e),
            "kb_id": input.kb_id
        }

@hatchet.task(name="kb-get")
def kb_get(input, ctx):
    try:
        knowledge_bases = dsrag.get_knowledge_bases()
        return {
            "message": "Knowledge bases fetched successfully.",
            "knowledge_bases": knowledge_bases
        }
    except Exception as e:
        return {
            "message": "Failed to fetch knowledge bases.",
            "error": str(e),
        }

@hatchet.task(name="kb-upload", input_validator=KnowledgeBaseUploadInput)
def kb_upload(input: KnowledgeBaseUploadInput, ctx: Context):
    try:
        kb = dsrag.upload_file_to_knowledge_base(
            kb_id=input.kb_id, file_path=input.file_path
        )
        os.remove(input.file_path)
        return {"filename": Path(input.file_path).name, "message": "File uploaded successfully."}
    except Exception as e:
        return KnowledgeBaseUploadOutput(
            filename="",
            message="Unable to upload KB",
            error=str(e)
        )

@hatchet.task(name="kb-query")
async def kb_query(input: EmptyModel, ctx: Context) -> None:
    # kb_id = input.kb_id
    # query = input.query
    config = {"configurable": {"thread_id": "1"}}
    kb = KnowledgeBase(kb_id="aaa", exists_ok=True)
    rag_output = kb.query("sta ovaj zakon najvise obuhvata?", rse_params=RSE_PARAMS_PRESETS["find_all"])
    context = dsrag.format_context(rag_output=rag_output)
    # prompt = f"Context:\n{context}\n\nQuestion: {query[0]}"
    prompt = f"Context:\n{context}\n\nQuestion: sta ovaj zakon najvise obuhvata?"
    response = agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]},
        config=config
    )
    print(response)
    return {"response": response}
