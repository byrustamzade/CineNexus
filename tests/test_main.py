from main import print_connections


def test_print_connections_handles_empty_result(capsys) -> None:
    print_connections({})

    output = capsys.readouterr().out

    assert "No connections found." in output


def test_print_connections_renders_shortest_path(capsys) -> None:
    connections = {
        "shared_directors": ["Christopher Nolan"],
        "shared_actors": [],
        "shared_genres": ["Science Fiction"],
        "shared_keywords": ["space"],
        "shared_years": [],
        "shortest_path": [
            "Movie:Interstellar",
            "Person:Christopher Nolan",
            "Movie:Inception",
        ],
    }

    print_connections(connections)
    output = capsys.readouterr().out

    assert "Shared directors:" in output
    assert "Christopher Nolan" in output
    assert "Movie:Interstellar -> Person:Christopher Nolan -> Movie:Inception" in output
