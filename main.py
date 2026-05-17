from app.graph_store import GraphStore
from app.movie_resolver import MovieResolver
from app.tmdb_client import TMDBClient


def load_and_store_movie(selected_movie: dict) -> dict:
    # `selected_movie` comes from search results; fetch the full profile before persistence.
    client = TMDBClient()
    store = GraphStore()

    movie_id = selected_movie["id"]

    print(f"\nFetching full profile for: {selected_movie.get('title')} ({movie_id})")

    movie_profile = client.get_normalized_movie_profile(movie_id)

    try:
        print(f"Saving to Neo4j: {movie_profile['title']}")
        store.save_movie_profile(movie_profile)
    finally:
        # Always close the driver, even when network/database writes fail mid-flow.
        store.close()

    return movie_profile


def main():
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

    print("\nNext step: find graph connections between these movies.")


if __name__ == "__main__":
    main()
