1.  

mcp_servers\hotel_server.py

FastMCP exposes Python functions as MCP tools using @mcp.tool; its HTTP server can then be consumed by an MCP client.

2. Skills

The skill should contain behavior/instructions, not the implementation of tools.

skills\hotel_agent\SKILL.md

SKILL
  ↓
Agent behavior

MCP TOOL
  ↓
Actual capability

LANGGRAPH
  ↓
Orchestration/state

LLM
  ↓
Reasoning/tool selection


3. Skill loader

app\utils\skills_loader.py

4. Configuration

app\config.py

5. MCP dynamic tool discovery

This is the most important part of the POC.

We will:

Connect to MCP.

Call list_tools().

Read each MCP tool's schema.

Dynamically create LangChain tools.

When LangGraph invokes a tool, the wrapper calls MCP's call_tool().

The MCP client API explicitly supports list_tools() and call_tool(), with tool names, descriptions and input schemas exposed to the client. 

app\agent\mcp_tools.py

There is one important POC design choice here: the MCP server owns the tool schema. The LangGraph agent does not duplicate the hotel API definitions.

So if tomorrow your MCP server adds:

get_room_types
get_hotel_reviews
get_cancellation_policy
get_nearby_attractions

the agent can discover them without you manually adding each function to the graph.

6. LangGraph state
app\agent\state.py

7. Prompt

app/agent/prompts.py

8.  LangGraph

app\agent\graph.py

                 ┌─────────────┐
                 │   AGENT     │
                 └──────┬──────┘
                        │
                 tool call?
                  /          \
                yes           no
                │              │
                ▼              ▼
          ┌──────────┐       END
          │  TOOLS   │
          └────┬─────┘
               │
               ▼
             AGENT

This is the classic LangGraph tool-calling loop: the model decides whether it needs a tool, ToolNode executes it, and the result goes back to the model.

9. Main application

app/main.py