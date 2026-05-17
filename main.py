import sys

from app.tmdb_client import TMDBClient
from app.graph_store import GraphStore


def search_movie(title: str):
    client = TMDBClient()
    results = client.search_movies(title)

    if not results:
        print("No movies found.")
        return

    print(f"\nResults for: {title}")
    print("=" * 100)

    for index, movie in enumerate(results[:10], start=1):
        title = movie.get("title")
        original_title = movie.get("original_title")
        release_date = movie.get("release_date") or "Unknown"
        movie_id = movie.get("id")

        print(f"{index}. {title} ({release_date[:4]})")
        print(f"   TMDB ID: {movie_id}")
        print(f"   Original title: {original_title}")
        print("-" * 100)


def show_movie_profile(movie_id: int):
    client = TMDBClient()
    movie = client.get_normalized_movie_profile(movie_id)

    print(f"\n{movie['title']} ({movie['year']})")
    print("=" * 80)
    print(f"TMDB ID: {movie['tmdb_id']}")
    print(f"Original title: {movie['original_title']}")
    print(f"Runtime: {movie['runtime']} min")
    print(f"Overview: {movie['overview']}")
    print()

    print("Directors:")
    for director in movie["directors"]:
        print(f"- {director['name']}")

    print("\nGenres:")
    for genre in movie["genres"]:
        print(f"- {genre['name']}")

    print("\nTop Cast:")
    for cast in movie["cast"]:
        print(f"- {cast['name']} as {cast['character']}")

    print("\nKeywords:")
    for keyword in movie["keywords"][:15]:
        print(f"- {keyword['name']}")


def select_movie_by_title(title: str) -> dict | None:
    client = TMDBClient()
    results = client.search_movies(title)

    if not results:
        print(f"No movies found for: {title}")
        return None

    top_results = results[:10]

    print(f"\nSelect movie for: {title}")
    print("=" * 80)

    for index, movie in enumerate(top_results, start=1):
        movie_title = movie.get("title")
        original_title = movie.get("original_title")
        release_date = movie.get("release_date") or "Unknown"
        movie_id = movie.get("id")
        overview = (movie.get("overview") or "").replace("\n", " ")

        print(f"{index}. {movie_title} ({release_date[:4]})")
        print(f"   TMDB ID: {movie_id}")
        print(f"   Original title: {original_title}")
        print(f"   Overview: {overview[:180]}...")
        print("-" * 80)

    choice = input("Choose movie number (or press Enter to cancel): ").strip()

    if not choice:
        print("Cancelled.")
        return None

    if not choice.isdigit():
        print("Invalid choice.")
        return None

    choice_index = int(choice)

    if choice_index < 1 or choice_index > len(top_results):
        print("Choice out of range.")
        return None

    return top_results[choice_index - 1]


def ingest_movie_by_title(title: str):
    selected = select_movie_by_title(title)

    if not selected:
        return

    movie_id = selected["id"]

    client = TMDBClient()

    print(f"\nFetching movie profile: {selected['title']} ({movie_id})")
    movie = client.get_normalized_movie_profile(movie_id)

    store = GraphStore()

    try:
        print(f"Saving to Neo4j: {movie['title']}")
        store.save_movie_profile(movie)
        print("Movie saved to graph.")
    finally:
        store.close()


def main():
    if len(sys.argv) < 3:
        print('Usage: python main.py search "Batman"')
        return

    command = sys.argv[1]

    if command == "search":
        title = " ".join(sys.argv[2:])
        search_movie(title)
    elif command == "profile":
        if len(sys.argv) < 3:
            print("Usage: python main.py profile <tmdb_id>")
            return

        show_movie_profile(int(sys.argv[2]))

    elif command == "ingest":

        if len(sys.argv) < 3:
            print('Usage: python main.py ingest "Batman"')
            return

        title = " ".join(sys.argv[2:])
        ingest_movie_by_title(title)

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
