import requests

from app.settings import TMDB_API_KEY


class TMDBClient:
    """HTTP client for TMDB search and movie profile retrieval."""

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self):
        if not TMDB_API_KEY:
            raise ValueError("TMDB_API_KEY is missing. Add it to your .env file.")

        self.headers = {
            "Authorization": f"Bearer {TMDB_API_KEY}",
            "accept": "application/json",
        }

    def search_movies(self, query: str, page: int = 1) -> list[dict]:
        """Search TMDB movies by free-text title."""
        response = requests.get(
            f"{self.BASE_URL}/search/movie",
            headers=self.headers,
            params={
                "query": query,
                "page": page,
                "include_adult": False,
                "language": "en-US",
            },
            timeout=20,
        )

        response.raise_for_status()

        data = response.json()

        return data.get("results", [])

    def get_movie_full_profile(self, movie_id: int) -> dict:
        """Fetch full movie payload, including credits and keywords."""
        response = requests.get(
            f"{self.BASE_URL}/movie/{movie_id}",
            headers=self.headers,
            params={
                "append_to_response": "credits,keywords",
                "language": "en-US",
            },
            timeout=20,
        )

        response.raise_for_status()
        return response.json()

    def normalize_movie_profile(self, raw: dict) -> dict:
        """Map TMDB payload into the graph schema expected by GraphStore."""
        # TMDB stores directors in the crew list; filter by job for stable mapping.
        directors = [
            person
            for person in raw.get("credits", {}).get("crew", [])
            if person.get("job") == "Director"
        ]

        # Limit cast size to keep graph writes and queries predictable per movie.
        top_cast = raw.get("credits", {}).get("cast", [])[:10]

        return {
            "tmdb_id": raw.get("id"),
            "title": raw.get("title"),
            "original_title": raw.get("original_title"),
            "overview": raw.get("overview"),
            "release_date": raw.get("release_date"),
            "year": (raw.get("release_date") or "")[:4],
            "runtime": raw.get("runtime"),
            "genres": [
                {
                    "id": genre.get("id"),
                    "name": genre.get("name"),
                }
                for genre in raw.get("genres", [])
            ],
            "directors": [
                {
                    "id": person.get("id"),
                    "name": person.get("name"),
                }
                for person in directors
            ],
            "cast": [
                {
                    "id": person.get("id"),
                    "name": person.get("name"),
                    "character": person.get("character"),
                    "order": person.get("order"),
                }
                for person in top_cast
            ],
            "keywords": [
                {
                    "id": keyword.get("id"),
                    "name": keyword.get("name"),
                }
                for keyword in raw.get("keywords", {}).get("keywords", [])
            ],
        }

    def get_normalized_movie_profile(self, movie_id: int) -> dict:
        """Fetch and normalize a movie profile in one call."""
        raw = self.get_movie_full_profile(movie_id)
        return self.normalize_movie_profile(raw)
