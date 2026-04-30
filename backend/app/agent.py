"""F1 Agent module to orchestrate the LLM and MCP F1 tools."""

# pylint: disable=line-too-long, too-many-locals

import asyncio
import logging
import os
import sys

import requests
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat")


async def run_f1_agent(year: int = 2026, gp: str = "Japan") -> str:
    """Run an agentic simulation using an MCP client connected to our F1 Server."""

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "app.mcp_server"],
        env=dict(os.environ),
    )

    logger.info("Starting MCP Client connection to app/mcp_server.py...")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            logger.info("MCP Session Initialized!")

            # 1. Ask MCP for available tools
            response = await session.list_tools()
            tools = response.tools

            ollama_tools = []
            for t in tools:
                # Convert MCP tool schema to Ollama tool schema
                ollama_tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": t.name,
                            "description": t.description,
                            "parameters": t.inputSchema,
                        },
                    }
                )

            messages = [
                {
                    "role": "system",
                    "content": "You are an expert F1 journalist. You have tools to investigate the race lap-by-lap. Do NOT hallucinate data. ALWAYS use your tools to get information before writing the report. IMPORTANT: Output ONLY the final report. Do NOT include any conversational filler, meta-commentary, or introductory phrases like 'Now I have all the data I need...'.",
                },
                {
                    "role": "user",
                    "content": f"Write a detailed race report for the {year} {gp} Grand Prix. Ensure you provide deep engineering insights: explicitly use the get_track_status tool to note safety cars, use get_driver_stints to analyze tire strategies, and use get_telemetry_summary to break down top-speeds during key overtakes.",
                },
            ]

            logger.info("Starting Agent Loop...")

            while True:
                payload = {
                    "model": "minimax-m2.7:cloud",
                    "messages": messages,
                    "tools": ollama_tools,
                    "stream": False,
                }

                res = requests.post(OLLAMA_URL, json=payload, timeout=120)
                if res.status_code != 200:
                    logger.error("Ollama Error: %s", res.text)
                    return f"Error: Failed to connect to local LLM: {res.text}"

                data = res.json()
                assistant_message = data.get("message", {})

                messages.append(assistant_message)

                if (
                    "tool_calls" in assistant_message
                    and assistant_message["tool_calls"]
                ):
                    # The LLM decided to use a tool!
                    for tc in assistant_message["tool_calls"]:
                        tool_name = tc["function"]["name"]
                        tool_args = tc["function"]["arguments"]

                        logger.info(
                            "Agent called Tool: %s with args %s", tool_name, tool_args
                        )

                        # Call the tool over MCP
                        tool_res = await session.call_tool(
                            tool_name, arguments=tool_args
                        )
                        result_text = (
                            "\n".join([c.text for c in tool_res.content])
                            if tool_res.content
                            else ""
                        )

                        # Return the true data to the Agent's context history
                        messages.append(
                            {"role": "tool", "name": tool_name, "content": result_text}
                        )
                else:
                    # Final response generated
                    logger.info("Agent Loop Completed.")
                    return assistant_message.get("content", "")


if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(asyncio.run(run_f1_agent(int(sys.argv[1]), sys.argv[2])))
    else:
        print(asyncio.run(run_f1_agent()))
