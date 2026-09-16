"""
Retrieval stage of the RAG pipeline.

Chunking -> [Embeddings] -> Vector store -> Retrieval -> LLM

Note: this reference implementation uses a small pure-Python TF-IDF +
cosine similarity function instead of a downloaded neural embedding model
(or scikit-learn/numpy), so the whole pipeline runs with zero compiled
dependencies -- nothing to build from source, on any OS or Python version.
It is a drop-in swap: replace `TfidfRetriever` with a call to your
embedding provider (OpenAI, Voyage, Cohere, etc.) plus a real vector DB
(Chroma/Pinecone) for production scale.
"""
import re
import math
from collections import Counter

_WORD_RE = re.compile(r"[a-zA-Z']+")

_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "is",
    "are", "was", "were", "be", "been", "being", "this", "that", "these",
    "those", "with", "as", "by", "at", "from", "it", "its", "shall",
    "will", "may", "not", "any", "all", "such", "so", "if", "than", "then",
    "which", "who", "whom", "but", "into", "under", "over", "upon", "per",
}


def _tokenize(text: str):
    return [w.lower() for w in _WORD_RE.findall(text) if w.lower() not in _STOPWORDS and len(w) > 1]


class TfidfRetriever:
    def __init__(self, chunks):
        """chunks: list of dicts with at least a 'content' key."""
        self.chunks = chunks
        self.term_freqs = [Counter(_tokenize(c["content"])) for c in chunks]

        doc_freq = Counter()
        for tf in self.term_freqs:
            for term in tf:
                doc_freq[term] += 1

        n_docs = max(len(chunks), 1)
        self.idf = {term: math.log((n_docs + 1) / (df + 1)) + 1 for term, df in doc_freq.items()}

        self.doc_vectors = [self._to_tfidf_vector(tf) for tf in self.term_freqs]
        self.doc_norms = [self._norm(v) for v in self.doc_vectors]

    def _to_tfidf_vector(self, tf: Counter):
        return {term: count * self.idf.get(term, 0.0) for term, count in tf.items()}

    @staticmethod
    def _norm(vec: dict):
        return math.sqrt(sum(v * v for v in vec.values())) or 1e-9

    @staticmethod
    def _dot(vec_a: dict, vec_b: dict):
        # iterate over the smaller dict for speed
        if len(vec_a) > len(vec_b):
            vec_a, vec_b = vec_b, vec_a
        return sum(v * vec_b.get(term, 0.0) for term, v in vec_a.items())

    def retrieve(self, query: str, top_k: int = 4):
        if not self.chunks:
            return []

        query_tf = Counter(_tokenize(query))
        query_vec = self._to_tfidf_vector(query_tf)
        query_norm = self._norm(query_vec)

        scores = []
        for i, doc_vec in enumerate(self.doc_vectors):
            score = self._dot(query_vec, doc_vec) / (query_norm * self.doc_norms[i])
            scores.append(score)

        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        results = []
        for i in ranked[:top_k]:
            if scores[i] <= 0:
                continue
            results.append({**self.chunks[i], "relevance_score": float(scores[i])})
        return results


def build_retriever_from_db_chunks(document_chunks):
    """document_chunks: list of DocumentChunk model instances."""
    payload = [
        {
            "content": c.content,
            "section_label": c.section_label,
            "chunk_index": c.chunk_index,
        }
        for c in document_chunks
    ]
    return TfidfRetriever(payload)
