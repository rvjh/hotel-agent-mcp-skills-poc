```
conda create --prefix ./venv python=3.14 -y
```

```
conda activate ./venv
```

langgraph>=1.0.0
langchain>=1.0.0
langchain-core>=1.0.0
langchain-openai>=1.0.0
fastmcp>=2.0.0
mcp>=2.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
uvicorn>=0.30.0
httpx>=0.27.0

```
pip install -r requirements.txt
```

hotel-agent-poc/
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
│
├── skills/
│   └── hotel_agent/
│       └── SKILL.md
│
├── app/
│   ├── __init__.py
│   │
│   ├── main.py
│   ├── config.py
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── prompts.py
│   │   └── mcp_tools.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── skills_loader.py
│
├── mcp_servers/
│   ├── __init__.py
│   └── hotel_server.py
│
└── tests/
    ├── __init__.py
    └── test_hotel_server.py
