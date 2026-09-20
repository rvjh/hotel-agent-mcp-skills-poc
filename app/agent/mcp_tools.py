from __future__ import annotations

from typing import Any, Optional, Union

from fastmcp import Client
from langchain_core.tools import StructuredTool
from pydantic import Field, create_model


# ============================================================================
# JSON Schema -> Python type
# ============================================================================

def python_type_from_json_schema(
    property_schema: dict,
):
    """
    Convert a simple JSON Schema definition into a Python type.

    Supported:
        string
        integer
        number
        boolean
        array
        object

    This is intentionally lightweight for the POC.
    """

    if not property_schema:
        return str

    schema_type = property_schema.get(
        "type"
    )

    # ------------------------------------------------------------------------
    # Handle nullable / union schemas
    # ------------------------------------------------------------------------

    if isinstance(
        schema_type,
        list,
    ):

        non_null_types = [
            item
            for item in schema_type
            if item != "null"
        ]

        if non_null_types:

            schema_type = (
                non_null_types[0]
            )

        else:

            return str

    # ------------------------------------------------------------------------
    # JSON Schema primitive types
    # ------------------------------------------------------------------------

    if schema_type == "integer":
        return int

    if schema_type == "number":
        return float

    if schema_type == "boolean":
        return bool

    if schema_type == "array":
        return list

    if schema_type == "object":
        return dict

    if schema_type == "string":
        return str

    # ------------------------------------------------------------------------
    # Default
    # ------------------------------------------------------------------------

    return str


# ============================================================================
# Build Pydantic arguments model
# ============================================================================

def build_args_model(
    tool_name: str,
    input_schema: dict,
):
    """
    Convert an MCP tool's JSON Schema into a Pydantic model.

    Example MCP schema:

        {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string"
                },
                "guests": {
                    "type": "integer"
                }
            },
            "required": ["city"]
        }

    Produces approximately:

        class SearchHotelsInput(BaseModel):
            city: str
            guests: Optional[int] = None
    """

    if not input_schema:

        return create_model(
            f"{tool_name}_Input"
        )

    properties = input_schema.get(
        "properties",
        {},
    )

    required = set(
        input_schema.get(
            "required",
            [],
        )
    )

    fields = {}

    for name, schema in properties.items():

        python_type = (
            python_type_from_json_schema(
                schema
            )
        )

        description = schema.get(
            "description",
            f"Argument for {name}",
        )

        # --------------------------------------------------------------------
        # Required argument
        # --------------------------------------------------------------------

        if name in required:

            fields[name] = (
                python_type,
                Field(
                    ...,
                    description=description,
                ),
            )

        # --------------------------------------------------------------------
        # Optional argument
        # --------------------------------------------------------------------

        else:

            fields[name] = (
                Optional[python_type],
                Field(
                    default=None,
                    description=description,
                ),
            )

    return create_model(
        f"{tool_name}_Input",
        **fields,
    )


# ============================================================================
# MCP result extraction
# ============================================================================

def extract_mcp_result(
    result: Any,
):
    """
    Normalize a FastMCP result into a value that LangChain
    can return to the LLM.
    """

    # ------------------------------------------------------------------------
    # Structured content
    # ------------------------------------------------------------------------

    if hasattr(
        result,
        "structured_content",
    ):

        structured_content = (
            result.structured_content
        )

        if structured_content is not None:

            return structured_content

    # ------------------------------------------------------------------------
    # Standard MCP content blocks
    # ------------------------------------------------------------------------

    if hasattr(
        result,
        "content",
    ):

        output = []

        for block in result.content:

            if hasattr(
                block,
                "text",
            ):

                output.append(
                    block.text
                )

            else:

                output.append(
                    str(block)
                )

        return "\n".join(
            output
        )

    # ------------------------------------------------------------------------
    # Fallback
    # ------------------------------------------------------------------------

    return str(result)


# ============================================================================
# MCP tool discovery
# ============================================================================

