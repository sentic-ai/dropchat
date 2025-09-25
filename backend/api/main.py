#!/usr/bin/env python3
"""
FastAPI backend for PDF RAG system.
Multi-user support with hybrid document storage approach.
"""

import os
import hashlib
import uuid
from typing import List, Optional
from collections import defaultdict, Counter
from datetime import datetime, timedelta

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

from api.models.schemas import CreateProjectRequest, CreateProjectResponse, ProjectInfo, ChatRequest, ChatResponse
from api.services.rag_service import MultiUserRAGService
from agent.rag_agent import run_agent

load_dotenv()

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="PDF RAG API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# In-memory storage for project-based rate limiting
project_request_counts = Counter()  # project_id -> request_count
PROJECT_REQUEST_LIMIT = 20

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_service = MultiUserRAGService()

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "PDF RAG API is running", "status": "healthy"}

@app.post("/create", response_model=CreateProjectResponse)
@limiter.limit("5/minute")
async def create_project(
    request: Request,
    files: List[UploadFile] = File(...),
    project_name: str = "My Documents",
    description: Optional[str] = None
):
    """
    Create a new RAG project with uploaded PDF files.

    Limits:
    - Maximum 3 PDF files per request
    - Maximum 15MB per file
    - Rate limit: 5 requests per minute per IP

    This endpoint:
    1. Generates a unique user hash
    2. Creates a project structure
    3. Processes all uploaded PDFs
    4. Creates embeddings and FAISS index
    5. Stores everything for future queries
    """

    # Validate files
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    if len(files) > 3:
        raise HTTPException(
            status_code=400,
            detail="Maximum 3 PDF files allowed per request"
        )

    MAX_FILE_SIZE = 15 * 1024 * 1024  # 15MB in bytes

    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail=f"Only PDF files are allowed. Got: {file.filename}"
            )

        # Check file size
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} is too large. Maximum size is 15MB."
            )

        # Reset file pointer for later processing
        await file.seek(0)

    try:
        user_hash = generate_user_hash()
        project_id = str(uuid.uuid4())

        result = await rag_service.create_project(
            user_hash=user_hash,
            project_id=project_id,
            project_name=project_name,
            description=description,
            files=files
        )

        return CreateProjectResponse(
            user_hash=user_hash,
            project_id=project_id,
            project_name=project_name,
            message=f"Successfully created project with {result['document_count']} documents and {result['total_chunks']} chunks"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")

@app.get("/projects/{user_hash}")
async def list_projects(user_hash: str):
    """List all projects for a user."""
    try:
        projects = await rag_service.list_user_projects(user_hash)
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing projects: {str(e)}")

@app.get("/projects/{user_hash}/{project_id}")
async def get_project_info(user_hash: str, project_id: str):
    """Get detailed information about a specific project."""
    try:
        project_info = await rag_service.get_project_info(user_hash, project_id)
        return project_info
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Project not found: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat_with_documents(_: Request, request: ChatRequest):
    """
    Chat with documents using the RAG agent.

    Limits:
    - Rate limit: 20 requests per minute per IP
    - Project limit: 20 total requests per project (lifetime)

    This endpoint:
    1. Validates the project exists
    2. Checks project-based rate limits
    3. Runs the LangGraph agent with the query
    4. Returns the AI-generated response with sources
    """

    # Check project-based rate limit (max 20 requests total per project)
    project_key = f"{request.user_hash}_{request.project_id}"
    if project_request_counts[project_key] >= PROJECT_REQUEST_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Project rate limit exceeded. Maximum {PROJECT_REQUEST_LIMIT} requests per project."
        )

    # Validate project exists
    try:
        await rag_service.get_project_info(request.user_hash, request.project_id)
    except Exception:
        raise HTTPException(
            status_code=404,
            detail=f"Project not found: {request.user_hash}/{request.project_id}"
        )

    # Increment project request count
    project_request_counts[project_key] += 1

    session_id = str(uuid.uuid4())

    try:
        # Run the RAG agent
        result = run_agent(
            user_hash=request.user_hash,
            project_id=request.project_id,
            query=request.query,
            session_id=session_id
        )

        return ChatResponse(
            answer=result.get("answer", ""),
            sources=result.get("sources", []),
            processing_steps=result.get("processing_steps", []),
            error=result.get("error")
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )

def generate_user_hash() -> str:
    """Generate a unique user hash."""
    # For now, use UUID + timestamp for uniqueness
    unique_data = f"{uuid.uuid4()}{os.urandom(8).hex()}"
    return hashlib.sha256(unique_data.encode()).hexdigest()[:16]

def main():
    """Main function for running the server."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()