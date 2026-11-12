#!/usr/bin/env python3
"""Agent-like client that answers a student using the learning MCP server."""
import asyncio
import json
from pathlib import Path

from fastmcp import Client

# Chemins calculés à partir de ce fichier
ROOT = Path(__file__).resolve().parent.parent
SERVER_FILE = ROOT / "server" / "learning_server.py"
OUTPUT_FILE = ROOT / "output" / "sample_agent_response.md"

# Sujet utilisé si l'étudiant appuie juste sur Entrée
DEFAULT_TOPIC = "decorators"


def bullet_list(items: list[str]) -> str:
    """Turn a list of strings into a Markdown bullet list."""
    # Exemple : ["Functions", "Scope"] devient le texte :
    # - Functions
    # - Scope
    lines = []
    for item in items:
        # On ajoute un tiret devant chaque élément
        lines.append(f"- {item}")
    # On recolle les lignes en un seul texte, avec un retour à la ligne entre chacune
    return "\n".join(lines)


def build_answer(request: str, topic: dict) -> str:
    """Write the student-facing answer from the MCP topic data."""
    # C'est une "lettre à trous" : le texte est fixe, et les {...} sont
    # remplis avec la fiche renvoyée par le serveur MCP.
    # Chaque partie = 2 lignes : un titre, puis son contenu.
    # Les \n\n ajoutent une ligne vide entre les parties.
    return (
        # Le grand titre et la demande de l'étudiant
        "# Study Recommendation\n\n"
        f"**Student request:** {request}\n\n"
        # 1. Le sujet recommandé
        f"## Recommended topic: {topic['title']}\n\n"
        # 2. Pourquoi ce sujet est pertinent (son résumé)
        "### Why this topic is relevant\n\n"
        f"{topic['summary']}\n\n"
        # 3. Les prérequis, en liste à puces
        "### Review these prerequisites first\n\n"
        f"{bullet_list(topic['prerequisites'])}\n\n"
        # 4. Les notions clés, en liste à puces
        "### Key concepts\n\n"
        f"{bullet_list(topic['key_concepts'])}\n\n"
        # 5. L'idée d'exercice
        "### Practice idea\n\n"
        f"{topic['practice_idea']}\n\n"
        # 6. Les erreurs fréquentes, en liste à puces
        "### Common mistakes to avoid\n\n"
        f"{bullet_list(topic['common_mistakes'])}\n\n"
        # La source : on montre que les données viennent du serveur MCP
        "_Source: Programming Learning MCP Server "
        "(`search_topics`, `get_topic_details`)._\n"
    )


def build_not_found_answer(request: str, catalog: list[dict]) -> str:
    """Write a clear answer when no topic matches the request."""
    # On récupère seulement les titres des sujets du catalogue
    titles = []
    for topic in catalog:
        titles.append(topic["title"])
    # Même principe de lettre à trous, en plus court
    return (
        "# Study Recommendation\n\n"
        f"**Student request:** {request}\n\n"
        # On dit clairement qu'aucun sujet ne correspond...
        "No matching topic was found on the learning server.\n\n"
        # ...et on propose la liste des sujets disponibles
        "Available topics:\n\n"
        f"{bullet_list(titles)}\n"
    )


async def main():
    """Receive a topic, use the MCP server, and write an answer."""
    # Étape 1 : on reçoit le sujet que l'étudiant veut étudier
    request = input("Which topic do you want to study? ").strip()
    if not request:
        request = DEFAULT_TOPIC

    # Le client MCP lance le serveur et s'y connecte (transport stdio)
    client = Client(str(SERVER_FILE))
    async with client:
        # Étape 2 : on cherche le sujet avec search_topics (via MCP)
        print("[1/3] Searching topics with search_topics...")
        result = await client.call_tool("search_topics", {"query": request})
        matches = result.data

        if not matches:
            # Aucun sujet : on lit le catalogue pour proposer les sujets existants
            resource = await client.read_resource("topics://catalog")
            catalog = json.loads(resource[0].text)
            answer = build_not_found_answer(request, catalog)
        else:
            # Étape 3 : on récupère la fiche complète du premier résultat
            topic_id = matches[0]["id"]
            print(f"[2/3] Getting details for '{topic_id}'...")
            result = await client.call_tool(
                "get_topic_details", {"topic_id": topic_id}
            )
            answer = build_answer(request, result.data)

    # Étape 4 : on affiche la réponse et on l'enregistre
    print("[3/3] Writing the answer...\n")
    print(answer)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(answer, encoding="utf-8")
    print(f"Answer saved to {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    asyncio.run(main())
