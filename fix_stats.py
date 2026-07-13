with open('d:\\ENSIASD\\TP S4\\Projet_StagePFA\\backend\\fastapi\\app\\rag_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = """    def get_stats(self) -> Dict[str, Any]:
        if not CHROMADB_AVAILABLE or not self.vector_store:
            return {"status": "unavailable"}
        try:
            collection = self.vector_store._collection
            count = collection.count()
            results = collection.get(include=["metadatas"])
            unique_docs = set()
            if results["metadatas"]:
                unique_docs = {meta.get("document_id") for meta in results["metadatas"] if meta}
            return {
                "status": "active",
                "total_chunks": count,
                "total_documents": len(unique_docs),
                "embedding_model": EMBEDDING_MODEL,
                "llm": OLLAMA_MODEL if self.llm else "None (retrieval-only)",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}"""

new = """    def get_stats(self) -> Dict[str, Any]:
        if not CHROMADB_AVAILABLE or not self.vector_store:
            return {"status": "unavailable"}
        try:
            # ChromaDB 1.x API: use _client and get_collection
            client = self.vector_store._client
            collection = client.get_collection(name="inspection_docs")
            count = collection.count()
            results = collection.get(include=["metadatas"])
            unique_docs = set()
            if results["metadatas"]:
                unique_docs = {meta.get("document_id") for meta in results["metadatas"] if meta}
            return {
                "status": "active",
                "total_chunks": count,
                "total_documents": len(unique_docs),
                "embedding_model": EMBEDDING_MODEL,
                "llm": OLLAMA_MODEL if self.llm else "None (retrieval-only)",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}"""

if old in content:
    content = content.replace(old, new)
    with open('d:\\ENSIASD\\TP S4\\Projet_StagePFA\\backend\\fastapi\\app\\rag_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('get_stats fixed')
else:
    print('ERROR: old pattern not found')
