"""
Agent state definition for the RAG agent.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    """State object for the RAG agent."""

    user_hash: str = Field(description="User identifier")
    project_id: str = Field(description="Project identifier")
    query: str = Field(description="User query")

    conversation_history: List[Dict[str, str]] = Field(default_factory=list, description="Previous messages")

    retrieved_documents: List[Dict[str, Any]] = Field(default_factory=list, description="Retrieved document chunks")
    relevance_scores: List[float] = Field(default_factory=list, description="Similarity scores")

    reformulated_query: Optional[str] = Field(default=None, description="Reformulated query for better retrieval")
    search_type: str = Field(default="semantic", description="Type of search to perform")

    context: str = Field(default="", description="Combined context for generation")
    answer: str = Field(default="", description="Generated answer")
    sources: List[str] = Field(default_factory=list, description="Source documents referenced")

    processing_steps: List[str] = Field(default_factory=list, description="Steps performed by agent")
    error_message: Optional[str] = Field(default=None, description="Error message if something goes wrong")

    max_documents: int = Field(default=5, description="Maximum documents to retrieve")
    temperature: float = Field(default=0.3, description="Generation temperature")