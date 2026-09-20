# Hotel Agent — Execution Flow

 This project uses **MCP, FastMCP, Skills, LangChain, LangGraph, and an LLM** to build a dynamic hotel agent.

 The main flow is:

```
USER
  │
  ▼
app/main.py
  │
  ▼
app/config.py
  │
  ▼
skills/hotel_agent/SKILL.md
  │
  ▼
app/utils/skills_loader.py
  │
  ▼
app/agent/mcp_tools.py
  │
  │  Connect to MCP
  │  └── list_tools()
  │      ├── Tool name
  │      ├── Description
  │      └── Input schema
  │
  ▼
Dynamic LangChain Tools
  │
  ▼
app/agent/state.py
  │
  ▼
app/agent/prompts.py
  │
  ▼
app/agent/graph.py
  │
  ▼
LLM / AGENT
  │
  ├── No tool required ──────► END
  │
  └── Tool required
           │
           ▼
      Dynamic MCP Tool
           │
           ▼
       call_tool()
           │
           ▼
mcp_servers/hotel_server.py
           │
           ▼
      MCP Tool Execution
           │
           ▼
        Tool Result
           │
           ▼
          AGENT
```

---

## 1\. MCP Server

### `mcp_servers/hotel_server.py`

 This is the **MCP server**.

 FastMCP exposes Python functions as MCP tools using the `@mcp.tool` decorator.

```
Python Function
      │
      ▼
  @mcp.tool
      │
      ▼
   MCP Tool
```

 The MCP server owns the:

- Actual tool implementation
- Tool name
- Tool description
- Tool input schema
- Tool execution

 The MCP server is the **source of truth for the available tools**.

---

## 2\. Skills

### `skills/hotel_agent/SKILL.md`

 The skill contains the **behavior and instructions** for the hotel agent.

 The skill should describe what the agent should do, not implement the actual tools.

```
SKILL
  ↓
Agent behavior
```

 The separation of responsibilities is:

```
SKILL
  ↓
Agent behavior

MCP TOOL
  ↓
Actual capability

LANGGRAPH
  ↓
Orchestration / State

LLM
  ↓
Reasoning / Tool Selection
```

---

## 3\. Skill Loader

### `app/utils/skills_loader.py`

 The skill loader reads the skill instructions from `SKILL.md` and makes them available to the agent.

```
skills/hotel_agent/SKILL.md
            │
            ▼
    skills_loader.py
            │
            ▼
     Agent Instructions
```

---

## 4\. Configuration

### `app/config.py`

 Contains the application configuration.

 This can include:

- MCP server configuration
- LLM configuration
- Environment variables
- Model settings
- Other application-level settings

```
Configuration
      │
      ▼
app/config.py
```

---

## 5\. Dynamic MCP Tool Discovery

### `app/agent/mcp_tools.py`

 This is the **most important part of the POC**.

 Instead of manually defining every hotel tool in the LangGraph agent, the application dynamically discovers the tools exposed by the MCP server.

### Discovery Flow

```
Connect to MCP
      │
      ▼
list_tools()
      │
      ▼
Read tool information
      │
      ├── Tool name
      ├── Description
      └── Input schema
      │
      ▼
Create Dynamic LangChain Tools
      │
      ▼
Make tools available to LangGraph
```

### Tool Execution Flow

 When the LangGraph agent decides to use a tool:

```
LLM
 │
 ▼
LangGraph
 │
 ▼
Dynamic LangChain Tool
 │
 ▼
MCP call_tool()
 │
 ▼
MCP Server
 │
 ▼
Tool Execution
 │
 ▼
Tool Result
 │
 ▼
LangGraph Agent
```

### Important Design Choice

 The **MCP server owns the tool schema**.

 The LangGraph agent does **not** duplicate the hotel API definitions.

 For example, if the MCP server currently exposes:

```
search_hotels
get_hotel_details
```

 the agent discovers them dynamically.

 If the MCP server later adds:

```
get_room_types
get_hotel_reviews
get_cancellation_policy
get_nearby_attractions
```

 the agent can discover these new tools through `list_tools()` without manually adding each function to the LangGraph.

 This makes the architecture dynamic and extensible.

---

## 6\. LangGraph State

