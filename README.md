# MCP Servers in Python

🇫🇷 Version française : [README.fr.md](README.fr.md)

## Description

**Programming Learning MCP Server**: a simple MCP server built with Python and
FastMCP. It exposes a small local dataset of programming topics through MCP
**tools** and a **resource**. An agent-like client connects to it through MCP
and uses it to answer a student who wants to study a topic.

```text
mcp-intro/
├── server/
│   ├── learning_server.py   # FastMCP server (tools and resource)
│   └── __init__.py
├── client/
│   ├── mcp_client.py        # Test client that checks the server
│   ├── agent.py             # Agent-like client that uses the server
│   └── __init__.py
├── data/
│   └── topics.json          # Local dataset of programming topics
├── output/
│   └── sample_agent_response.md
├── README.md
├── README.fr.md
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

- **MCP host**: the AI application that manages the whole interaction and
  decides what to ask. Here, it is the agent (`client/agent.py`).
- **MCP client**: the connection between the host and one MCP server.
  A host creates one client per server. Here, the agent uses the FastMCP
  `Client`, and `client/mcp_client.py` uses one to test the server.
- **MCP server**: the program that exposes capabilities. Here,
  `server/learning_server.py` exposes the programming topics.

The server can expose:

- **Tools**: actions that can be called with parameters, like functions.
- **Resources**: read-only data that can be consulted but not modified.

**Why expose only what is needed?** An agent can make mistakes. The fewer
capabilities a server exposes, the less damage a wrong call can do.
A learning server only needs to read topics: it has no reason to write,
delete or access other files.

### Comparison with my previous project

In my previous project (AI agents with Google ADK), the tools were Python
functions stored inside the project and imported directly by `main.py`.
Only my own program could use them. With MCP, the tools are still Python
functions, but they live in a separate server, and the agent asks for them
through MCP.

| | Previous project | MCP project |
|---|---|---|
| Where are the tools? | Inside the project | In a server |
| How does the agent use them? | Direct import | Request through MCP |
| Who can use them? | Only my program | Any compatible host |

## Requirements

- **Python 3.10 or later** (FastMCP requirement; developed with Python 3.12)
- **Ubuntu** (developed on Ubuntu under WSL, Windows)
- **FastMCP**, listed in `requirements.txt`
- No API key, no account, no language model: the project runs fully locally.
  `.env.example` is empty because the project needs no configuration
  variable and no secret.

## Setup

```bash
python3 -m venv venv --prompt mcp
source venv/bin/activate
pip install -r requirements.txt
```

## How to Run the Server

```bash
python3 server/learning_server.py
```

The FastMCP banner appears, then the server waits for a client to connect:
this is normal. Stop it with `Ctrl + C`.

The server uses the **stdio** transport: it talks with the client through
standard input and output. For this reason, the server never uses `print()`,
which would mix with the MCP messages.

You usually do not need to start it by hand: the test client and the agent
start it themselves.

## How to Test the Server

```bash
python3 client/mcp_client.py
```

The test client starts the server itself (stdio transport) and checks, one
at a time:

- the server starts;
- the tools and the resource are listed;
- `search_topics` with a matching query and a query with no match;
- `get_topic_details` with a valid id and an invalid id;
- the `topics://catalog` resource can be read.

Shortened output:

```text
== Tools ==
- search_topics
- get_topic_details

== Resources ==
- topics://catalog

== search_topics('sushi') ==
[]

== get_topic_details('sushi') ==
{'error': "Topic 'sushi' not found. Use search_topics to find a valid id."}
```

## How to Run the Agent

```bash
python3 client/agent.py
```

`client/agent.py` is an **agent-like client**: deterministic code, without a
language model. It uses the MCP server as an external capability and never
imports the server functions directly.

1. It asks for a topic (press Enter to use `decorators`).
2. It starts the server and connects to it with the FastMCP `Client`.
3. It calls `search_topics` through MCP, then `get_topic_details` on the
   first result.
4. It writes a student-facing answer and saves it in
   `output/sample_agent_response.md`.

If no topic matches, it reads the `topics://catalog` resource and lists the
available topics.

An LLM-based agent (for example Google ADK with `McpToolset`) would also
work. A deterministic client was chosen to keep the focus on the MCP
integration and to get the same result every time.

## Available Tools

### `search_topics(query: str)`

Searches the topics by **title** and **key concepts** (case-insensitive) and
returns a short summary of each matching topic: `id`, `title` and `summary`.
Returns an empty list if nothing matches.

```json
[
  {
    "id": "python-decorators",
    "title": "Python Decorators",
    "summary": "A decorator is a function that wraps another function to add behavior without changing its code. It is applied with the @decorator syntax."
  }
]
```

### `get_topic_details(topic_id: str)`

Returns the **full information** for one topic, using its exact `id`:
title, summary, prerequisites, key concepts, common mistakes and practice
idea. If the id does not exist, it returns a clear error instead of
crashing:

```json
{"error": "Topic 'sushi' not found. Use search_topics to find a valid id."}
```

The two tools work together: `search_topics` finds the candidates, then
`get_topic_details` retrieves the full topic.

## Available Resources

### `topics://catalog`

A **read-only** resource that returns the catalog of available topics as a
JSON string, with only the `id` and `title` of each topic:

```json
[
  {"id": "python-decorators", "title": "Python Decorators"},
  {"id": "python-list-comprehensions", "title": "Python List Comprehensions"},
  {"id": "python-virtual-environments", "title": "Python Virtual Environments"},
  {"id": "c-pointers", "title": "C Pointers"},
  {"id": "recursion", "title": "Recursion"}
]
```

