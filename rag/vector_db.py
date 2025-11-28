import faiss
import numpy as np

class VectorDB:
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)
        self.text_chunks = []
        self.embeddings = []

    def add(self, embeddings, texts):
        self.index.add(np.array(embeddings).astype('float32'))
        self.text_chunks.extend(texts)
        self.embeddings.extend(embeddings)

    def search(self, query_embedding, top_k=5):
        D, I = self.index.search(np.array([query_embedding]).astype('float32'), top_k)
        results = [(self.text_chunks[i], D[0][idx]) for idx, i in enumerate(I[0]) if i < len(self.text_chunks)]
        return results
