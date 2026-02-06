from rag.embedder import embed_texts, embed_query
from rag.vector_store import VectorStore
import os


def load_documents():
    docs = []
    if not os.path.isdir("rag/documents"):
        return docs
    for file in os.listdir("rag/documents"):
        path = os.path.join("rag/documents", file)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                docs.append(f.read())
    return docs


def _build_vector_store():
    docs = load_documents()
    if not docs:
        return None, []
    doc_embeddings = embed_texts(docs)
    vector_store = VectorStore(dim=doc_embeddings.shape[1])
    vector_store.add(doc_embeddings, docs)
    return vector_store, docs


_vector_store, _docs = _build_vector_store()


def retrieve_context(query, k=3):
    if _vector_store is None:
        return []
    q_emb = embed_query(query)
    return _vector_store.search(q_emb, k)
