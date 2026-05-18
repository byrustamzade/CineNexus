from app.connection_finder import ConnectionFinder


class _FakeResult:
    def __init__(self, record: dict | None):
        self._record = record

    def single(self) -> dict | None:
        return self._record


class _FakeSession:
    def __init__(self, connection: "_FakeConnection"):
        self._connection = connection

    def __enter__(self) -> "_FakeSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def run(self, query: str, **params: int) -> _FakeResult:
        self._connection.calls.append({"query": query, "params": params})
        record = self._connection.record_for_query(query, params)
        return _FakeResult(record)


class _FakeConnection:
    def __init__(self, record_for_query):
        self.record_for_query = record_for_query
        self.calls: list[dict] = []
        self.closed = False

    def session(self) -> _FakeSession:
        return _FakeSession(self)

    def close(self) -> None:
        self.closed = True


def _build_finder(record_for_query):
    finder = object.__new__(ConnectionFinder)
    fake_connection = _FakeConnection(record_for_query)
    finder.connection = fake_connection
    return finder, fake_connection


def test_find_between_movies_maps_results_to_expected_shape() -> None:
    def record_for_query(query: str, params: dict) -> dict | None:
        if "RETURN m.title AS title" in query:
            titles = {1: "Inception", 2: "Interstellar"}
            return {"title": titles[params["tmdb_id"]]}
        if "DIRECTED_BY" in query:
            return {"names": ["Christopher Nolan"]}
        if "ACTED_IN" in query:
            return {"names": ["Michael Caine"]}
        if "HAS_GENRE" in query:
            return {"values": ["Science Fiction"]}
        if "HAS_KEYWORD" in query:
            return {"values": ["dream"]}
        if "RELEASED_IN" in query:
            return {"values": [2010]}
        if "shortestPath" in query:
            return {
                "path": [
                    "Movie:Inception",
                    "Person:Christopher Nolan",
                    "Movie:Interstellar",
                ]
            }
        raise AssertionError(f"Unexpected query: {query}")

    finder, fake_connection = _build_finder(record_for_query)
    result = finder.find_between_movies(1, 2)

    assert result == {
        "first_title": "Inception",
        "second_title": "Interstellar",
        "shared_directors": ["Christopher Nolan"],
        "shared_actors": ["Michael Caine"],
        "shared_genres": ["Science Fiction"],
        "shared_keywords": ["dream"],
        "shared_years": [2010],
        "shortest_path": [
            "Movie:Inception",
            "Person:Christopher Nolan",
            "Movie:Interstellar",
        ],
    }
    assert len(fake_connection.calls) == 8
    assert fake_connection.calls[0]["params"] == {"tmdb_id": 1}
    assert fake_connection.calls[1]["params"] == {"tmdb_id": 2}


def test_find_between_movies_returns_empty_lists_and_none_when_no_records() -> None:
    finder, fake_connection = _build_finder(lambda _query, _params: None)
    result = finder.find_between_movies(1, 2)

    assert result == {
        "first_title": None,
        "second_title": None,
        "shared_directors": [],
        "shared_actors": [],
        "shared_genres": [],
        "shared_keywords": [],
        "shared_years": [],
        "shortest_path": [],
    }
    assert len(fake_connection.calls) == 8


def test_close_delegates_to_connection_close() -> None:
    finder, fake_connection = _build_finder(lambda _query, _params: None)

    finder.close()

    assert fake_connection.closed is True
