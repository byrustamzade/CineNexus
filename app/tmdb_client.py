import requests

from app.settings import TMDB_API_KEY


class TMDBClient:
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self):
        if not TMDB_API_KEY:
            raise ValueError("TMDB_API_KEY is missing. Add it to your .env file.")

        self.headers = {
            "Authorization": f"Bearer {TMDB_API_KEY}",
            "accept": "application/json",
        }

    def search_movies(self, query: str, page: int = 1) -> list[dict]:
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