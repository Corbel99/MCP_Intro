# MCP Servers in Python: Programming Learning MCP Server

A simple MCP server built with Python and FastMCP. It exposes a small local
dataset of programming topics through MCP tools and resources, and a small
client or agent uses it to answer a student's questions.

## Project structure

```
mcp-intro/
├── server/
│   ├── learning_server.py   # FastMCP server (tools and resources)
│   └── __init__.py
├── client/
│   ├── mcp_client.py        # Client that connects to the server
│   ├── agent.py             # Agent that uses the server
│   └── __init__.py
├── data/
│   └── topics.json          # Local dataset of programming topics
├── output/
│   └── sample_agent_response.md
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

## MCP Architecture Summary

**MCP (Model Context Protocol)** is a standard way to connect an AI
application to external capabilities. Instead of writing a custom
integration for every tool, a program exposes its capabilities through an
MCP server, and any compatible application can discover and use them.
It works like a universal plug between AI agents and tools.

Example used in this project: an agent wants information about
`Python decorators`, so it asks the learning server.

- **MCP host**: the AI application that manages the whole interaction.
  Here, it is the agent (`client/agent.py`): it receives the student's
  question and decides when to use the server.
- **MCP client**: the connection between the host and one MCP server.
  A host creates one client per server. Here, `client/mcp_client.py`
  connects to the learning server.
- **MCP server**: the program that exposes capabilities. Here,
  `server/learning_server.py` exposes the programming topics.

The server can expose:

- **Tools**: actions that can be called with parameters, like functions.
  Example: search the topics that match `decorators`.
- **Resources**: read-only data that can be consulted but not modified.
  Example: the catalog of available topics.

**Why expose only what is needed?** An agent can make mistakes. The fewer
capabilities a server exposes, the less damage a wrong call can do.
A learning server only needs to read topics: it has no reason to write,
delete or access other files.

### Comparison with my previous project

In my previous project (AI agents with Google ADK), the tools were Python
functions stored inside the project and imported directly by `main.py`:

```text
main.py ── direct import ──► tools/file_writer.py, tools/validation.py
```

Only my own program could use them. With MCP, the tools are still Python
functions, but they live in a separate server. The agent does not import
them: it asks the server through MCP.

```text
agent.py (host) ── client ── MCP ──► learning_server.py (server)
```

| | Previous project | MCP project |
|---|---|---|
| Where are the tools? | Inside the project | In a server |
| How does the agent use them? | Direct import | Request through MCP |
| Who can use them? | Only my program | Any compatible host |

## Setup

FastMCP requires **Python 3.10 or later** (developed with Python 3.12).

```bash
python3 -m venv venv --prompt mcp
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Start the MCP server

```bash
python3 server/learning_server.py
```

The FastMCP banner appears, then the server waits for a client to connect:
this is normal. Stop it with `Ctrl + C`.

## Author

Thomas
