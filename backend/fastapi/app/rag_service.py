"""
Service RAG pour assistant IA.
Architecture: ChromaDB + LangChain + Ollama/Llama 3
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import hashlib
from datetime import datetime

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_ollama import ChatOllama
    from langchain_core.prompts import PromptTemplate
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from .config import PROJECT_ROOT

CHROMA_PERSIST_DIR = PROJECT_ROOT / "chroma_db"
CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_MODEL = "llama3.2:3b"
OLLAMA_BASE_URL = "http://localhost:11434"

SYSTEM_PROMPT = "Tu es un assistant IA specialise dans les inspections scolaires."
CUSTOM_PROMPT_TEMPLATE = "{system_prompt}\n\nContexte: {context}\n\nQuestion: {question}\n\nReponse:"


class RagService:
    def __init__(self) -> None:
        self.embeddings = None
        self.vector_store = None
        self.llm = None
        self.qa_chain = None
        self.retriever = None
        self.initialized = False
        self.init_error: Optional[str] = None
        self._initialize()

    def _missing_packages(self) -> str:
        missing = []
        if not CHROMADB_AVAILABLE:
            missing.append("chromadb")
        if not EMBEDDINGS_AVAILABLE:
            missing.append("sentence-transformers")
        if not LANGCHAIN_AVAILABLE:
            missing.append("langchain")
        return ", ".join(missing) if missing else "aucun"

    def _ollama_up(self) -> bool:
        try:
            import urllib.request
            req = urllib.request.urlopen(OLLAMA_BASE_URL, timeout=2)
            return req.status == 200
        except Exception:
            return False

    def _connect_llm(self) -> None:
        if not self._ollama_up():
            print(f"[RAG] Ollama indisponible sur {OLLAMA_BASE_URL} -> mode retrieval-only")
            self.llm = None
            return
        try:
            self.llm = ChatOllama(
                model=OLLAMA_MODEL,
                base_url=OLLAMA_BASE_URL,
                temperature=0.3,
                # Plafonne la longueur de la reponse pour accelerer l'inference CPU
                num_predict=256,
            )
            print("[RAG] Ollama connecte")
        except Exception as e:
            print(f"[RAG] Ollama erreur (mode retrieval-only): {e}")
            self.llm = None

    def _build_qa_chain(self) -> None:
        prompt = PromptTemplate(
            template=CUSTOM_PROMPT_TEMPLATE,
            input_variables=["context", "question"],
            partial_variables={"system_prompt": SYSTEM_PROMPT},
        )
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
        self.retriever = retriever

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        self.qa_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        print("[RAG] Chain prete")

    def _initialize(self) -> bool:
        """Initialise le service RAG. Renvoie True si pret, False sinon.
        Peut etre re-appelle pour reessayer apres un echec (ex: Ollama demarre
        apres le backend, ou modele a telecharger)."""
        if self.initialized and self.vector_store is not None:
            return True
        if not all([CHROMADB_AVAILABLE, EMBEDDINGS_AVAILABLE, LANGCHAIN_AVAILABLE]):
            self.init_error = (
                "Packages RAG manquants (" + self._missing_packages() + "). "
                "Installez-les avec: pip install chromadb langchain-chroma "
                "langchain-huggingface langchain-ollama langchain-text-splitters "
                "sentence-transformers pypdf"
            )
            print("[RAG] " + self.init_error)
            return False
        try:
            print(f"[RAG] Embeddings: {EMBEDDING_MODEL}")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                model_kwargs={"device": "cpu"},
            )
            print(f"[RAG] ChromaDB: {CHROMA_PERSIST_DIR}")
            self.vector_store = Chroma(
                collection_name="inspection_docs",
                embedding_function=self.embeddings,
                persist_directory=str(CHROMA_PERSIST_DIR),
            )
            # LLM optionnel : si Ollama est indisponible, on reste en mode
            # retrieval-only (pas d'erreur bloquante).
            self._connect_llm()
            if self.llm:
                self._build_qa_chain()
            self.initialized = True
            self.init_error = None
            print("[RAG] Service initialise")
            return True
        except Exception as e:
            self.init_error = str(e)
            self.initialized = False
            self.vector_store = None
            print(f"[RAG] Erreur d'initialisation: {e}")
            import traceback
            traceback.print_exc()
            return False

    def ensure_initialized(self) -> bool:
        """S'assure que le vector store est pret, en reessayant l'init au besoin.
        Reconnecte aussi Ollama a la volee s'il etait indisponible au depart."""
        if self.vector_store is not None:
            if self.llm is None and self._ollama_up():
                self._connect_llm()
                if self.llm and self.qa_chain is None:
                    self._build_qa_chain()
            return True
        return self._initialize()

    def ingest_pdf(self, file_path: Path, document_id: int, title: str) -> Dict[str, Any]:
        if not self.ensure_initialized():
            reason = self.init_error or "cause inconnue"
            return {"status": "error", "message": f"RAG non initialise: {reason}"}
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(file_path))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            if not text.strip():
                return {"status": "error", "message": "PDF vide"}
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=300,
                chunk_overlap=50,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
            chunks = text_splitter.split_text(text)
            base_metadata = {
                "document_id": document_id,
                "title": title,
                "source": file_path.name,
                "indexed_at": datetime.utcnow().isoformat(),
            }
            ids, metadatas, documents = [], [], []
            for i, chunk in enumerate(chunks):
                chunk_id = hashlib.md5(f"{document_id}_{i}_{chunk[:50]}".encode()).hexdigest()
                ids.append(chunk_id)
                metadatas.append({**base_metadata, "chunk_index": i})
                documents.append(chunk)
            self.vector_store.add_texts(texts=documents, metadatas=metadatas, ids=ids)
            return {
                "status": "success",
                "chunks_indexed": len(chunks),
                "document_id": document_id,
                "title": title,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


    def ask(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        if not self.ensure_initialized():
            reason = self.init_error or "cause inconnue"
            return {"answer": f"RAG non initialise: {reason}", "sources": [], "confidence": 0.0}
        try:
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": top_k},
            )
            docs = retriever.invoke(question)
            if not docs:
                return {"answer": "Aucun document pertinent trouve.", "sources": [], "confidence": 0.0}

            sources = [
                {
                    "title": doc.metadata.get("title", "Unknown"),
                    "document_id": doc.metadata.get("document_id"),
                    "excerpt": doc.page_content[:200] + "...",
                }
                for doc in docs
            ]

            if self.llm and self.qa_chain:
                try:
                    answer = self.qa_chain.invoke(question)
                    return {"answer": answer, "sources": sources, "confidence": 0.8, "mode": "RAG (Ollama + ChromaDB)"}
                except Exception as e:
                    # Repli sur le mode retrieval-only si le LLM echoue a generer
                    print(f"[RAG] Echec generation LLM, repli retrieval-only: {e}")
                    combined_context = "\n\n---\n\n".join(doc.page_content for doc in docs[:3])
                    return {
                        "answer": f"[Mode retrieval-only - LLM indisponible]\n\n{combined_context}",
                        "sources": sources,
                        "confidence": 0.7,
                        "mode": "Retrieval only",
                    }
            else:
                excerpts = [doc.page_content for doc in docs]
                combined_context = "\n\n---\n\n".join(excerpts[:3])
                return {"answer": f"[Mode retrieval-only]\n\n{combined_context}", "sources": sources, "confidence": 0.7, "mode": "Retrieval only"}
        except Exception as e:
            return {"answer": f"Erreur: {str(e)}", "sources": [], "confidence": 0.0}

    def ask_stream(self, question: str, top_k: int = 3):
        """Version streaming de ask(). Yield des dictionnaires (NDJSON) :
           {"type": "meta", "confidence":..., "mode":..., "sources":[...], "question":...}
           {"type": "token", "text": "..."}
           {"type": "done"}
           {"type": "error", "message": "..."}
        """
        if not self.ensure_initialized():
            yield {"type": "error", "message": f"RAG non initialise: {self.init_error or 'cause inconnue'}"}
            return
        try:
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": top_k},
            )
            docs = retriever.invoke(question)
            if not docs:
                yield {"type": "meta", "confidence": 0.0, "mode": "Retrieval only",
                       "sources": [], "question": question}
                yield {"type": "token", "text": "Aucun document pertinent trouve."}
                yield {"type": "done"}
                return

            sources = [
                {
                    "title": doc.metadata.get("title", "Unknown"),
                    "document_id": doc.metadata.get("document_id"),
                    "excerpt": doc.page_content[:200] + "...",
                }
                for doc in docs
            ]

            if self.llm and self.qa_chain:
                yield {"type": "meta", "confidence": 0.8, "mode": "RAG (Ollama + ChromaDB)",
                       "sources": sources, "question": question}
                try:
                    for chunk in self.qa_chain.stream(question):
                        if chunk:
                            yield {"type": "token", "text": chunk}
                    yield {"type": "done"}
                    return
                except Exception as e:
                    print(f"[RAG] Echec streaming LLM, repli retrieval-only: {e}")
                    combined_context = "\n\n---\n\n".join(doc.page_content for doc in docs[:3])
                    yield {"type": "token", "text": f"[Mode retrieval-only - LLM indisponible]\n\n{combined_context}"}
                    yield {"type": "done"}
                    return
            else:
                excerpts = [doc.page_content for doc in docs]
                combined_context = "\n\n---\n\n".join(excerpts[:3])
                yield {"type": "meta", "confidence": 0.7, "mode": "Retrieval only",
                       "sources": sources, "question": question}
                yield {"type": "token", "text": f"[Mode retrieval-only]\n\n{combined_context}"}
                yield {"type": "done"}
                return
        except Exception as e:
            yield {"type": "error", "message": f"Erreur: {str(e)}"}

    def delete_document(self, document_id: int) -> Dict[str, Any]:
        if not self.ensure_initialized():
            reason = self.init_error or "cause inconnue"
            return {"status": "error", "message": f"RAG non initialise: {reason}"}
        try:
            results = self.vector_store.get(
                where={"document_id": document_id},
                include=["metadatas", "documents"],
            )
            if not results["ids"]:
                return {"status": "success", "deleted": 0}
            self.vector_store.delete(ids=results["ids"])
            return {"status": "success", "deleted": len(results["ids"]), "document_id": document_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_stats(self) -> Dict[str, Any]:
        if not self.ensure_initialized():
            return {"status": "unavailable", "error": self.init_error or "RAG non initialise"}
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
            return {"status": "error", "message": str(e)}


rag_service = RagService()



