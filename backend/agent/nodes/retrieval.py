"""
Retrieval node - loads FAISS index and searches for relevant documents.
"""

import os
import pickle
from pathlib import Path
from typing import List, Tuple

import numpy as np
import faiss
from openai import OpenAI

from agent.state import AgentState


def retrieve_documents(state: AgentState) -> AgentState:
    """
    Retrieve relevant documents from FAISS index.

    Args:
        state: Current agent state

    Returns:
        Updated state with retrieved documents
    """

    try:
        # Load FAISS index and metadata for the project
        project_dir = Path("data") / state.user_hash / state.project_id
        index_path = project_dir / "embeddings" / "index.faiss"
        metadata_path = project_dir / "embeddings" / "metadata.pkl"

        # Check if project exists
        if not index_path.exists() or not metadata_path.exists():
            state.retrieved_documents = []
            state.relevance_scores = []
            state.processing_steps.append("no_index_found")
            return state

        # Load FAISS index
        index = faiss.read_index(str(index_path))

        with open(metadata_path, "rb") as f:
            metadata = pickle.load(f)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        client = OpenAI(api_key=api_key)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[state.query]
        )

        query_embedding = np.array([response.data[0].embedding], dtype=np.float32)
        faiss.normalize_L2(query_embedding)

        max_docs = min(state.max_documents, len(metadata))
        scores, indices = index.search(query_embedding, max_docs)

        relevance_threshold = 0.1
        retrieved_documents = []
        relevance_scores = []

        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and score >= relevance_threshold:
                doc_metadata = metadata[idx]
                retrieved_documents.append({
                    "text": doc_metadata["text"],
                    "doc_id": doc_metadata["doc_id"],
                    "filename": doc_metadata["filename"],
                    "chunk_index": doc_metadata["chunk_index"],
                    "chunk_id": doc_metadata["chunk_id"]
                })
                relevance_scores.append(float(score))

        state.retrieved_documents = retrieved_documents
        state.relevance_scores = relevance_scores
        state.processing_steps.append("retrieved_documents")

    except Exception as e:
        state.error_message = f"Error during retrieval: {str(e)}"
        state.retrieved_documents = []
        state.relevance_scores = []
        state.processing_steps.append("retrieval_error")

    return state