"""
Hotel Agent - Application Entry Point

Run from repository root:

    python -m app.main

Single query:

    python -m app.main "Find hotels in Bangalore for 2 adults"
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from app import config
from app.utils.skills_loader import load_skill
from app.agent.mcp_tools import discover_mcp_tools
from app.agent.graph import build_graph


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

SKILL_PATH = (
    ROOT_DIR
    / "skills"
    / "hotel_agent"
    / "SKILL.md"
)


# ---------------------------------------------------------------------------
# Load Skill
# ---------------------------------------------------------------------------

def load_hotel_skill() -> str:
    """
    Load the hotel agent skill instructions.
    """

    print(
        f"[SKILLS] Loading: {SKILL_PATH}"
    )

    skill = load_skill(
        str(SKILL_PATH)
    )

    print(
        "[SKILLS] Hotel skill loaded"
    )

    return skill


# ---------------------------------------------------------------------------
# Extract final response
# ---------------------------------------------------------------------------

def extract_final_response(result) -> str:
    """
    Extract the final AI response from LangGraph state.
    """

    if not result:
        return ""

    messages = result.get(
        "messages",
        [],
    )

    if not messages:
        return str(result)

    # Search backwards for the final AI message.
    for message in reversed(messages):

        # LangChain AIMessage
        if hasattr(
            message,
            "type",
        ):

            if message.type == "ai":

                content = getattr(
                    message,
                    "content",
                    "",
                )

                if content:
                    return content

        # Dictionary message
        if isinstance(
            message,
            dict,
        ):

            role = message.get(
                "role"
            )

            if role in {
                "assistant",
                "ai",
            }:

                return message.get(
                    "content",
                    "",
                )

    # Fallback
    last_message = messages[-1]

    if hasattr(
        last_message,
        "content",
    ):
        return last_message.content

    if isinstance(
        last_message,
        dict,
    ):
        return last_message.get(
            "content",
            str(last_message),
        )

    return str(last_message)


# ---------------------------------------------------------------------------
# Create Application
# ---------------------------------------------------------------------------

async def create_application():
    """
    Initialize the complete hotel agent.

    Flow:

        SKILL.md
            |
            v
        Skill Loader
            |
            v
        MCP list_tools()
            |
            v
        Dynamic LangChain Tools
            |
            v
        LangGraph
    """

    print()
    print("=" * 70)
    print("HOTEL AGENT")
    print("=" * 70)

    # -----------------------------------------------------------------------
    # 1. Load skill
    # -----------------------------------------------------------------------

    print()
    print("[1/3] Loading skill...")

    skill = load_hotel_skill()

    # -----------------------------------------------------------------------
    # 2. Discover MCP tools
    # -----------------------------------------------------------------------

    print()
    print("[2/3] Discovering MCP tools...")

    print(
        f"      MCP Server: "
        f"{config.MCP_HOTEL_SERVER_URL}"
    )

    tools = await discover_mcp_tools(
        config.MCP_HOTEL_SERVER_URL
    )

    print()
    print(
        f"      Discovered {len(tools)} MCP tool(s)"
    )

    for tool in tools:

        print(
            f"      - {tool.name}"
        )

    if not tools:

        raise RuntimeError(
            "No MCP tools discovered.\n"
            "Make sure the FastMCP hotel server is running."
        )

    # -----------------------------------------------------------------------
    # 3. Build LangGraph
    # -----------------------------------------------------------------------

    print()
    print("[3/3] Building LangGraph...")

    graph = build_graph(
        skill=skill,
        tools=tools,
    )

    print(
        "      LangGraph ready"
    )

    print()
    print("=" * 70)
    print("AGENT READY")
    print("=" * 70)

    return graph


# ---------------------------------------------------------------------------
# Run Query
# ---------------------------------------------------------------------------

async def run_query(
    graph,
    query: str,
):

    result = await graph.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ]
        }
    )

    return result


# ---------------------------------------------------------------------------
# Interactive Mode
# ---------------------------------------------------------------------------

async def interactive_loop(
    graph,
):

    print()
    print(
        "Type your hotel request."
    )

    print(
        "Type 'exit' or 'quit' to stop."
    )

    print()

    while True:

        try:

            query = input(
                "You: "
            ).strip()

        except (
            KeyboardInterrupt,
            EOFError,
        ):

            print()
            print(
                "Exiting..."
            )

            break

        if not query:
            continue

        if query.lower() in {
            "exit",
            "quit",
            "q",
        }:

            print(
                "Goodbye!"
            )

            break

        try:

            result = await run_query(
                graph,
                query,
            )

            response = extract_final_response(
                result
            )

            print()
            print(
                "Agent:"
            )
            print(
                response
            )
            print()

        except Exception as exc:

            print()
            print(
                "Agent error:"
            )
            print(
                f"{type(exc).__name__}: {exc}"
            )
            print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():

    # -----------------------------------------------------------------------
    # Initialize
    # -----------------------------------------------------------------------

    graph = await create_application()

    # -----------------------------------------------------------------------
    # Single query mode
    #
    # python -m app.main "Find hotels in Bangalore"
    # -----------------------------------------------------------------------

    if len(sys.argv) > 1:

        query = " ".join(
            sys.argv[1:]
        )

        print()
        print(
            f"Query: {query}"
        )

        print()

        result = await run_query(
            graph,
            query,
        )

        response = extract_final_response(
            result
        )

        print(
            "Agent:"
        )

        print(
            response
        )

        return

    # -----------------------------------------------------------------------
    # Interactive mode
    #
    # python -m app.main
    # -----------------------------------------------------------------------

    await interactive_loop(
        graph
    )


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print()
        print(
            "Stopped."
        )

    except Exception as exc:

        print()
        print("=" * 70)
        print("APPLICATION FAILED")
        print("=" * 70)

        print(
            f"{type(exc).__name__}: {exc}"
        )

        print("=" * 70)

        sys.exit(1)
