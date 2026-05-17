from app.tmdb_client import TMDBClient


class MovieResolver:
    def __init__(self):
        self.client = TMDBClient()

    def resolve(self, label: str) -> dict | None:
        while True:
            query = input(f"\nEnter {label} movie name: ").strip()

            if not query:
                print("Movie name cannot be empty.")
                continue

            results = self.client.search_movies(query)

            if not results:
                print("No movies found. Try another name.")
                continue

            selected = self._select_from_results(query, results)

            if selected:
                return selected

    def _select_from_results(self, query: str, results: list[dict]) -> dict | None:
        # Keep the CLI list short enough to scan while preserving top relevance ordering.
        filtered_results = results[:10]

        while True:
            self._print_results(query, filtered_results)

            print("\nOptions:")
            print("  number  - select movie")
            print("  y       - filter by year")
            print("  r       - search again")
            print("  q       - cancel")

            choice = input("Choose option: ").strip().lower()

            if choice == "q":
                return None

            if choice == "r":
                return None

            if choice == "y":
                year = input("Enter release year: ").strip()
                filtered_results = self._filter_by_year(results, year)

                if not filtered_results:
                    print(f"No results found for year: {year}")
                    # Fall back to the original shortlist so the user can continue selection.
                    filtered_results = results[:10]

                continue

            if choice.isdigit():
                index = int(choice)

                if 1 <= index <= len(filtered_results):
                    return filtered_results[index - 1]

                print("Invalid number.")
                continue

            print("Invalid option.")

    def _print_results(self, query: str, results: list[dict]) -> None:
        print(f"\nResults for: {query}")
        print("=" * 80)

        for index, movie in enumerate(results, start=1):
            title = movie.get("title") or "Unknown"
            original_title = movie.get("original_title") or "Unknown"
            release_date = movie.get("release_date") or "Unknown"
            movie_id = movie.get("id")
            overview = (movie.get("overview") or "").replace("\n", " ")

            print(f"{index}. {title} ({release_date[:4]})")
            print(f"   TMDB ID: {movie_id}")
            print(f"   Original title: {original_title}")
            print(f"   Overview: {overview[:180]}...")
            print("-" * 80)

    def _filter_by_year(self, results: list[dict], year: str) -> list[dict]:
        if not year.isdigit():
            print("Year must be numeric.")
            return []

        return [
            movie for movie in results
            if (movie.get("release_date") or "").startswith(year)
        ][:10]
