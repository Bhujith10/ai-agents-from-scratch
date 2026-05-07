import chromadb
import uuid

class MemoryStore:
    def __init__(self, user_id: str):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(name=f"user_{user_id}_memories")

    def save(self, message: str, metadata: dict = None):
        self.collection.add(
            documents=[message],
            metadatas=[metadata] if metadata else [{"source":"no_source"}],
            ids=[str(uuid.uuid4())]
        )

    def retrieve(self, query: str, n_results: int = 3):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        docs = results.get("documents", [])[0]
        return "\n".join(docs) if docs else ""

    def retrieve_all(self):
        results = self.collection.get()
        docs = results.get("documents", [])
        return docs


if __name__ == "__main__":
    memory = MemoryStore("41")
    # memory.save("Hello, my name is oneTwoThree and my age is 35")
    print(memory.retrieve("what's my age ?"))
    # print(memory.retrieve_all())

