import warnings
from dsrag.knowledge_base import KnowledgeBase
from dsrag.database.vector.milvus_db import MilvusDB
from dsrag.dsparse.file_parsing.non_vlm_file_parsing import extract_text_from_pdf
from dsrag.llm import LLM
from dsrag.reranker import Reranker
from dsrag.embedding import Embedding
from pymilvus import MilvusClient
from functools import lru_cache
from dsrag.database.vector.milvus_db import MilvusDB


@lru_cache()
def get_milvus_client() -> MilvusClient:
    return MilvusClient("./milvus.db")

warnings.filterwarnings("ignore", category=DeprecationWarning)

class DSRagClient():
    def __init__(self, llm: LLM, reranker: Reranker, embedding: Embedding, dimension: int = 1024):
        self.llm = llm
        self.reranker = reranker
        self.embedding = embedding
        self.dimension = dimension

    def get_knowledge_bases(self):
        """
        Retrieve a list of all existing knowledge bases (collections) in Milvus.

        Returns:
            List[str]: A list of knowledge base (collection) names.
        """
        try:
            milvus_db = get_milvus_client()
            collections = milvus_db.list_collections()

            if not collections:
                print("No knowledge bases found in Milvus.")
                return []

            return collections

        except Exception as e:
            print(f"Error retrieving knowledge bases: {e}")
            return []


    def create_knowledge_base(self, kb_id: str):
        # milvus_db = get_milvus_client().create_collection(collection_name=kb_id, dimension=1024)
        milvus_db = MilvusDB(kb_id=kb_id, storage_directory="~/dsRAG", dimension=1024)
        kb = KnowledgeBase(
            kb_id=kb_id,
            embedding_model=self.embedding,
            vector_db=milvus_db,
            reranker=self.reranker,
            auto_context_model=self.llm
        )
        return kb

    def upload_file_to_knowledge_base(self, kb_id: str, file_path: str):
        text = extract_text_from_pdf(file_path=file_path)
        kb = KnowledgeBase(kb_id=kb_id)
        kb.add_document(doc_id=file_path.lstrip('./uploads/'), text=text[0])
        return kb

    def format_context(self, rag_output):
        """
        Formats the retrieved chunks into a prompt for the LLM.
        """
        context = []
        print(rag_output)
        # Iterate through each chunk and format it into a readable context
        for idx, chunk in enumerate(rag_output):
            doc_id = chunk["doc_id"]
            content = chunk["content"]
            context.append(f"Document {idx + 1} (ID: {doc_id}): {content}")

        # Join all context pieces into a single string
        context_str = "\n".join(context)

        return context_str
