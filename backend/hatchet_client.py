from hatchet_sdk import Hatchet
from workflows.kb import kb_create

hatchet = Hatchet(debug=True)

def main() -> None:
    worker = hatchet.worker("rag-agent", workflows=[kb_create])

    worker.start()

if __name__ == "__main__":
    main()
