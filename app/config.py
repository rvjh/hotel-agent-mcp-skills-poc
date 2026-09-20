import os
from dotenv import load_dotenv


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

MCP_HOTEL_SERVER_URL = os.getenv("MCP_HOTEL_SERVER_URL", "http://localhost:8001/mcp")
