"""
Main RAG Agent implementation using LangGraph.
"""
from typing import Dict, Any

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agent.state import AgentState
from agent.nodes.retrieval import retrieve_documents
from agent.nodes.generate import generate_answer
from agent.nodes.router import route_query


def create_rag_agent() -> StateGraph:
    """Create the RAG agent graph."""

    workflow = StateGraph(AgentState)

    workflow.add_node("route_query", route_query)
    workflow.add_node("retrieve_documents", retrieve_documents)
    workflow.add_node("generate_answer", generate_answer)

    workflow.add_edge(START, "route_query")
    workflow.add_edge("route_query", "retrieve_documents")
    workflow.add_edge("retrieve_documents", "generate_answer")

    workflow.add_edge("generate_answer", END)

    # Compile the graph with memory
    # memory = MemorySaver()
    return workflow.compile()

graph = create_rag_agent()


def run_agent(
    user_hash: str,
    project_id: str,
    query: str,
    session_id: str = None,
    conversation_history: list = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Run the RAG agent with the given query.

    Args:
        user_hash: User identifier
        project_id: Project identifier
        query: User query
        session_id: Visitor session ID for individual conversations
        conversation_history: Previous conversation messages
        **kwargs: Additional configuration

    Returns:
        Dict containing the agent's response
    """

    initial_state = AgentState(
        user_hash=user_hash,
        project_id=project_id,
        query=query,
        conversation_history=conversation_history or [],
        **kwargs
    )

    # Create individual thread per visitor session
    if session_id:
        thread_id = f"{user_hash}_{project_id}_{session_id}"
    else:
        # Fallback to shared thread if no session_id provided
        thread_id = f"{user_hash}_{project_id}"

    config = {"configurable": {"thread_id": thread_id}}

    try:
        result = graph.invoke(initial_state.model_dump(), config=config)

        return {
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "retrieved_documents": result.get("retrieved_documents", []),
            "processing_steps": result.get("processing_steps", []),
            "error": result.get("error_message"),
        }

    except Exception as e:
        return {
            "answer": f"Sorry, I encountered an error: {str(e)}",
            "sources": [],
            "retrieved_documents": [],
            "processing_steps": ["error_occurred"],
            "error": str(e),
        }


if __name__ == "__main__":
    result = run_agent(
        user_hash="test_user",
        project_id="test_project",
        query="What is this document about?"
    )
    print(result)