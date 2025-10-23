from typing import Union, Optional
import os
import shutil
from dsrag_wrapper import DSRagClient
from dsrag.rse import RSE_PARAMS_PRESETS
from dsrag.knowledge_base import KnowledgeBase
from pathlib import Path
from hatchet_sdk import Context, Hatchet
from pydantic import BaseModel
import json
from fastapi import File, UploadFile

dsrag = DSRagClient()
hatchet = Hatchet(debug=True)

class KnowledgeBaseCreateRequest(BaseModel):
    kb_id: str

class KnowledgeBaseCreateResponse(BaseModel):
    kb_id: str
    message: str
    error: Optional[str] = None

class KnowledgeBaseUploadInput(BaseModel):
    knowledge_base: str
    file: UploadFile = File(...)

class KnowledgeBaseUploadOuptut(BaseModel):
    filename: str
    message: str
    err: Optional[str]

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
# @hatchet.task(name="kb-upload", input_validator=KnowledgeBaseUploadInput)
# def kb_upload(input: KnowledgeBaseUploadInput, ctx: Context):
#     try:
#         upload_dir = "uploads"
#         Path(upload_dir).mkdir(parents=True, exist_ok=True)

#         file_location = os.path.join(upload_dir, input.file.filename)

#         with open(file_location, "wb") as buffer:
#             shutil.copyfileobj(input.file.file, buffer)

#         kb = dsrag.upload_file_to_knowledge_base(
#             kb_id=input.knowledge_base, file_path=file_location
#         )

#         os.remove(file_location)

#         return {
#             "filename": input.file.filename,
#             "message": "File uploaded successfully.",
#         }

#     except Exception as e:
#         return KnowledgeBaseUploadOuptut('', 'Unable to upload KB', e)
