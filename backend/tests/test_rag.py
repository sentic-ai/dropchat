#!/usr/bin/env python3
"""
Simple RAG (Retrieval-Augmented Generation) implementation
using FAISS for vector storage, OpenAI for embeddings and chat, and PyMuPDF for PDF parsing.

This script demonstrates:
1. PDF text extraction using PyMuPDF
2. Text chunking for better retrieval
3. Creating embeddings using OpenAI
4. Vector storage and search using FAISS
5. RAG pipeline for question answering
"""

import os
import re
from typing import List, Tuple
import numpy as np
import pymupdf
import faiss
from openai import OpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class SimpleRAG:
    def __init__(self, openai_api_key: str = None):
        """Initialize the RAG system."""
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key must be provided either as parameter or OPENAI_API_KEY environment variable")

        self.client = OpenAI(api_key=api_key)
        self.embedding_model = "text-embedding-3-small"
        self.chat_model = "gpt-4.1-nano"

        self.index = None
        self.documents = []
        self.embedding_dimension = 1536

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using PyMuPDF."""
        try:
            doc = pymupdf.open(pdf_path)
            text = ""

            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page_text

            doc.close()
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks using RecursiveCharacterTextSplitter."""
        if chunk_size != 1000 or overlap != 200:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=overlap,
                separators=["\n\n", "\n", ".", " ", ""]
            )

        text = re.sub(r'\s+', ' ', text.strip())

        chunks = self.text_splitter.split_text(text)

        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

        return chunks

    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for a list of texts using OpenAI."""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )

            embeddings = np.array([item.embedding for item in response.data], dtype=np.float32)
            return embeddings
        except Exception as e:
            raise Exception(f"Error creating embeddings: {str(e)}")

    def build_index(self, pdf_path: str, chunk_size: int = 1000, overlap: int = 200):
        """Build FAISS index from PDF document."""
        print(f"Processing PDF: {pdf_path}")

        text = self.extract_text_from_pdf(pdf_path)
        print(f"Extracted {len(text)} characters from PDF")

        chunks = self.chunk_text(text, chunk_size, overlap)
        print(f"Created {len(chunks)} text chunks")

        print("Creating embeddings...")
        embeddings = self.create_embeddings(chunks)

        self.index = faiss.IndexFlatIP(self.embedding_dimension)

        faiss.normalize_L2(embeddings)

        self.index.add(embeddings)

        self.documents = chunks

        print(f"Built index with {self.index.ntotal} vectors")

    def search(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        """Search for relevant documents."""
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")

        query_embedding = self.create_embeddings([query])

        faiss.normalize_L2(query_embedding)

        similarities, indices = self.index.search(query_embedding, k)

        results = []
        for i, similarity in zip(indices[0], similarities[0]):
            if i < len(self.documents):
                results.append((self.documents[i], float(similarity)))

        return results

    def generate_answer(self, query: str, context_docs: List[str]) -> str:
        """Generate answer using retrieved context."""
        context = "\n\n---\n\n".join(context_docs)

        prompt = f"""Based on the following context, please answer the question. If the answer cannot be found in the context, say so clearly.

Context:
{context}

Question: {query}

Answer:"""

        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context. Be accurate and cite the relevant parts of the context when possible."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating answer: {str(e)}"

    def ask(self, query: str, k: int = 3) -> dict:
        """Complete RAG pipeline: search and generate answer."""
        results = self.search(query, k)

        context_docs = [doc for doc, score in results]

        answer = self.generate_answer(query, context_docs)

        return {
            "query": query,
            "answer": answer,
            "sources": results,
            "num_sources": len(results)
        }


def main():
    """Demo script to test the RAG implementation."""
    print("=== Simple RAG Demo ===")

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: Please set your OPENAI_API_KEY environment variable")
        print("You can do this by running: export OPENAI_API_KEY='your-api-key-here'")
        return

    rag = SimpleRAG()

    documents_dir = os.path.join(os.path.dirname(__file__), "documents")
    pdf_files = [f for f in os.listdir(documents_dir) if f.endswith('.pdf')]
    

    if not pdf_files:
        print(f"Error: No PDF files found in {documents_dir} directory")
        return

    pdf_path = os.path.join(documents_dir, pdf_files[0])
    print(f"Using PDF: {pdf_files[0]}")

    try:
        # Build the index
        rag.build_index(pdf_path)

        # Demo queries
        demo_queries = [
            "What is this document about?",
            "What are the main topics covered?",
            "Can you summarize the key points?"
        ]

        print("\n=== Demo Questions ===")

        for query in demo_queries:
            print(f"\nQ: {query}")
            print("-" * 50)

            result = rag.ask(query)
            print(f"A: {result['answer']}")

            if result['sources']:
                print(f"\nTop sources (similarity scores):")
                for i, (doc, score) in enumerate(result['sources'][:2]):
                    print(f"{i+1}. Score: {score:.3f}")
                    print(f"   Text: {doc[:200]}...")
                    print()

        # Interactive mode
        print("\n=== Interactive Mode ===")
        print("Ask questions about the document (type 'quit' to exit):")

        while True:
            user_query = input("\nYour question: ").strip()
            if user_query.lower() in ['quit', 'exit', 'q']:
                break

            if not user_query:
                continue

            result = rag.ask(user_query)
            print(f"\nAnswer: {result['answer']}")

    except Exception as e:
        print(f"Error: {str(e)}")
        return


if __name__ == "__main__":
    main()