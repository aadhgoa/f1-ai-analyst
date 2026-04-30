"""API routes for the F1 AI Analyst."""

from fastapi import APIRouter
from app.agent import run_f1_agent
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
