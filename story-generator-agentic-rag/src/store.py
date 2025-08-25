import hashlib
from typing import List, Dict, Callable

import chromadb
from chromadb.utils import embedding_functions

class _ExternalEmbedder(embedding_functions.EmbeddingFunction):
    def __init__(self, fn: Callable[[List[str]], List[List[float]]]):
        self.fn = fn
    def __call__(self, inputs: List[str]) -> List[List[float]]:
        return self.fn(inputs)

class VectorStore:
    def __init__(self, persist_path: str, embedder: Callable[[List[str]], List[List[float]]]):
        self.client = chromadb.PersistentClient(path=persist_path or "./chroma_data")
        self.embedder = embedder
        self._collections = {}

    def _get(self, name: str):
        if name in self._collections:
            return self._collections[name]
        col = self.client.get_or_create_collection(name=name, embedding_function=_ExternalEmbedder(self.embedder))
        self._collections[name] = col
        return col

    def list_collections(self) -> List[str]:
        return [c.name for c in self.client.list_collections()]

    def _make_ids(self, source_key: str, texts: List[str]) -> List[str]:
        ids = []
        for t in texts:
            h = hashlib.sha256(t.encode("utf-8", errors="ignore")).hexdigest()[:24]
            ids.append(f"{source_key}:{h}")
        return ids

    def upsert(self, collection: str, source_key: str, chunks: List[str], metadatas: List[dict]) -> int:
        if not chunks:
            return 0
        ids = self._make_ids(source_key, chunks)
        embs = self.embedder(chunks)
        coll = self._get(collection)
        coll.upsert(ids=ids, documents=chunks, metadatas=metadatas, embeddings=embs)
        return len(chunks)

    def query(self, collection: str, query: str, k: int = 5) -> List[Dict]:
        q_emb = self.embedder([query])[0]
        coll = self._get(collection)
        res = coll.query(query_embeddings=[q_emb], n_results=k, include=["documents","metadatas","distances"])
        docs = []
        for d, m, s in zip(res.get("documents", [[]])[0], res.get("metadatas", [[]])[0], res.get("distances", [[]])[0]):
            docs.append({"text": d, "meta": m, "score": float(s)})
        return docs
