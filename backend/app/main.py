from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.graph.support_graph import support_graph
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Customer Support Duo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow Streamlit frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Define the structure for chat history ---
class Message(BaseModel):
    role: str
    content: str
    agent: Optional[str] = None 

# --- Request body schema ---
class QueryRequest(BaseModel):
    history: Optional[List[Message]] = Field(default=None, description="Previous chat messages")

@app.post("/ask")
async def ask_support(request: QueryRequest):
    """
    Handles the user's query and passes conversation context to the support graph.
    """
    # Prepare full conversational context for the LLM
    context = ""
    if request.history:
        for msg in request.history:
            context += f"{msg.role.capitalize()}: {msg.content}\n"

    # Combine context + current query        
    state = {"context": context.strip()}

    # Invoke LangGraph chain
    final_state = await support_graph.ainvoke(state)

    # Include which agent handled the response if available
    response_data: Dict[str, Any] = {"response": final_state.get("response", "No response generated.")}
    if "agent" in final_state:
        response_data["agent"] = final_state["agent"]

    return response_data

