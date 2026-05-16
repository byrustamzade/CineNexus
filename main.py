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


def main():
    if len(sys.argv) < 3:
        print('Usage: python main.py search "Batman"')
        return

    command = sys.argv[1]

    if command == "search":
        title = " ".join(sys.argv[2:])
        search_movie(title)
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()