### `app/agent/state.py`

 Defines the state used by LangGraph.

 The state carries information through the agent workflow, including messages, tool calls, and tool results.

```
User Input
    │
    ▼
Agent State
    │
    ▼
LangGraph Nodes
    │
    ▼
Updated State
```

---

## 7\. Prompt

### `app/agent/prompts.py`

 Contains the prompts used by the LLM.

 The prompt works together with the skill instructions to define the agent's behavior.

```
SKILL.md
   │
   ▼
Skill Instructions
   │
   +
   │
Prompt
   │
   ▼
LLM
```

 The LLM uses these instructions to understand the user's request and decide whether a tool is required.

---

## 8\. LangGraph

### `app/agent/graph.py`

 Builds and orchestrates the LangGraph agent.

 The graph follows the standard tool-calling loop:

```
                 ┌─────────────┐
                 │    AGENT    │
                 └──────┬──────┘
                        │
                   Tool call?
                    /       \
                  yes         no
                  │            │
                  ▼            ▼
            ┌──────────┐      END
            │  TOOLS   │
            └────┬─────┘
                 │
                 ▼
               AGENT
```

### How It Works

1. The LLM receives the user request and available tools.
2. The LLM decides whether a tool is required.
3. If no tool is required, the agent returns the response.
4. If a tool is required, LangGraph executes the selected tool.
5. The tool result is returned to the agent.
6. The LLM processes the result.
7. The agent can either call another tool or return the final response.

```
AGENT
  │
  ├── No tool required ──────► END
  │
  └── Tool required
          │
          ▼
        TOOLS
          │
          ▼
      Tool Result
          │
          ▼
        AGENT
```

---

## 9\. Main Application

### `app/main.py`

 This is the **main entry point** of the application.

 It brings the different components together:

```
app/main.py
     │
     ▼
Load Configuration
     │
     ▼
Load Skill
     │
     ▼
Connect to MCP
     │
     ▼
Discover MCP Tools
     │
     ▼
Create Dynamic Tools
     │
     ▼
Build LangGraph
     │
     ▼
Start Agent
     │
     ▼
Accept User Questions
```

---

# Complete File Flow

```
┌──────────────────────────────────────┐
│             app/main.py              │
│          Main Application            │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│            app/config.py             │
│           Configuration              │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│   skills/hotel_agent/SKILL.md        │
│        Agent Behavior / Rules        │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│     app/utils/skills_loader.py       │
│          Loads the Skill             │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│       app/agent/mcp_tools.py         │
│       Dynamic MCP Tool Discovery     │
│                                      │
│          list_tools()                │
│               ↓                      │
│       Dynamic LangChain Tools        │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│        app/agent/state.py            │
│          LangGraph State             │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│       app/agent/prompts.py           │
│             Prompts                  │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│         app/agent/graph.py           │
│        LangGraph Orchestration       │
└──────────────────┬───────────────────┘
                   │
                   ▼
                ┌───────┐
                │  LLM  │
                └───┬───┘
                    │
              Tool required?
               /          \
             No            Yes
             │              │
             ▼              ▼
            END       Dynamic MCP Tool
                            │
                            ▼
                       call_tool()
                            │
                            ▼
              ┌─────────────────────────┐
              │ mcp_servers/            │
              │ hotel_server.py         │
              │                         │
              │ MCP Tool Execution      │
              └────────────┬────────────┘
                           │
                           ▼
                      Tool Result
                           │
                           ▼
                         AGENT
```

---

# Runtime Flow

 The runtime interaction is:

```
User
 │
 ▼
Agent
 │
 ▼
LLM
 │
 ├── Answer directly ─────────────► Response
 │
 └── Need information/capability
              │
              ▼
        Dynamic MCP Tool
              │
              ▼
         call_tool()
              │
              ▼
        MCP Server
              │
              ▼
        Tool Execution
              │
              ▼
         Tool Result
              │
              ▼
             LLM
              │
              ▼
           Response
```

---

# Run the Application

## Terminal 1 — Start MCP Server

```
python mcp_servers/hotel_server.py
```

## Terminal 2 — Start Agent

```
python -m app.main
```

 Once both applications are running, enter your hotel-related questions in the agent terminal.
