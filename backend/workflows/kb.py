from hatchet_sdk import Context, EmptyModel, Hatchet
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from dsrag_wrapper import DSRagClient
from dsrag.knowledge_base import KnowledgeBase
from dsrag.llm import OpenAIChatAPI
from dsrag.embedding import VoyageAIEmbedding
from dsrag.reranker import CohereReranker
from dsrag.rse import RSE_PARAMS_PRESETS
from agent import agent

llm = OpenAIChatAPI(model='gpt-4o-mini')
reranker = CohereReranker(model="rerank-multilingual-v3.0")
embedding = VoyageAIEmbedding(model="voyage-law-2", dimension=1024)

dsrag = DSRagClient(llm=llm, reranker=reranker, embedding=embedding, dimension=1024)
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
async def kb_upload(input: KnowledgeBaseUploadInput, ctx: Context):
    try:
        await dsrag.upload_file_to_knowledge_base(
            kb_id=input.kb_id, file_path=input.file_path
        )
        return {"filename": Path(input.file_path).name, "message": "File uploaded successfully."}
    except Exception as e:
        return KnowledgeBaseUploadOutput(
            filename="",
            message="Unable to upload KB",
            error=str(e)
        )

@hatchet.task(name="kb-query")
async def kb_query(input: EmptyModel, ctx: Context) -> None:
    kb_id = input.kb_id
    query = input.query
    config = {"configurable": {"thread_id": "2"}}
    kb = KnowledgeBase(kb_id=kb_id, exists_ok=True)
    rag_output = kb.query(search_queries=[query], rse_params=RSE_PARAMS_PRESETS["balanced"])
    print(rag_output)
    context = dsrag.format_context(rag_output=rag_output)
    prompt = f"Context:\n{context}\n\nQuestion: {query}"
    response = agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]},
        config=config
    )
    print(response)
    return {"response": response}
