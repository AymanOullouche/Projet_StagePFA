import re

FILEPATH = r"d:\ENSIASD\TP S4\Projet_StagePFA\backend\fastapi\app\rag_service.py"

with open(FILEPATH, "r", encoding="utf-8") as f:
    content = f.read()

# FIX 1: Replace qa_chain initialization (RetrievalQA -> LCEL)
new_chain_init = '''                retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
                self.retriever = retriever
                def format_docs(docs):
                    return "\\n\\n".join(doc.page_content for doc in docs)
                self.qa_chain = (
                    {"context": retriever | format_docs, "question": RunnablePassthrough()}
                    | prompt
                    | self.llm
                    | StrOutputParser()
                )'''

if "RetrievalQA.from_chain_type" in content:
    lines = content.split("\n")
    new_lines = []
    skip = False
    for line in lines:
        if "self.qa_chain = RetrievalQA.from_chain_type(" in line:
            skip = True
            new_lines.append(new_chain_init)
        elif skip:
            if line.strip() in [")", "                )"]:
                skip = False
        else:
            new_lines.append(line)
    content = "\n".join(new_lines)
    print("FIX 1: qa_chain init -> LCEL")
else:
    print("FIX 1: Already fixed or not found")

# FIX 2: Replace ask method
new_ask = '''            if self.llm and self.qa_chain:
                sources = [
                    {
                        "title": doc.metadata.get("title", "Unknown"),
                        "document_id": doc.metadata.get("document_id"),
                        "excerpt": doc.page_content[:200] + "...",
                    }
                    for doc in docs
                ]
                answer = self.qa_chain.invoke(question)
                return {"answer": answer, "sources": sources, "confidence": 0.8, "mode": "RAG (Ollama + ChromaDB)"}'''

if 'self.qa_chain.invoke({"query": question})' in content:
    lines = content.split("\n")
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped == 'if self.llm and self.qa_chain:':
            # Check if next few lines match the old pattern
            joined = "\n".join(lines[i:i+15])
            if 'self.qa_chain.invoke({"query": question})' in joined and 'return {"answer": answer' in joined:
                # This is the old pattern - skip lines until return
                new_lines.append(new_ask)
                while i < len(lines):
                    s = lines[i].strip()
                    i += 1
                    if s.startswith('return {') and '"RAG (Ollama + ChromaDB)"' in s:
                        break
                continue
        new_lines.append(line)
        i += 1
    content = "\n".join(new_lines)
    print("FIX 2: ask method updated")
else:
    print("FIX 2: Already updated or not found")

with open(FILEPATH, "w", encoding="utf-8") as f:
    f.write(content)

print("Done")
