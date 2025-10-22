import warnings
import os
from dsrag.knowledge_base import KnowledgeBase
from dsrag.llm import OpenAIChatAPI
from dsrag.embedding import VoyageAIEmbedding, dimensionality, OpenAIEmbedding
from dsrag.reranker import CohereReranker
from dsrag.create_kb import create_kb_from_file
from dsrag.database.vector.milvus_db import MilvusDB
from dsrag.rse import RSE_PARAMS_PRESETS
from dsrag.dsparse.file_parsing.non_vlm_file_parsing import extract_text_from_pdf
from dsrag.llm import LLM
from dsrag.reranker import Reranker
from dsrag.embedding import Embedding
from openai import OpenAI
from pymilvus import MilvusClient

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Setup models
llm = OpenAIChatAPI(model='gpt-4o-mini')
reranker = CohereReranker(model="rerank-multilingual-v3.0")
embedding = VoyageAIEmbedding(model="voyage-law-2", dimension=1024)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
milvus_client =MilvusClient("./milvus.db")

class DSRagClient():
    def __init__(self, llm: LLM = llm, reranker: Reranker = reranker, embedding: Embedding = embedding, dimension: int = 1024):
        self.llm = llm
        self.reranker = reranker
        self.embedding = embedding
        self.dimension = dimension
        # Initialize session memory (stores last n interactions)
        self.session_memory = []
        self.memory_limit = 5  # Store up to the last 5 interactions

    def create_knowledge_base(self, kb_id: str):
        milvus_db = milvus_client.create_collection(collection_name=kb_id, dimension=1024)
        # milvus_db = MilvusDB(kb_id=kb_id, storage_directory="~/dsRAG", dimension=1024)
        kb = KnowledgeBase(kb_id=kb_id, embedding_model=self.embedding, vector_db=milvus_db, reranker=self.reranker, auto_context_model=self.llm)
        return kb

    def upload_file_to_knowledge_base(self, kb_id: str, file_path: str):
        print(file_path)
        text = extract_text_from_pdf(file_path=file_path)
        kb = KnowledgeBase(kb_id=kb_id)
        kb.add_document(doc_id=file_path.lstrip('./uploads/'), text=text[0])
        return kb

    def add_to_memory(self, user_query: str, model_response: str):
        """Store a new interaction in memory"""
        if len(self.session_memory) >= self.memory_limit:
            # Remove the oldest memory if we exceed the limit
            self.session_memory.pop(0)
        self.session_memory.append({"user_query": user_query, "model_response": model_response})

    def get_memory_context(self):
        """Retrieve the most recent interactions for context"""
        return " ".join([f"User: {entry['user_query']} Model: {entry['model_response']}" for entry in self.session_memory])

    # def query(self, kb_id: str, search_query: str, rse_params: RSE_PARAMS_PRESETS = RSE_PARAMS_PRESETS['find_all']):
    #     # Get memory context (previous interactions)
    #     memory_context = self.get_memory_context()

    #     # Combine memory context with current query
    #     full_query = memory_context + " " + search_query
    #     print(full_query)
    #     # Interact with the knowledge base
    #     kb = KnowledgeBase(kb_id)
    #     results = kb.query([full_query], rse_params=rse_params, latency_profiling=True)

    #     self.add_to_memory(search_query, results)

    #     return results

    def format_context(self, rag_output):
        """
        Formats the retrieved chunks into a prompt for the LLM.
        """
        context = []

        # Iterate through each chunk and format it into a readable context
        for idx, chunk in enumerate(rag_output):
            doc_id = chunk["doc_id"]
            content = chunk["content"]
            context.append(f"Document {idx + 1} (ID: {doc_id}): {content}")

        # Join all context pieces into a single string
        context_str = "\n".join(context)

        return context_str

    def get_llm_response(self, prompt):
        """
        Sends the formatted prompt to the LLM (e.g., GPT-3 or GPT-4) and returns the response.
        """
        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="gpt-4o-mini"
            )
            return response.choices[0].dict()['message']['content']

        except Exception as e:
            print(f"Error with OpenAI API: {e}")
            return None

dsr = DSRagClient(llm=llm, reranker=reranker, embedding=embedding, dimension=1024)

kb_id = 'test_dass'
file_path = 'prinos.pdf'
dsr.create_knowledge_base(kb_id=kb_id)

dsr.upload_file_to_knowledge_base(kb_id=kb_id, file_path=file_path)

nomem = dsr.query(kb_id=kb_id, search_query="koliki je prinos fonda")
print(nomem[0])
