"""API routes for the F1 AI Analyst."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.agent import run_f1_agent, run_f1_chat
from app.services.data_service import F1RaceAnalyzer

router = APIRouter()


@router.get("/api/v1/race-summary")
async def race_summary(year: int = 2026, gp: str = "Japan"):
    """Generate a race summary using the F1 agent."""

    # Use the autonomous agent loop instead of the linear generate_summary
    summary = await run_f1_agent(year, gp)

    return {"summary": summary}


@router.get("/api/v1/dashboard-data")
async def get_dashboard(year: int = 2026, gp: str = "Japan"):
    """Get telemetry data for the dashboard."""
    analyzer = F1RaceAnalyzer(year, gp)
    data = analyzer.get_dashboard_data()
    return data


class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

@router.post("/api/v1/chat")
async def chat_endpoint(request: ChatRequest):
    """Interact with the multi-agent F1 analyst."""
    chat_history = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    response = await run_f1_chat(chat_history)
    return {"response": response}


@router.get("/api/v1/test-rag")
async def test_rag(query: str = "Where was the first race of 2023?"):
    """Test route to query ChromaDB for contextual strings."""
    import chromadb
    from chromadb.utils import embedding_functions
    try:
        client = chromadb.HttpClient(host="localhost", port=8080)
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        collection = client.get_collection(name="f1_context", embedding_function=sentence_transformer_ef)
        
        results = collection.query(
            query_texts=[query],
            n_results=2
        )
        return {"query": query, "results": results}
    except Exception as e:
        return {"error": str(e)}

