import json
from typing import Any

from fastmcp import Client
from langchain_core.tools import StructuredTool
from pydantic import create_model


def python_type_from_json_schema(property_schema: dict):
    """
    Very small JSON Schema -> Python type mapper.

    This is intentionally simple for the POC.
    A production implementation should handle:
    arrays, enums, unions, nested objects, etc.
    """

    schema_type = property_schema.get("type", "string")

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

    return str


def build_args_model(tool_name: str, input_schema: dict):
    """
    Convert MCP JSON schema into a Pydantic model.
    """

    properties = input_schema.get("properties",{})

    required = set(input_schema.get("required", []))

    fields = {}

    for name, schema in properties.items():

        python_type = python_type_from_json_schema(schema)

        description = schema.get(
            "description",
            f"Argument for {name}",
        )

        if name in required:
            fields[name] = (
                python_type,
                ...,
            )
        else:
            fields[name] = (
                python_type | None,
                None,
            )

    return create_model(
        f"{tool_name}_Input",
        **fields,
    )


def extract_mcp_result(result: Any):
    """
    Normalize FastMCP result into something
    LangChain can pass back to the model.
    """

    if hasattr(result, "structured_content"):
        if result.structured_content is not None:
            return result.structured_content

    if hasattr(result, "content"):

        output = []

        for block in result.content:

            if hasattr(block, "text"):
                output.append(block.text)

            else:
                output.append(str(block))

        return "\n".join(output)

    return str(result)


async def discover_mcp_tools(server_url: str):
    """
    Discover MCP tools dynamically and convert them
    into LangChain StructuredTool objects.
    """

    client = Client(server_url)

    async with client:

        mcp_tools = await client.list_tools()

        print("\n[MCP DISCOVERY]")

        for tool in mcp_tools:
            print(
                f"- {tool.name}: "
                f"{tool.description}"
            )

        tools = []

        for mcp_tool in mcp_tools:

            args_model = build_args_model(
                mcp_tool.name,
                mcp_tool.inputSchema,
            )

            async def call_mcp_tool(
                _tool_name=mcp_tool.name,
                **kwargs,
            ):

                async with Client(server_url) as call_client:

                    result = await call_client.call_tool(
                        _tool_name,
                        kwargs,
                    )

                    return extract_mcp_result(
                        result
                    )

            langchain_tool = StructuredTool.from_function(
                coroutine=call_mcp_tool,
                name=mcp_tool.name,
                description=mcp_tool.description
                or f"MCP tool: {mcp_tool.name}",
                args_schema=args_model,
            )

            tools.append(
                langchain_tool
            )

        return tools
