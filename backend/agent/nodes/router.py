"""
Router node - decides how to process the query.
"""

from agent.state import AgentState


def route_query(state: AgentState) -> AgentState:
    """
    Route the query - for RAG agent, ALWAYS search documents.

    Args:
        state: Current agent state

    Returns:
        Updated state with search_type set to semantic
    """


    state.search_type = "semantic"
    state.processing_steps.append("routed_to_document_search")

    return state