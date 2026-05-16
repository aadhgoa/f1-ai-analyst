"""Model Context Protocol (MCP) server for exposing F1 telemetry tools to the agent."""

# pylint: disable=line-too-long, wrong-import-position, too-many-function-args

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp.server.fastmcp import FastMCP
from app.services.data_service import F1RaceAnalyzer
from app.services.event_service import detect_events
import chromadb
from chromadb.utils import embedding_functions

mcp = FastMCP("f1_analyst")

@mcp.tool()
def query_historical_context(query: str) -> str:
    """
    Query historical F1 context from the vector database.
    Use this to look up past performances, track histories, or driver biographies.
    """
    try:
        client = chromadb.HttpClient(host="localhost", port=8080)
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        collection = client.get_collection(name="f1_context", embedding_function=sentence_transformer_ef)
        
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        if not results['documents'] or not results['documents'][0]:
            return "No historical context found."
            
        context = []
        for doc in results['documents'][0]:
            context.append(doc)
        return "\n".join(context)
    except Exception as e:
        return f"Error querying vector DB: {str(e)}"


@mcp.tool()
def get_race_overview(year: int, gp: str) -> str:
    """
    Get a high-level overview of the race, including the podium finishers,
    the final standings, and the fastest lap of the race. Use this to establish baseline facts.
    """
    analyzer = F1RaceAnalyzer(year, gp)
    laps = analyzer.get_race_data()
    if laps.is_empty():
        return f"No data found for {year} {gp}"

    # We query the very last lap to get the final standing events which we added to event_service
    max_lap = int(laps.drop_nulls("LapNumber")["LapNumber"].max())
    events = detect_events(laps, start_lap=max_lap, end_lap=max_lap)
    return "\n".join(events)


@mcp.tool()
def get_lap_events_slice(year: int, gp: str, start_lap: int, end_lap: int) -> str:
    """
    Get a detailed timeline of events (overtakes, pit stops, penalties, retirements)
    that occurred between a specific start lap and end lap.
    Use this to paginate through the race or investigate specific incidents.
    """
    analyzer = F1RaceAnalyzer(year, gp)
    laps = analyzer.get_race_data()
    if laps.is_empty():
        return f"No data found for {year} {gp}"

    events = detect_events(laps, start_lap=start_lap, end_lap=end_lap)
    if not events:
        return f"No notable events found between lap {start_lap} and lap {end_lap}."
    return "\n".join(events)


@mcp.tool()
def get_total_laps(year: int, gp: str) -> int:
    """
    Find out the total number of laps in a race, useful for knowing the bounds of the race before slicing.
    """
    analyzer = F1RaceAnalyzer(year, gp)
    laps = analyzer.get_race_data()
    if laps.is_empty():
        return 0
    return int(laps.drop_nulls("LapNumber")["LapNumber"].max())


@mcp.tool()
def get_track_status(year: int, gp: str) -> str:
    """
    Get a timeline of major track incidents (Safety Cars, Virtual Safety Cars, Red Flags).
    Use this to understand why pit-stop flurries happened or why gaps between drivers suddenly closed up.
    """
    analyzer = F1RaceAnalyzer(year, gp)
    return analyzer.extract_track_status()


@mcp.tool()
def get_driver_stints(year: int, gp: str, driver: str) -> str:
    """
    Get a breakdown of a driver's tire strategy. Includes the compounds used (Soft/Medium/Hard),
    the start/end lap of each stint, and the average lap pace.
    Use this to analyze undercuts, overcuts, and tire degradation advantages!
    """
    analyzer = F1RaceAnalyzer(year, gp)
    return analyzer.extract_driver_stints(driver)


@mcp.tool()
def get_telemetry_summary(year: int, gp: str, driver: str, lap: int) -> str:
    """
    Analyze the raw engineering telemetry for a specific driver on a specific lap.
    Returns their Top Speed, Minimum Apex Speed, Full Throttle %, and Braking %.
    Use this to narrate exactly *how* an overtake was executed! (e.g. later braking or straight-line speed)
    """
    analyzer = F1RaceAnalyzer(year, gp)
    return analyzer.extract_telemetry_summary(driver, lap)


if __name__ == "__main__":
    # Start the fastmcp server
    # Run this via `python -m app.mcp_server`
    mcp.run()
