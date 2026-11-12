#!/usr/bin/env python3
"""Programming Learning MCP server built with FastMCP."""
from fastmcp import FastMCP

# On crée le serveur MCP en lui donnant un nom clair
mcp = FastMCP("Programming Learning Server")


# Point d'entrée : on lance le serveur seulement si on exécute ce fichier
if __name__ == "__main__":
    mcp.run()
