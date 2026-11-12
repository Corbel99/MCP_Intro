# Serveurs MCP en Python

🇬🇧 English version: [README.md](README.md)

## Description

**Programming Learning MCP Server** (serveur MCP d'apprentissage de la
programmation) : un serveur MCP simple, construit avec Python et FastMCP. Il
expose un petit jeu de données local de sujets de programmation, sous forme
d'**outils** et d'une **ressource** MCP. Un client qui se comporte comme un
agent s'y connecte via MCP et l'utilise pour répondre à un étudiant qui veut
étudier un sujet.

```text
mcp-intro/
├── server/
│   ├── learning_server.py   # Serveur FastMCP (outils et ressource)
│   └── __init__.py
├── client/
│   ├── mcp_client.py        # Client de test qui vérifie le serveur
│   ├── agent.py             # Client-agent qui utilise le serveur
│   └── __init__.py
├── data/
│   └── topics.json          # Jeu de données local des sujets
├── output/
│   └── sample_agent_response.md
├── README.md
├── README.fr.md
├── requirements.txt
├── .env.example
└── .gitignore
```

## Résumé de l'architecture MCP

**MCP (Model Context Protocol)** est une façon standard de connecter une
application d'IA à des capacités extérieures. Au lieu d'écrire une
intégration sur mesure pour chaque outil, un programme expose ses capacités
via un serveur MCP, et toute application compatible peut les découvrir et
les utiliser. C'est comme une prise universelle entre les agents d'IA et les
outils.

Exemple utilisé dans ce projet : un agent veut des informations sur
`Python decorators`, il interroge donc le serveur d'apprentissage.

- **Hôte MCP** : l'application d'IA qui gère toute l'interaction et
  **décide** quoi demander. Ici, c'est l'agent (`client/agent.py`).
- **Client MCP** : la connexion entre l'hôte et **un** serveur MCP. Un hôte
  crée un client par serveur. Ici, l'agent utilise le `Client` de FastMCP,
  et `client/mcp_client.py` en utilise un pour tester le serveur.
- **Serveur MCP** : le programme qui expose des capacités. Ici,
  `server/learning_server.py` expose les sujets de programmation.

Le serveur peut exposer :

- **Des outils** : des actions qu'on appelle avec des paramètres, comme des
  fonctions.
- **Des ressources** : des données en lecture seule, qu'on consulte sans les
  modifier.

**Pourquoi n'exposer que le nécessaire ?** Un agent peut se tromper. Moins un
serveur expose de capacités, moins un mauvais appel peut faire de dégâts. Un
serveur d'apprentissage a seulement besoin de lire des sujets : il n'a
aucune raison d'écrire, de supprimer ou d'accéder à d'autres fichiers.

### Comparaison avec mon projet précédent

Dans mon projet précédent (agents IA avec Google ADK), les outils étaient
des fonctions Python rangées dans le projet et importées directement par
`main.py`. Seul mon programme pouvait les utiliser. Avec MCP, les outils sont
toujours des fonctions Python, mais ils vivent dans un serveur séparé, et
l'agent les demande via MCP.

| | Projet précédent | Projet MCP |
|---|---|---|
| Où sont les outils ? | Dans le projet | Dans un serveur |
| Comment l'agent les utilise ? | Import direct | Demande via MCP |
| Qui peut les utiliser ? | Seulement mon programme | Tout hôte compatible |

## Prérequis

- **Python 3.10 ou plus** (exigence de FastMCP ; développé avec Python 3.12)
- **Ubuntu** (développé sous Ubuntu dans WSL, sur Windows)
- **FastMCP**, listé dans `requirements.txt`
- Pas de clé API, pas de compte, pas de modèle de langage : le projet tourne
  entièrement en local. `.env.example` est vide, car le projet n'a besoin
  d'aucune variable de configuration ni d'aucun secret.

## Installation

```bash
python3 -m venv venv --prompt mcp
source venv/bin/activate
pip install -r requirements.txt
```

## Lancer le serveur

```bash
python3 server/learning_server.py
```

La bannière FastMCP s'affiche, puis le serveur attend qu'un client se
connecte : c'est normal. Pour l'arrêter : `Ctrl + C`.

Le serveur utilise le transport **stdio** : il discute avec le client par
l'entrée et la sortie standard. C'est pour ça qu'il n'utilise jamais
`print()`, qui se mélangerait aux messages MCP.

En général, pas besoin de le lancer à la main : le client de test et
l'agent le démarrent eux-mêmes.

## Tester le serveur

```bash
python3 client/mcp_client.py
```

Le client de test démarre lui-même le serveur (transport stdio) et vérifie,
une chose à la fois :