The catalog never changes and takes no parameter, so it is exposed as a
resource rather than a tool. The URI `topics://catalog` is a name chosen for
this server, not an Internet address.

## Third-Party MCP Server Review

I reviewed the official **Filesystem MCP server**
(`@modelcontextprotocol/server-filesystem`), one of the reference servers of
the MCP project. The review was done through its
[documentation](https://mcpservers.org/servers/modelcontextprotocol/filesystem)
only: I did not install or run it.

| Question | Answer |
|---|---|
| What does it do? | Gives an AI application access to files on the computer: read, write, search, list and move files and directories. |
| Local or remote? | **Local.** The client starts it on the user's machine with `npx` or Docker. |
| Tools | 13 tools. **Read-only:** `read_text_file`, `read_media_file`, `read_multiple_files`, `list_directory`, `list_directory_with_sizes`, `directory_tree`, `search_files`, `get_file_info`, `list_allowed_directories`. **Write:** `create_directory`, `write_file`, `edit_file`, `move_file`. |
| Resources | None mentioned in the documentation. |
| Permissions or credentials | No API key or password. It requires a list of **allowed directories** (command-line arguments, MCP Roots, or Docker mounts). All operations are restricted to these directories. |

**One risk:** the write tools can change files. `write_file` overwrites
existing files, so a wrong call from the AI (a model can hallucinate) could
destroy important data. The more directories are allowed, the bigger the
possible damage.

**One safety measure:** allow only **one dedicated test directory**, never the
home directory or the whole disk. With Docker, mount it **read-only** (`ro`)
so the server can read but not modify anything. For `edit_file`, use its
`dryRun` option first to preview the changes.

**What I checked before using it:** the README, the list of tools and which
ones can modify files, the required permissions, and how to limit the
allowed directories.

## Example Output

Running `python3 client/agent.py` and pressing Enter (topic `decorators`)
produces this answer, saved in `output/sample_agent_response.md`
(shortened):

```markdown
# Study Recommendation

**Student request:** decorators

## Recommended topic: Python Decorators

### Why this topic is relevant

A decorator is a function that wraps another function to add behavior
without changing its code. It is applied with the @decorator syntax.

### Review these prerequisites first

- Functions
- Scope
- Functions as arguments

### Practice idea

Create a decorator that prints a message before and after a function call.

...
```

## Known Limitations

- **The agent expects a topic, not a full sentence.** `search_topics` checks
  if the query appears in a title or key concept: a whole question such as
  "I want to study Python decorators, what should I review first?" matches
  nothing. Typing `decorators` works.
- **The agent keeps only the first result.** A broad query such as `python`
  matches three topics, and the agent picks the first one.
- **Simple text search.** No synonyms or typo tolerance: `decorater` finds
  nothing.
- **Small static dataset.** Five topics in a JSON file; adding a topic means
  editing the file by hand.
- **No language model.** The answer is a fixed template filled with the
  server data: reliable, but not adapted to the student's exact question.
- **Local stdio transport only.** The server is not exposed over HTTP.

### Errors encountered during the project

- **The project zip was extracted as flat files** (no folders, names with
  ` (1)`, `.gitignore` lost). Fixed by extracting it again with `unzip` in
  WSL.
- **Commands pasted together ran in the wrong order**: `mv` ran before
  `unzip`. Fixed by running the commands one at a time.
- **The virtual environment was deleted** with the wrong files. Fixed by
  creating it again.
- **Testing the wrong tool**: an error test called `search_topics` instead
  of `get_topic_details`. Each tool has its own name and parameters
  (`query` vs `topic_id`).

## Reflection

**1. What problem does MCP solve?**

Without MCP, every agent needs a custom integration for every tool. MCP is a
standard, like a universal plug: a server exposes its capabilities once, and
any compatible host can connect to it and discover them. In my previous
project, my tools could only be used by my own program; here, any MCP host
could use my server.

**2. What is the difference between an MCP tool and an MCP resource?**

A tool is an action: a function called with parameters, like ordering a dish
in a restaurant. A resource is a read-only document, without parameters,
like the menu on the wall: everyone can read it, nobody changes it. Tools are
called by name; resources are read by their address (URI).

**3. What does my MCP server expose?**

Two tools, `search_topics` (find topics from a word) and `get_topic_details`
(the full topic from its id), and one resource, `topics://catalog` (the list
of available topics). The function that reads `topics.json` is not exposed:
it has no decorator, so it stays internal to the server.

**4. How does my agent use the MCP server?**

It never imports the server functions. It starts the server, connects with a
FastMCP client, calls `search_topics` to find the topic, then
`get_topic_details` to get the full information, and writes the answer from
the returned data. If nothing matches, it reads the catalog resource.

**5. What should I check before using a third-party MCP server?**

I should read its README and check what it does, whether it runs locally or
remotely, which tools can modify data, and which permissions or credentials
it asks for. Then I give it the smallest access possible: one directory,
read-only if I can, and no personal credentials. If I add an MCP server to
an AI tool like Copilot in VS Code, I am the one who has to do this review.

**6. What limitation did I observe in my implementation?**

My agent only understands a topic, not a full question: the student must
type `decorators`, not a sentence. Understanding a full question would need
either more complex code (splitting the sentence into keywords) or a
language model, which can call the tools by itself but is less predictable.

## Author

Thomas
