from app.tmdb_client import TMDBClient


def test_normalize_movie_profile_extracts_expected_fields() -> None:
    client = object.__new__(TMDBClient)

    raw = {
        "id": 42,
        "title": "Inception",
        "original_title": "Inception",
        "overview": "A mind-bending thriller.",
        "release_date": "2010-07-16",
        "runtime": 148,
        "genres": [
            {"id": 878, "name": "Science Fiction"},
            {"id": 28, "name": "Action"},
        ],
        "credits": {
            "crew": [
                {"id": 525, "name": "Christopher Nolan", "job": "Director"},
                {"id": 526, "name": "Someone Else", "job": "Writer"},
            ],
            "cast": [
                {
                    "id": index,
                    "name": f"Actor {index}",
                    "character": f"Character {index}",
                    "order": index,
                }
                for index in range(12)
            ],
        },
        "keywords": {
            "keywords": [
                {"id": 1, "name": "dream"},
                {"id": 2, "name": "subconscious"},
            ]
        },
    }

    normalized = client.normalize_movie_profile(raw)

    assert normalized["tmdb_id"] == 42
    assert normalized["title"] == "Inception"
    assert normalized["year"] == "2010"
    assert normalized["directors"] == [{"id": 525, "name": "Christopher Nolan"}]
    assert len(normalized["cast"]) == 10
    assert normalized["cast"][0]["name"] == "Actor 0"
    assert normalized["keywords"] == [
        {"id": 1, "name": "dream"},
        {"id": 2, "name": "subconscious"},
    ]
