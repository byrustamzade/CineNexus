# CineNexus

CineNexus is a Python CLI project that combines TMDB metadata, Neo4j graph modeling, and an Ollama-hosted LLM to explain relationships between two movies.

It builds a knowledge graph from movie profiles (directors, actors, genres, keywords, release year), computes shared graph signals, and produces a concise AI explanation grounded in graph output.

## Features

- Interactive movie search and selection (TMDB)
- Graph ingestion into Neo4j with idempotent `MERGE` writes
- Multi-signal connection analysis:
  - shared directors
  - shared actors
  - shared genres
  - shared keywords
  - shared release years
  - shortest graph path
- LLM explanation with explicit grounding prompt rules

## Architecture

```text
User (CLI)
  -> MovieResolver
      -> TMDBClient (search + full profile)
      -> GraphStore (Neo4j write)
  -> ConnectionFinder (Neo4j read/query)
  -> AIExplainer
      -> OllamaClient (local model inference)
```

## Tech Stack

- Python 3.10+
- Neo4j (graph database)
- TMDB API
- Ollama (local LLM serving)
- Requests, python-dotenv

## Project Structure

```text
CineNexus/
  app/
    ai_explainer.py
    connection_finder.py
    graph_store.py
    movie_resolver.py
    neo4j_connection.py
    ollama_client.py
    settings.py
    tmdb_client.py
  tests/
  .github/workflows/ci.yml
  main.py
  requirements.txt
  requirements-dev.txt
```

## Quick Start

### 1. Clone and set up environment

```bash
git clone <your-repo-url>
cd CineNexus
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
```

### 2. Configure environment variables

Create `.env` from `.env.example` and fill values:

```bash
cp .env.example .env
```

Required:

- `TMDB_API_KEY` (TMDB API Read Access Token / Bearer token)
- `NEO4J_URI` (for example `bolt://localhost:7687`)
- `NEO4J_USERNAME`
- `NEO4J_PASSWORD`

Optional:

- `OLLAMA_MODEL` (default: `qwen2.5:3b`)

### 3. Start services

- Run Neo4j locally and ensure credentials match your `.env`.
- Run Ollama locally:

```bash
ollama serve
ollama pull qwen2.5:3b
```

### 4. Run CineNexus

```bash
python main.py
```

## Development Commands

Run lint:

```bash
ruff check .
```

Run formatter check:

```bash
black --check .
```

Run tests:

```bash
pytest
```

## Example Output (Abbreviated)

```text
Selected movies:
1. Inception (2010)
2. Interstellar (2014)

Graph connections:
Shared directors:
['Christopher Nolan']
...

AI explanation:
- Both films share the same director...
```

## Known Limitations

- Relies on external services (TMDB, Neo4j, Ollama), so local setup is required.
- Connection quality depends on available TMDB metadata.
- LLM output quality depends on selected local model.

## Roadmap

- Non-interactive CLI flags (`--movie-a`, `--movie-b`)
- Docker Compose for one-command local environment
- Graph schema bootstrap with explicit indexes/constraints
- Expanded test suite (integration tests with mocked services)

## TMDB Attribution

This product uses TMDB and the TMDB APIs but is not endorsed, certified, or otherwise approved by TMDB.

Reference:
- https://developer.themoviedb.org/docs/faq
- https://www.themoviedb.org/api-terms-of-use