async def discover_mcp_tools(
    server_url: str,
):
    """
    Dynamically discover MCP tools and convert them into
    LangChain StructuredTool objects.

    Flow:

        FastMCP Server
              |
              | list_tools()
              v
        MCP Tool Definition
              |
              | input_schema
              v
        Pydantic Model
              |
              v
        LangChain StructuredTool
              |
              v
        LangGraph
    """

    print()
    print(
        "[MCP] Connecting to:"
    )
    print(
        f"      {server_url}"
    )

    client = Client(
        server_url
    )

    async with client:

        # ====================================================================
        # Discover MCP tools
        # ====================================================================

        mcp_tools = await client.list_tools()

        print()
        print(
            "[MCP DISCOVERY]"
        )

        print(
            f"Found {len(mcp_tools)} tool(s)"
        )

        for tool in mcp_tools:

            print(
                f"- {tool.name}: "
                f"{tool.description or 'No description'}"
            )

        tools = []

        # ====================================================================
        # Convert every MCP tool
        # ====================================================================

        for mcp_tool in mcp_tools:

            tool_name = mcp_tool.name

            tool_description = (
                mcp_tool.description
                or f"MCP tool: {tool_name}"
            )

            # ----------------------------------------------------------------
            # MCP SDK v2:
            #
            #     input_schema
            #
            # Older versions:
            #
            #     inputSchema
            #
            # Prefer input_schema.
            # ----------------------------------------------------------------

            input_schema = getattr(
                mcp_tool,
                "input_schema",
                None,
            )

            # Backward compatibility
            if input_schema is None:

                input_schema = getattr(
                    mcp_tool,
                    "inputSchema",
                    None,
                )

            if input_schema is None:

                input_schema = {
                    "type": "object",
                    "properties": {},
                }

            # ----------------------------------------------------------------
            # Build Pydantic model
            # ----------------------------------------------------------------

            args_model = build_args_model(
                tool_name,
                input_schema,
            )

            # ----------------------------------------------------------------
            # MCP execution wrapper
            #
            # Capture tool_name as a local default so every generated
            # function invokes the correct MCP tool.
            # ----------------------------------------------------------------

            async def call_mcp_tool(
                _tool_name=tool_name,
                **kwargs,
            ):
                """
                Execute the dynamically discovered MCP tool.
                """

                # ------------------------------------------------------------
                # Remove None values.
                #
                # Example:
                #
                # {
                #     "city": "Bengaluru",
                #     "guests": None
                # }
                #
                # becomes:
                #
                # {
                #     "city": "Bengaluru"
                # }
                # ------------------------------------------------------------

                clean_kwargs = {
                    key: value
                    for key, value in kwargs.items()
                    if value is not None
                }

                print()
                print(
                    "[MCP CALL]"
                )

                print(
                    f"Tool: {_tool_name}"
                )

                print(
                    f"Arguments: {clean_kwargs}"
                )

                # ------------------------------------------------------------
                # Create MCP client for tool invocation
                # ------------------------------------------------------------

                async with Client(
                    server_url
                ) as call_client:

                    result = await call_client.call_tool(
                        _tool_name,
                        clean_kwargs,
                    )

                # ------------------------------------------------------------
                # Normalize MCP response
                # ------------------------------------------------------------

                normalized_result = (
                    extract_mcp_result(
                        result
                    )
                )

                print(
                    "[MCP RESULT]"
                )

                print(
                    normalized_result
                )

                return normalized_result

            # ----------------------------------------------------------------
            # Create LangChain StructuredTool
            # ----------------------------------------------------------------

            langchain_tool = (
                StructuredTool.from_function(
                    coroutine=call_mcp_tool,
                    name=tool_name,
                    description=tool_description,
                    args_schema=args_model,
                )
            )

            tools.append(
                langchain_tool
            )

        # ====================================================================
        # Summary
        # ====================================================================

        print()
        print(
            "[MCP] Dynamic tool conversion complete"
        )

        print(
            f"[MCP] LangChain tools: {len(tools)}"
        )

        for tool in tools:

            print(
                f"      - {tool.name}"
            )

        return tools
