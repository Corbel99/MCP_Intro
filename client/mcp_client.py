#!/usr/bin/env python3
#!/usr/bin/env python3
"""Test client for the Programming Learning MCP server."""
import asyncio
from pathlib import Path

from fastmcp import Client

# Chemin vers le fichier du serveur, calculé à partir de ce fichier
SERVER_FILE = Path(__file__).resolve().parent.parent / "server" / "learning_server.py"


async def main():
    """Run every check on the MCP server, one at a time."""
    # Le client lance lui-même le serveur et s'y connecte (transport stdio)
    client = Client(str(SERVER_FILE))

    async with client:
        # 1. Les outils sont-ils listés ?
        print("== Tools ==")
        tools = await client.list_tools()
        for tool in tools:
            print("-", tool.name)

        # 2. La ressource est-elle listée ?
        print("\n== Resources ==")
        resources = await client.list_resources()
        for resource in resources:
            print("-", resource.uri)

        # 3. search_topics : une recherche qui trouve, une qui ne trouve rien
        print("\n== search_topics('decorator') ==")
        result = await client.call_tool("search_topics", {"query": "decorator"})
        print(result.data)

        print("\n== search_topics('sushi') ==")
        result = await client.call_tool("search_topics", {"query": "sushi"})
        print(result.data)

        # 4. get_topic_details : un id valide, un id invalide
        print("\n== get_topic_details('python-decorators') ==")
        result = await client.call_tool(
            "get_topic_details", {"topic_id": "python-decorators"}
        )
        print(result.data)

        print("\n== get_topic_details('sushi') ==")
        result = await client.call_tool("get_topic_details", {"topic_id": "sushi"})
        print(result.data)

        # 5. La ressource catalogue peut-elle être lue ?
        print("\n== topics://catalog ==")
        catalog = await client.read_resource("topics://catalog")
        print(catalog[0].text)


if __name__ == "__main__":
    asyncio.run(main())
