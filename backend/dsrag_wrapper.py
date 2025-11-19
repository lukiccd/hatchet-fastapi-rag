from dsrag.knowledge_base import KnowledgeBase
from dsrag.database.vector.basic_db import BasicVectorDB
from dsrag.dsparse.file_parsing.non_vlm_file_parsing import extract_text_from_pdf
from dsrag.llm import LLM
from dsrag.reranker import Reranker
from dsrag.embedding import Embedding
from pathlib import Path

class DSRagClient():
    def __init__(self, llm: LLM, reranker: Reranker, embedding: Embedding, dimension: int = 1024):
        self.llm = llm
        self.reranker = reranker
        self.embedding = embedding
        self.dimension = dimension

    def get_knowledge_bases(self) -> list[str]:
        try:
            base_dir = Path.home() / "dsRAG" / "metadata"
            if not base_dir.exists():
                return []

            kb_files = base_dir.glob("*.json")
            kb_ids = [f.stem for f in kb_files]  # remove .json

            return kb_ids

        except Exception as e:
            print(f"Error retrieving knowledge bases: {e}")
            return []

    def create_knowledge_base(self, kb_id: str):
        vector_db = BasicVectorDB(kb_id=kb_id)
        kb = KnowledgeBase(
            kb_id=kb_id,
            embedding_model=self.embedding,
            vector_db=vector_db,
            reranker=self.reranker,
            auto_context_model=self.llm
        )
        return kb

    async def upload_file_to_knowledge_base(self, kb_id: str, file_path: str):
        text = extract_text_from_pdf(file_path=file_path)
        kb = KnowledgeBase(kb_id=kb_id)
        kb.add_document(doc_id=file_path.lstrip('./uploads/'), text=text[0])
        return kb

    def format_context(self, rag_output):
        context = []
        print(rag_output)
        for idx, chunk in enumerate(rag_output):
            doc_id = chunk["doc_id"]
            content = chunk["content"]
            context.append(f"Document {idx + 1} (ID: {doc_id}): {content}")

        context_str = "\n".join(context)

        return context_str
