 ## How to Run

 The application requires **two terminals** running simultaneously.

 ### Terminal 1 — Start the MCP Server

 From the project root directory, run:

```
python mcp_servers/hotel_server.py
```

 Keep this terminal running. The MCP server needs to remain active so that the agent can communicate with it.

 ### Terminal 2 — Start the Agent

 Open a second terminal in the project root directory and run:

```
python -m app.main
```

 Once the agent starts successfully, you can enter questions or requests for the hotel agent.

 ## Testing the Agent

 After starting both the MCP server and the agent, enter questions in the agent terminal to verify that it can understand requests and interact with the MCP server correctly.

 ### Example Questions

 You can test the agent with questions such as:

```
Find hotels in Bengaluru.
```

```
Find hotels in Mumbai.
```

```
What hotels are available in Bengaluru?
```

```
Show me hotels with good ratings.
```

```
Find a hotel suitable for a business trip.
```

 You can also test variations of the same request to verify how the agent handles different locations, requirements, and natural-language queries.

 ## Test Results

 The file:

```
Test results - Outputs.docx
```

 contains the test questions and corresponding outputs/results obtained while testing the agent.

 Use this document as a reference for validating the agent's behavior and MCP tool integration.

 ## Execution Flow

 The overall execution flow is:

```
User
  │
  │  Question
  ▼
Agent (app.main)
  │
  │  MCP communication
  ▼
Hotel MCP Server
(mcp_servers/hotel_server.py)
  │
  │  Hotel-related tools/data
  ▼
Agent
  │
  ▼
Response to User
```

 ## Troubleshooting

 ### MCP Server Is Not Running

 Make sure Terminal 1 is still running:

```
python mcp_servers/hotel_server.py
```

 The agent may not be able to execute hotel-related operations if the MCP server has stopped.

 ### Agent Does Not Start

 Verify that you are running the command from the project root:

```
python -m app.main
```

 Also check that all required dependencies have been installed.

 ### Connection or MCP Errors

 If the agent cannot communicate with the MCP server:

 1. Confirm that the MCP server is running in Terminal 1.
2. Confirm that the agent is running in Terminal 2.
3. Check the terminal output from both processes for errors.
4. Verify that the MCP configuration and environment variables are correct.

 ## Quick Start

 For a quick test, open two terminals.

 **Terminal 1:**

```
python mcp_servers/hotel_server.py
```

 **Terminal 2:**

```
python -m app.main
```

 Then enter your hotel-related questions in Terminal 2.

 Refer to **`Test results - Outputs.docx`** for the test cases and outputs.
