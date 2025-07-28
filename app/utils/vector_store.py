"""
In‑memory vector store for embedding and retrieving relevant code snippets.

This module provides a simple alternative to a full‑featured vector database like
Chroma. It uses scikit‑learn's TF-IDF implementation to embed file contents
into a vector space and cosine similarity to retrieve the most relevant
snippets given a textual query. The store lives entirely in process and is
rebuilt on each call to `embed_files`.

If `chromadb` is available in the environment, you could substitute this
implementation with an actual Chroma client. For the purposes of this proof‑
of‑concept, TF-IDF embeddings suffice.
"""

from typing import List, Dict, Any

import numpy as np  # type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
from sklearn.metrics.pairwise import cosine_similarity  # type: ignore

# Global variables for the vector store
_vectorizer: TfidfVectorizer | None = None
_matrix: Any = None  # Will hold the TF-IDF matrix
_docs: List[Dict[str, Any]] = []  # Each entry holds {'filename': str, 'content': str}


def embed_files(decoded_files: List[Dict[str, Any]]) -> None:
    """Embed a list of decoded file contents into the vector store.

    Each call replaces any previously stored vectors. The decoded_files list
    should contain dictionaries with keys 'filename' and 'content'. Only
    non‑empty content entries are embedded. The embeddings are stored
    globally for subsequent queries.
    """
    global _vectorizer, _matrix, _docs
    texts: List[str] = []
    docs: List[Dict[str, Any]] = []
    for item in decoded_files:
        text = item.get('content', '')
        if text:
            texts.append(text)
            docs.append(item)
    if not texts:
        # Nothing to embed
        _vectorizer = None
        _matrix = None
        _docs = []
        return
    # Create a new vectorizer and fit to texts
    _vectorizer = TfidfVectorizer(stop_words='english')
    _matrix = _vectorizer.fit_transform(texts)
    _docs = docs


def query_snippets(query: str, k: int = 5) -> List[str]:
    """Return up to `k` snippets whose content is most similar to the query.

    The returned snippets are simple string excerpts taken from the start of
    each document to maintain brevity (up to 1000 characters). If no
    embeddings have been created, an empty list is returned.
    """
    global _vectorizer, _matrix, _docs
    if _vectorizer is None or _matrix is None or not _docs:
        return []
    # Transform the query into the same vector space
    try:
        query_vec = _vectorizer.transform([query])
    except Exception:
        return []
    # Compute cosine similarity between query and all docs
    try:
        similarities = cosine_similarity(query_vec, _matrix)[0]
    except Exception:
        return []
    # Get indices of top k similar documents
    top_indices = np.argsort(similarities)[::-1][:k]
    snippets: List[str] = []
    for idx in top_indices:
        if idx >= len(_docs):
            continue
        doc = _docs[int(idx)]
        text = doc.get('content', '')
        # Take up to first 1000 characters of the document to avoid large prompts
        snippet = text[:1000]
        snippets.append(snippet)
    return snippets