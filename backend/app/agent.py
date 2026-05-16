"""F1 Agent module orchestrated with LangGraph and MCP."""

import asyncio
import logging
import os
import sys
import warnings
from typing import Annotated, Sequence, TypedDict, Literal

# Suppress LangChain and LangGraph warnings
warnings.filterwarnings("ignore", message=".*Core Pydantic V1 functionality isn't compatible.*")
warnings.filterwarnings("ignore", message=".*The default value of `allowed_objects` will change.*")

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """The state passed between all nodes in the Multi-Agent graph."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next_agent: str


class Route(BaseModel):
    """Structured output schema for the Supervisor routing decision."""
    next_node: Literal["strategy_agent", "driver_agent", "FINISH"] = Field(
        description="The next agent to route to. Choose 'strategy_agent' for pit stops/tires, 'driver_agent' for telemetry/speed, or 'FINISH' if the user's request is fully answered."
    )


class F1AgentWorkflow:
    """Encapsulates the Multi-Agent F1 Workflow, nodes, and MCP Session management."""
    
    def __init__(self):
        self.llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "gpt-oss:20b"), temperature=0)
        self.session: ClientSession | None = None
        
        # Tool catalogs populated via MCP
        self.strategy_tools = []
        self.driver_tools = []
        self.orchestrator_tools = []

    # -------------------------------------------------------------------------
    # Node Definitions
    # -------------------------------------------------------------------------

    async def supervisor_node(self, state: AgentState):
        logger.info("-> SUPERVISOR NODE")
        sys_msg = SystemMessage(
            content="You are the Supervisor. Route the conversation to the correct agent based on the user's request. If the user's question has been answered, output FINISH."
        )
        router_llm = self.llm.with_structured_output(Route)
        res = await router_llm.ainvoke([sys_msg] + state["messages"])
        next_node = res.next_node if res else "FINISH"
        return {"next_agent": next_node}
        
    async def orchestrator_node(self, state: AgentState):
        logger.info("-> ORCHESTRATOR NODE (Final Synthesis)")
        sys_msg = SystemMessage(
            content="You are the Orchestrator. Synthesize the findings from the agents to answer the user. Use your tools if you need high level context."
        )
        agent_llm = self.llm.bind_tools(self.orchestrator_tools)
        res = await agent_llm.ainvoke([sys_msg] + state["messages"])
        return {"messages": [res]}

    async def strategy_agent(self, state: AgentState):
        logger.info("-> STRATEGY AGENT")
        sys_msg = SystemMessage(
            content="You are the Strategy Agent. Use your tools to fetch tire and pit stop data, then summarize your findings."
        )
        agent_llm = self.llm.bind_tools(self.strategy_tools)
        res = await agent_llm.ainvoke([sys_msg] + state["messages"])
        return {"messages": [res]}

    async def driver_agent(self, state: AgentState):
        logger.info("-> DRIVER AGENT")
        sys_msg = SystemMessage(
            content="You are the Driver Performance Agent. Use your tools to fetch telemetry, then summarize your findings."
        )
        agent_llm = self.llm.bind_tools(self.driver_tools)
        res = await agent_llm.ainvoke([sys_msg] + state["messages"])
        return {"messages": [res]}

    async def tool_executor(self, state: AgentState):
        logger.info("-> TOOL EXECUTOR")
        last_msg = state["messages"][-1]
        tool_messages = []
        
        for tc in last_msg.tool_calls:
            logger.info(f"Executing tool: {tc['name']}")
            try:
                tool_res = await self.session.call_tool(tc["name"], arguments=tc["args"])
                result_text = "\n".join([c.text for c in tool_res.content]) if tool_res.content else ""
            except Exception as e:
                result_text = f"Error: {str(e)}"
            tool_messages.append(ToolMessage(content=result_text, tool_call_id=tc["id"], name=tc["name"]))
            
        return {"messages": tool_messages}

    # -------------------------------------------------------------------------
    # Routing Logic
    # -------------------------------------------------------------------------

    def general_router(self, state: AgentState) -> str:
        last_msg = state["messages"][-1]
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            return "tool_executor"
        
        # If an agent finished generating a response, send to orchestrator for synthesis
        if last_msg.name in ["strategy_agent", "driver_agent"] or (hasattr(last_msg, "content") and "Agent" in str(last_msg.content)):
            return "orchestrator"
        
        return "supervisor"

    def supervisor_router(self, state: AgentState) -> str:
        if state["next_agent"] == "FINISH":
            return "orchestrator"
        return state["next_agent"]

    def orchestrator_router(self, state: AgentState) -> str:
        last_msg = state["messages"][-1]
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            return "tool_executor"
        return "__end__"

    def tool_return_router(self, state: AgentState) -> str:
        # Simplified: After any tool executes, the orchestrator handles synthesizing the final output
        return "orchestrator"

    # -------------------------------------------------------------------------
    # Graph Construction & Execution
    # -------------------------------------------------------------------------

    def build_graph(self):
        """Constructs and compiles the StateGraph."""
        workflow = StateGraph(AgentState)
        
        workflow.add_node("supervisor", self.supervisor_node)
        workflow.add_node("orchestrator", self.orchestrator_node)
        workflow.add_node("strategy_agent", self.strategy_agent)
        workflow.add_node("driver_agent", self.driver_agent)
        workflow.add_node("tool_executor", self.tool_executor)

        workflow.add_edge(START, "supervisor")
        workflow.add_conditional_edges("supervisor", self.supervisor_router)
        
        workflow.add_conditional_edges("strategy_agent", self.general_router)
        workflow.add_conditional_edges("driver_agent", self.general_router)
        workflow.add_conditional_edges("orchestrator", self.orchestrator_router, {"tool_executor": "tool_executor", "__end__": END})
        
        workflow.add_conditional_edges("tool_executor", self.tool_return_router)

        return workflow.compile()

    def _setup_mcp_tools(self, mcp_tools):
        """Converts MCP schemas to Ollama schemas and categorizes them."""
        ollama_tools = []
        for t in mcp_tools:
            ollama_tools.append({
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.inputSchema,
                },
            })
            
        self.strategy_tools = [t for t in ollama_tools if t["function"]["name"] in ["get_driver_stints", "get_lap_events_slice"]]
        self.driver_tools = [t for t in ollama_tools if t["function"]["name"] in ["get_telemetry_summary"]]
        self.orchestrator_tools = [t for t in ollama_tools if t["function"]["name"] in ["query_historical_context", "get_race_overview", "get_total_laps", "get_track_status"]]

    async def execute(self, initial_messages: list) -> str:
        """Main entry point to execute the workflow within an MCP context."""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "python", "-m", "app.mcp_server"],
            env=dict(os.environ),
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                response = await session.list_tools()
                
                self.session = session
                self._setup_mcp_tools(response.tools)
                
                app = self.build_graph()
                logger.info("Starting LangGraph execution...")
                final_state = await app.ainvoke({"messages": initial_messages, "next_agent": ""})
                
                return final_state["messages"][-1].content


# -------------------------------------------------------------------------
# Public API Endpoints
# -------------------------------------------------------------------------

async def run_f1_chat(chat_history: list) -> str:
    messages = []
    for msg in chat_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
            
    workflow = F1AgentWorkflow()
    return await workflow.execute(messages)


async def run_f1_agent(year: int = 2026, gp: str = "Japan") -> str:
    user_prompt = f"Write a detailed race report for the {year} {gp} Grand Prix. Ensure you provide deep engineering insights."
    workflow = F1AgentWorkflow()
    return await workflow.execute([HumanMessage(content=user_prompt)])


if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(asyncio.run(run_f1_agent(int(sys.argv[1]), sys.argv[2])))
    else:
        print(asyncio.run(run_f1_agent()))
