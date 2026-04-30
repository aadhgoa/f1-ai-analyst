"""Service for interacting with local LLMs to generate F1 content."""

# pylint: disable=line-too-long

import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_GENERATE_URL", "http://localhost:11434/api/generate")


def generate_summary(events: list[str], gp: str, year: int) -> str:
    """Generate a high-energy narrative summary of the race."""

    prompt = f"""
You are an expert Formula 1 journalist and race commentator.

Using the race events from the {gp} Grand Prix in {year} below, write a vivid, high-energy narrative of the race as if it were being retold in a post-race feature article.

Race events:
{events}

Instructions:
- Tell the story in chronological order, turning raw events into a dramatic and engaging narrative.
- Capture the atmosphere: weather, crowd energy, tension, and stakes of the race.
- Highlight key moments such as overtakes, crashes, pit strategies, safety cars, and turning points.
- Include driver perspectives, emotions, and rivalries where relevant.
- Use dynamic, descriptive language to make the reader feel like they are watching the race unfold.
- Add context about the championship battle or importance of this race if applicable.
- Maintain factual accuracy based on the provided events, but enhance storytelling with realistic detail.
- Write in a professional motorsport journalism style (similar to F1.com or top sports media).

Output:
A compelling race story in 500-900 words.
"""

    payload = {"model": "minimax-m2.7:cloud", "prompt": prompt, "stream": False}

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    data = response.json()

    return data["response"]
