"""
Pydantic models for API requests and responses.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class CreateProjectRequest(BaseModel):
    project_name: str = Field(default="My Documents", description="Name of the project")
    description: Optional[str] = Field(default=None, description="Optional project description")

class CreateProjectResponse(BaseModel):
    user_hash: str = Field(description="Unique user identifier")
    project_id: str = Field(description="Unique project identifier")
    project_name: str = Field(description="Project name")
    message: str = Field(description="Success message with details")

class ProjectInfo(BaseModel):
    project_id: str = Field(description="Unique project identifier")
    project_name: str = Field(description="Project name")
    description: Optional[str] = Field(description="Project description")
    document_count: int = Field(description="Number of documents in project")
    total_chunks: int = Field(description="Total number of text chunks")
    created_at: str = Field(description="Creation timestamp")
    document_names: List[str] = Field(description="List of document filenames")

class DocumentMetadata(BaseModel):
    doc_id: str = Field(description="Document identifier")
    filename: str = Field(description="Original filename")
    page_count: int = Field(description="Number of pages")
    chunk_count: int = Field(description="Number of chunks from this document")
    upload_time: str = Field(description="Upload timestamp")

class ChatRequest(BaseModel):
    user_hash: str = Field(description="User identifier from project creation")
    project_id: str = Field(description="Project identifier")
    query: str = Field(description="User's question about the documents")

class ChatResponse(BaseModel):
    answer: str = Field(description="AI-generated answer")
    sources: List[str] = Field(description="Source document filenames referenced")
    processing_steps: List[str] = Field(description="Steps performed by the agent")
    error: Optional[str] = Field(description="Error message if something went wrong")