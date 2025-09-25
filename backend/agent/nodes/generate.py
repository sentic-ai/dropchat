"""
Generation node - generates final answer using OpenAI.
"""

import os
from openai import OpenAI

from agent.state import AgentState


def generate_answer(state: AgentState) -> AgentState:
    """
    Generate final answer based on context or direct response.

    Args:
        state: Current agent state

    Returns:
        Updated state with generated answer
    """

    try:
        if state.retrieved_documents:
            context = " ".join([doc["text"] for doc in state.retrieved_documents])
            state.context = context

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")

            client = OpenAI(api_key=api_key)

            history_context = ""
            if state.conversation_history:
                history_context = "\n\nPrevious conversation:\n"
                for msg in state.conversation_history[-3:]:  # Last 3 messages for context
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    history_context += f"{role}: {content}\n"

            system_prompt = """You are a helpful AI assistant that answers questions based on provided documents.
Use the document context to provide accurate, detailed answers. If the answer isn't fully covered in the documents,
say so clearly. Always cite which documents you're referencing when possible."""

            user_prompt = f"""Based on the following documents, please answer this question: {state.query}

Document context:
{context}
{history_context}

Please provide a comprehensive answer based on the document content."""

            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000
            )

            state.answer = response.choices[0].message.content.strip()
            state.sources = list(set([doc["filename"] for doc in state.retrieved_documents]))

        else:
            state.answer = "I couldn't find any relevant information in your documents to answer this question. Please try rephrasing your query or make sure your documents contain information about this topic."
            state.sources = []

        state.processing_steps.append("generated_answer")

    except Exception as e:
        state.error_message = f"Error during generation: {str(e)}"
        state.answer = f"Sorry, I encountered an error while generating the answer: {str(e)}"
        state.sources = []
        state.processing_steps.append("generation_error")

    return state