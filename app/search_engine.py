import os
import json
from typing import List, Tuple, Union
from sentence_transformers import SentenceTransformer, util
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class SearchEngine:

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.docs = []
        self.embeddings = []

    def load_documents_from_json(self, json_path: str):
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            self.docs = json.load(f)
        texts = [doc['text'] for doc in self.docs if 'text' in doc]
        self.embeddings = self.model.encode(texts, convert_to_tensor=True)

    def prepare_documents(self, texts: List[str]):
        self.docs = [{"text": t} for t in texts]
        self.embeddings = self.model.encode(texts, convert_to_tensor=True)

    def search(self, query: str, top_k: int = 5) -> List[dict]:
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        hits = util.semantic_search(query_embedding, self.embeddings, top_k=top_k)[0]

        results = []
        for hit in hits:
            idx = hit['corpus_id']
            score = hit['score']
            doc_text = self.docs[idx].get('text', '')
            results.append({
                "text": doc_text,
                "score": float(score)
            })
        return results
