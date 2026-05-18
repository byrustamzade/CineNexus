from app.ai_explainer import AIExplainer
from app.connection_finder import ConnectionFinder
from app.graph_store import GraphStore
from app.movie_resolver import MovieResolver
from app.tmdb_client import TMDBClient


def load_and_store_movie(selected_movie: dict) -> dict:
    """Fetch selected movie details from TMDB and persist them to Neo4j."""
    # Resolve the selected search result to a full TMDB profile before saving.
    client = TMDBClient()
    store = GraphStore()

    movie_id = selected_movie["id"]

    print(f"\nFetching full profile for: {selected_movie.get('title')} ({movie_id})")

    movie_profile = client.get_normalized_movie_profile(movie_id)

    try:
        print(f"Saving to Neo4j: {movie_profile['title']}")
        store.save_movie_profile(movie_profile)
        print("Movie saved.")
    finally:
        # Ensure the Neo4j driver is closed even if persistence fails.
        store.close()

    return movie_profile


def print_connections(connections: dict) -> None:
    """Render connection results in a readable CLI format."""
    print("\nGraph connections:")
    print("=" * 80)

    if not connections:
        print("No connections found.")
        return

    print("Shared directors:")
    print(connections.get("shared_directors") or "None")

    print("\nShared actors:")
    print(connections.get("shared_actors") or "None")

    print("\nShared genres:")
    print(connections.get("shared_genres") or "None")

    print("\nShared keywords:")
    print(connections.get("shared_keywords") or "None")

    print("\nShared release years:")
    print(connections.get("shared_years") or "None")

    shortest_path = connections.get("shortest_path") or []

    print("\nShortest path:")
    print(" -> ".join(shortest_path) if shortest_path else "None")


def main():
    """Run the interactive CineNexus workflow end-to-end."""
    print("\nCineNexus")
    print("=" * 80)
    print("Discover graph-based connections between two movies.")
    print("=" * 80)

    resolver = MovieResolver()

    first_selected = resolver.resolve("first")

    if not first_selected:
        print("Cancelled.")
        return

    first_movie = load_and_store_movie(first_selected)

    second_selected = resolver.resolve("second")

    if not second_selected:
        print("Cancelled.")
        return

    second_movie = load_and_store_movie(second_selected)

    print("\nSelected movies:")
    print("=" * 80)
    print(f"1. {first_movie['title']} ({first_movie['year']})")
    print(f"2. {second_movie['title']} ({second_movie['year']})")

    finder = ConnectionFinder()

    try:
        connections = finder.find_between_movies(
            first_movie["tmdb_id"],
            second_movie["tmdb_id"],
        )
    finally:
        finder.close()

    print_connections(connections)

    explainer = AIExplainer()
    explanation = explainer.explain(connections)

    print("\nAI explanation:")
    print("=" * 80)
    print(explanation)


if __name__ == "__main__":
    main()
