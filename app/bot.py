import os
import chromadb
from anthropic import Anthropic
from dotenv import load_dotenv
from app.documents import DOCUMENTS

load_dotenv()
print("Key loaded:", os.getenv("ANTHROPIC_API_KEY")[:15] if os.getenv("ANTHROPIC_API_KEY") else "NOT FOUND")

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Chroma's default embedding function (all-MiniLM) runs locally, no extra API needed
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="knowledge_base")


def index_documents():
    """Load documents into the vector store. Call this once at startup."""
    collection.upsert(
        ids=[doc["id"] for doc in DOCUMENTS],
        documents=[doc["text"] for doc in DOCUMENTS],
    )


def retrieve_context(question: str, n_results: int = 2, max_distance: float = 1.0) -> list[str]:
    results = collection.query(query_texts=[question], n_results=n_results)
    docs = results["documents"][0]
    distances = results["distances"][0]
    return [doc for doc, dist in zip(docs, distances) if dist < max_distance]


def ask(question: str, temperature: float = 1.0) -> str:
    """Answer a question using retrieved context, via the Claude API."""
    context_chunks = retrieve_context(question)
    context = "\n\n".join(context_chunks)

    system_prompt = (
        "You are a support assistant for CloudSync Pro. Answer the user's "
        "question using ONLY the context provided below. If the answer "
        "isn't in the context, say you don't have that information — do "
        "not make anything up. Do not describe general features "
        "as a way of indirectly answering an unrelated question.\n\n"
        f"Context:\n{context}"
    )

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": question}],
    )

    return response.content[0].text