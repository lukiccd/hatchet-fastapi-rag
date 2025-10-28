from hatchet_sdk import Hatchet
from workflows.kb import kb_create, kb_get, kb_upload, kb_query

hatchet = Hatchet(debug=True)

def main() -> None:
    worker = hatchet.worker("rag-agent", workflows=[kb_create, kb_get, kb_upload, kb_query])

    worker.start()

if __name__ == "__main__":
    main()