- que le serveur démarre ;
- que les outils et la ressource sont listés ;
- `search_topics` avec une recherche qui trouve et une qui ne trouve rien ;
- `get_topic_details` avec un id valide et un id invalide ;
- que la ressource `topics://catalog` peut être lue.

Sortie raccourcie :

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

## Lancer l'agent

```bash
python3 client/agent.py
```

`client/agent.py` est un **client qui se comporte comme un agent** : du code
déterministe, sans modèle de langage. Il utilise le serveur MCP comme une
capacité extérieure et n'importe jamais directement les fonctions du
serveur.

1. Il demande un sujet (Entrée = `decorators`).
2. Il démarre le serveur et s'y connecte avec le `Client` de FastMCP.
3. Il appelle `search_topics` via MCP, puis `get_topic_details` sur le
   premier résultat.
4. Il écrit une réponse pour l'étudiant et l'enregistre dans
   `output/sample_agent_response.md`.

Si aucun sujet ne correspond, il lit la ressource `topics://catalog` et
affiche la liste des sujets disponibles.

Un agent avec un modèle de langage (par exemple Google ADK avec
`McpToolset`) fonctionnerait aussi. Un client déterministe a été choisi pour
rester concentré sur l'intégration MCP et obtenir le même résultat à chaque
fois.

## Outils disponibles

### `search_topics(query: str)`

Cherche dans le **titre** et les **notions clés** des sujets (sans tenir
compte des majuscules) et renvoie un court résumé de chaque sujet trouvé :
`id`, `title` et `summary`. Renvoie une liste vide si rien ne correspond.

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

Renvoie **toutes les informations** d'un sujet, à partir de son `id` exact :
titre, résumé, prérequis, notions clés, erreurs fréquentes et idée
d'exercice. Si l'id n'existe pas, il renvoie une erreur claire au lieu de
planter :

```json
{"error": "Topic 'sushi' not found. Use search_topics to find a valid id."}
```

Les deux outils travaillent ensemble : `search_topics` trouve les
candidats, puis `get_topic_details` récupère la fiche complète.

## Ressources disponibles

### `topics://catalog`

Une ressource en **lecture seule** qui renvoie le catalogue des sujets
disponibles sous forme de texte JSON, avec seulement l'`id` et le `title` de
chaque sujet :

```json
[
  {"id": "python-decorators", "title": "Python Decorators"},
  {"id": "python-list-comprehensions", "title": "Python List Comprehensions"},
  {"id": "python-virtual-environments", "title": "Python Virtual Environments"},
  {"id": "c-pointers", "title": "C Pointers"},
  {"id": "recursion", "title": "Recursion"}
]
```

Le catalogue ne change jamais et ne prend aucun paramètre : il est donc
exposé comme une ressource plutôt qu'un outil. L'adresse `topics://catalog`
est un nom choisi pour ce serveur, pas une adresse Internet.

## Revue d'un serveur MCP tiers

J'ai examiné le serveur officiel **Filesystem MCP**
(`@modelcontextprotocol/server-filesystem`), l'un des serveurs de référence
du projet MCP. La revue a été faite uniquement à partir de sa
[documentation](https://mcpservers.org/servers/modelcontextprotocol/filesystem) :
je ne l'ai ni installé ni lancé.

| Question | Réponse |
|---|---|
| Que fait-il ? | Donne à une application d'IA l'accès aux fichiers de l'ordinateur : lire, écrire, chercher, lister et déplacer des fichiers et des dossiers. |
| Local ou à distance ? | **Local.** Le client le démarre sur la machine de l'utilisateur, avec `npx` ou Docker. |
| Outils | 13 outils. **Lecture seule :** `read_text_file`, `read_media_file`, `read_multiple_files`, `list_directory`, `list_directory_with_sizes`, `directory_tree`, `search_files`, `get_file_info`, `list_allowed_directories`. **Écriture :** `create_directory`, `write_file`, `edit_file`, `move_file`. |
| Ressources | Aucune mentionnée dans la documentation. |
| Permissions ou identifiants | Aucune clé API ni mot de passe. Il demande une liste de **dossiers autorisés** (arguments de lancement, MCP Roots ou montages Docker). Toutes les opérations sont limitées à ces dossiers. |

**Un risque :** les outils d'écriture peuvent modifier des fichiers.
`write_file` écrase les fichiers existants : un mauvais appel de l'IA (un
modèle peut halluciner) pourrait détruire des données importantes. Plus on
autorise de dossiers, plus les dégâts possibles sont grands.

**Une mesure de sécurité :** n'autoriser qu'**un seul dossier de test**,
jamais le dossier personnel ni tout le disque. Avec Docker, le monter en
**lecture seule** (`ro`) pour que le serveur puisse lire mais rien modifier.
Pour `edit_file`, utiliser d'abord son option `dryRun` pour prévisualiser les
changements.

