# rag.py
import faiss
import numpy as np
import tiktoken
from utils import extract_text_from_pdf
from groq_llm import groq_chat

# Tokenizer
enc = tiktoken.encoding_for_model("gpt-3.5-turbo")

# Very simple chunking strategy
def chunk_text(text: str, max_tokens=200) -> list[str]:
    tokens = enc.encode(text)
    chunks = [tokens[i:i+max_tokens] for i in range(0, len(tokens), max_tokens)]
    return [enc.decode(chunk) for chunk in chunks]

# Placeholder embedder

def embed(text: str) -> np.ndarray:
    return np.random.rand(384).astype("float32")  # Replace with real embedder

def build_faiss_index(chunks: list[str]):
    vectors = np.array([embed(chunk) for chunk in chunks])
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    return index, vectors

def summarize_with_rag(file_path: str) -> str:
    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)
    index, _ = build_faiss_index(chunks)

    query = "Summarize this document"
    query_vec = embed(query).reshape(1, -1)
    _, I = index.search(query_vec, k=3)
    top_chunks = [chunks[i] for i in I[0]]

    prompt = f"Summarize the following:\n\n{chr(10).join(top_chunks)}"
    return groq_chat(prompt)

def answer_question_with_rag(file_path: str, question: str) -> str:
    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)
    index, _ = build_faiss_index(chunks)

    query_vec = embed(question).reshape(1, -1)
    _, I = index.search(query_vec, k=3)
    top_chunks = [chunks[i] for i in I[0]]

    prompt = f"Use the context to answer:\n\nContext:\n{chr(10).join(top_chunks)}\n\nQuestion: {question}"
    return groq_chat(prompt)
