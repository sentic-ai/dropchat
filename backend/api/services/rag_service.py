"""
Multi-user RAG service for managing PDF documents and embeddings.
Implements hybrid approach: one FAISS index per project with metadata tracking.
"""

import os
import json
import pickle
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple
from pathlib import Path

import numpy as np
import pymupdf
import faiss
from openai import OpenAI
from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter

from api.models.schemas import ProjectInfo, DocumentMetadata

class MultiUserRAGService:
    def __init__(self, data_dir: str = "data"):
        """Initialize the multi-user RAG service."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.client = OpenAI(api_key=api_key)
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimension = 1536

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    async def create_project(
        self,
        user_hash: str,
        project_id: str,
        project_name: str,
        description: str = None,
        files: List[UploadFile] = None
    ) -> Dict[str, Any]:
        """Create a new RAG project with uploaded PDF files."""

        user_dir = self.data_dir / user_hash
        project_dir = user_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)

        (project_dir / "documents").mkdir(exist_ok=True)
        (project_dir / "embeddings").mkdir(exist_ok=True)

        all_chunks = []
        all_metadata = []
        document_metadata = []

        for file in files:
            doc_id = str(uuid.uuid4())
            file_path = project_dir / "documents" / f"{doc_id}_{file.filename}"

            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)

            text = self._extract_text_from_pdf(str(file_path))
            chunks = self._chunk_text(text)

            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    "doc_id": doc_id,
                    "filename": file.filename,
                    "chunk_id": f"{doc_id}_chunk_{i}",
                    "chunk_index": i,
                    "text": chunk
                }
                all_chunks.append(chunk)
                all_metadata.append(chunk_metadata)

            doc_metadata = DocumentMetadata(
                doc_id=doc_id,
                filename=file.filename,
                page_count=self._get_page_count(str(file_path)),
                chunk_count=len(chunks),
                upload_time=datetime.now().isoformat()
            )
            document_metadata.append(doc_metadata)

        if all_chunks:
            embeddings = self._create_embeddings(all_chunks)

            index = faiss.IndexFlatIP(self.embedding_dimension)
            faiss.normalize_L2(embeddings)
            index.add(embeddings)

            faiss.write_index(index, str(project_dir / "embeddings" / "index.faiss"))

            with open(project_dir / "embeddings" / "metadata.pkl", "wb") as f:
                pickle.dump(all_metadata, f)

        project_info = {
            "project_id": project_id,
            "project_name": project_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "document_count": len(files),
            "total_chunks": len(all_chunks),
            "document_metadata": [doc.dict() for doc in document_metadata]
        }

        with open(project_dir / "project_info.json", "w") as f:
            json.dump(project_info, f, indent=2)

        return {
            "document_count": len(files),
            "total_chunks": len(all_chunks)
        }

    async def list_user_projects(self, user_hash: str) -> List[Dict[str, Any]]:
        """List all projects for a user."""
        user_dir = self.data_dir / user_hash

        if not user_dir.exists():
            return []

        projects = []
        for project_dir in user_dir.iterdir():
            if project_dir.is_dir():
                info_file = project_dir / "project_info.json"
                if info_file.exists():
                    with open(info_file, "r") as f:
                        project_info = json.load(f)
                        projects.append(project_info)

        return projects

    async def get_project_info(self, user_hash: str, project_id: str) -> ProjectInfo:
        """Get detailed information about a specific project."""
        project_dir = self.data_dir / user_hash / project_id
        info_file = project_dir / "project_info.json"

        if not info_file.exists():
            raise FileNotFoundError(f"Project {project_id} not found")

        with open(info_file, "r") as f:
            project_data = json.load(f)

        # Extract document names
        document_names = [doc["filename"] for doc in project_data["document_metadata"]]

        return ProjectInfo(
            project_id=project_data["project_id"],
            project_name=project_data["project_name"],
            description=project_data.get("description"),
            document_count=project_data["document_count"],
            total_chunks=project_data["total_chunks"],
            created_at=project_data["created_at"],
            document_names=document_names
        )

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
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

    def _get_page_count(self, pdf_path: str) -> int:
        """Get page count from PDF."""
        try:
            doc = pymupdf.open(pdf_path)
            page_count = len(doc)
            doc.close()
            return page_count
        except Exception:
            return 0

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks using RecursiveCharacterTextSplitter."""
        import re
        text = re.sub(r'\s+', ' ', text.strip())

        chunks = self.text_splitter.split_text(text)

        # Filter out empty chunks
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

        return chunks

    def _create_embeddings(self, texts: List[str]) -> np.ndarray:
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