**Ce que j'ai vérifié avant de l'utiliser :** le README, la liste des outils
et ceux qui peuvent modifier des fichiers, les permissions demandées, et la
façon de limiter les dossiers autorisés.

## Exemple de sortie

En lançant `python3 client/agent.py` puis en appuyant sur Entrée (sujet
`decorators`), on obtient cette réponse, enregistrée dans
`output/sample_agent_response.md` (raccourcie, générée en anglais) :

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

## Limites connues

- **L'agent attend un sujet, pas une phrase complète.** `search_topics`
  vérifie si la recherche apparaît dans un titre ou une notion clé : une
  question entière comme « I want to study Python decorators, what should I
  review first? » ne trouve rien. Taper `decorators` fonctionne.
- **L'agent ne garde que le premier résultat.** Une recherche large comme
  `python` trouve trois sujets, et l'agent prend le premier.
- **Recherche de texte simple.** Pas de synonymes ni de tolérance aux fautes :
  `decorater` ne trouve rien.
- **Petit jeu de données fixe.** Cinq sujets dans un fichier JSON ; ajouter un
  sujet demande de modifier le fichier à la main.
- **Pas de modèle de langage.** La réponse est un modèle fixe rempli avec les
  données du serveur : fiable, mais pas adaptée à la question exacte de
  l'étudiant.
- **Transport stdio local uniquement.** Le serveur n'est pas exposé en HTTP.

### Erreurs rencontrées pendant le projet

- **Le zip du projet a été extrait « à plat »** (sans dossiers, noms avec
  ` (1)`, `.gitignore` perdu). Corrigé en le dézippant à nouveau avec
  `unzip` dans WSL.
- **Des commandes collées ensemble se sont exécutées dans le désordre** :
  `mv` est passé avant `unzip`. Corrigé en lançant les commandes une par une.
- **L'environnement virtuel a été supprimé** avec les mauvais fichiers.
  Corrigé en le recréant.
- **Test du mauvais outil** : un test d'erreur appelait `search_topics` au
  lieu de `get_topic_details`. Chaque outil a son propre nom et ses propres
  paramètres (`query` ou `topic_id`).

## Réflexion

**1. Quel problème MCP résout-il ?**

Sans MCP, chaque agent a besoin d'une intégration sur mesure pour chaque
outil. MCP est un standard, comme une prise universelle : un serveur expose
ses capacités une seule fois, et tout hôte compatible peut s'y brancher et
les découvrir. Dans mon projet précédent, mes outils ne servaient qu'à mon
propre programme ; ici, n'importe quel hôte MCP pourrait utiliser mon
serveur.

**2. Quelle est la différence entre un outil MCP et une ressource MCP ?**

Un outil est une action : une fonction appelée avec des paramètres, comme un
plat qu'on commande au restaurant. Une ressource est un document en lecture
seule, sans paramètre, comme le menu affiché au mur : tout le monde peut le
lire, personne ne le modifie. On appelle un outil par son nom ; on lit une
ressource par son adresse (URI).

**3. Qu'expose mon serveur MCP ?**

Deux outils, `search_topics` (trouver des sujets à partir d'un mot) et
`get_topic_details` (la fiche complète à partir de son id), et une ressource,
`topics://catalog` (la liste des sujets disponibles). La fonction qui lit
`topics.json` n'est pas exposée : elle n'a pas de décorateur, elle reste
interne au serveur.

**4. Comment mon agent utilise-t-il le serveur MCP ?**

Il n'importe jamais les fonctions du serveur. Il démarre le serveur, s'y
connecte avec un client FastMCP, appelle `search_topics` pour trouver le
sujet, puis `get_topic_details` pour obtenir les informations complètes, et
écrit la réponse à partir des données reçues. Si rien ne correspond, il lit
la ressource catalogue.

**5. Que faut-il vérifier avant d'utiliser un serveur MCP tiers ?**

Il faut lire son README et vérifier ce qu'il fait, s'il tourne en local ou à
distance, quels outils peuvent modifier des données, et quelles permissions
ou quels identifiants il demande. Ensuite, on lui donne le moins d'accès
possible : un seul dossier, en lecture seule si possible, et pas
d'identifiants personnels. Si j'ajoute un serveur MCP à un outil d'IA comme
Copilot dans VS Code, c'est moi qui dois faire cette vérification.

**6. Quelle limite ai-je observée dans mon implémentation ?**

Mon agent ne comprend qu'un sujet, pas une question complète : l'étudiant
doit taper `decorators`, pas une phrase. Comprendre une vraie question
demanderait soit un code plus complexe (découper la phrase en mots-clés),
soit un modèle de langage, qui peut appeler les outils tout seul mais qui
est moins prévisible.

## Auteur

Thomas
