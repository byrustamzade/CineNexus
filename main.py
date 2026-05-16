import sys

from app.tmdb_client import TMDBClient


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
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
