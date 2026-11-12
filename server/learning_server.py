#!/usr/bin/env python3
"""Programming Learning MCP server built with FastMCP."""
import json
from pathlib import Path

from fastmcp import FastMCP

# Chemin vers data/topics.json, calculé à partir de l'emplacement de ce fichier
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "topics.json"

# On crée le serveur MCP en lui donnant un nom clair
mcp = FastMCP("Programming Learning Server")


def load_topics() -> list[dict]:
    """Load all topics from data/topics.json."""
    # On ouvre le garde-manger et on lit tous les sujets
    with DATA_FILE.open(encoding="utf-8") as file:
        return json.load(file)


@mcp.tool
def search_topics(query: str) -> list[dict]:
    """Search programming topics by title or key concept.

    Return a short summary of each matching topic,
    or an empty list if nothing matches.
    """
    # On met la recherche en minuscules pour ignorer les majuscules
    text = query.strip().lower()

    # Recherche vide : aucun résultat
    if not text:
        return []

    results = []
    for topic in load_topics():
        # On cherche dans le titre et dans les notions clés
        searchable = [topic["title"]] + topic["key_concepts"]

        # On regarde si la recherche apparaît dans au moins un de ces textes
        found = False
        for item in searchable:
            if text in item.lower():
                found = True

        # Si oui, on renvoie un petit résumé, pas toute la fiche
        if found:
            results.append({
                "id": topic["id"],
                "title": topic["title"],
                "summary": topic["summary"],
            })

    return results


# Point d'entrée : on lance le serveur seulement si on exécute ce fichier
if __name__ == "__main__":
    mcp.run()
