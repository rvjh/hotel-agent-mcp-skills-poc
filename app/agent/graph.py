from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage

from langgraph.graph import StateGraph,START,END

from langgraph.prebuilt import ToolNode, tools_condition

from app.agent.state import HotelAgentState
from app.agent.prompts import build_system_prompt
from app.config import GROQ_MODEL


def build_graph(tools, skill: str):

    llm = ChatGroq(model=GROQ_MODEL,temperature=0)

    llm_with_tools = llm.bind_tools(tools)

    system_prompt = build_system_prompt(skill)

    # ------------------------------------------------------------
    # Agent node
    # ------------------------------------------------------------

    async def agent_node(state: HotelAgentState):
        messages = [
            SystemMessage(
                content=system_prompt
            ),
            *state["messages"],
        ]

        response = await llm_with_tools.ainvoke(messages)

        return {
            "messages": [response]
        }

    # ------------------------------------------------------------
    # Tool node
    # ------------------------------------------------------------

    tool_node = ToolNode(tools)

    # ------------------------------------------------------------
    # Graph
    # ------------------------------------------------------------

    graph = StateGraph(HotelAgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "agent")

    graph.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            "__end__": END,
        },
    )

    graph.add_edge("tools", "agent")

    return graph.compile()
