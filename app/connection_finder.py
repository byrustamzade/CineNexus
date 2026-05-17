from app.neo4j_connection import Neo4jConnection


class ConnectionFinder:

    def __init__(self):
        self.connection = Neo4jConnection()

    def close(self):
        self.connection.close()

    def find_between_movies(self, first_tmdb_id: int, second_tmdb_id: int) -> dict:
        return {
            "first_title": self._get_movie_title(first_tmdb_id),
            "second_title": self._get_movie_title(second_tmdb_id),
            "shared_directors": self._find_shared_people(first_tmdb_id, second_tmdb_id, "DIRECTED_BY"),
            "shared_actors": self._find_shared_actors(first_tmdb_id, second_tmdb_id),
            "shared_genres": self._find_shared_nodes(first_tmdb_id, second_tmdb_id, "HAS_GENRE", "Genre"),
            "shared_keywords": self._find_shared_nodes(first_tmdb_id, second_tmdb_id, "HAS_KEYWORD", "Keyword"),
            "shared_years": self._find_shared_nodes(first_tmdb_id, second_tmdb_id, "RELEASED_IN", "Year"),
            "shortest_path": self._find_shortest_path(first_tmdb_id, second_tmdb_id),
        }

    def _get_movie_title(self, tmdb_id: int) -> str | None:
        with self.connection.session() as session:
            result = session.run(
                """
                MATCH (m:Movie {tmdb_id: $tmdb_id})
                RETURN m.title AS title
                """,
                tmdb_id=tmdb_id,
            )
            record = result.single()
            return record["title"] if record else None

    def _find_shared_people(self, first_id: int, second_id: int, relation: str) -> list[str]:
        with self.connection.session() as session:
            # `relation` is passed only from internal constants, not user input.
            result = session.run(
                f"""
                MATCH (m1:Movie {{tmdb_id: $first_id}})
                MATCH (m2:Movie {{tmdb_id: $second_id}})
                MATCH (m1)-[:{relation}]->(p:Person)<-[:{relation}]-(m2)
                RETURN collect(DISTINCT p.name) AS names
                """,
                first_id=first_id,
                second_id=second_id,
            )
            record = result.single()
            return record["names"] if record else []

    def _find_shared_actors(self, first_id: int, second_id: int) -> list[str]:
        with self.connection.session() as session:
            result = session.run(
                """
                MATCH (m1:Movie {tmdb_id: $first_id})
                MATCH (m2:Movie {tmdb_id: $second_id})
                MATCH (p:Person)-[:ACTED_IN]->(m1)
                MATCH (p)-[:ACTED_IN]->(m2)
                RETURN collect(DISTINCT p.name) AS names
                """,
                first_id=first_id,
                second_id=second_id,
            )
            record = result.single()
            return record["names"] if record else []

    def _find_shared_nodes(self, first_id: int, second_id: int, relation: str, label: str) -> list[str]:
        property_name = "value" if label == "Year" else "name"

        with self.connection.session() as session:
            # `relation` and `label` are fixed internal values selected by caller.
            result = session.run(
                f"""
                MATCH (m1:Movie {{tmdb_id: $first_id}})
                MATCH (m2:Movie {{tmdb_id: $second_id}})
                MATCH (m1)-[:{relation}]->(n:{label})<-[:{relation}]-(m2)
                RETURN collect(DISTINCT n.{property_name}) AS values
                """,
                first_id=first_id,
                second_id=second_id,
            )
            record = result.single()
            return record["values"] if record else []

    def _find_shortest_path(self, first_id: int, second_id: int) -> list[str]:
        with self.connection.session() as session:
            result = session.run(
                """
                MATCH (m1:Movie {tmdb_id: $first_id})
                MATCH (m2:Movie {tmdb_id: $second_id})
                // Cap expansion depth to keep interactive queries fast.
                MATCH path = shortestPath((m1)-[*..4]-(m2))
                RETURN [node IN nodes(path) |
                    labels(node)[0] + ':' + coalesce(node.name, node.title, toString(node.value))
                ] AS path
                LIMIT 1
                """,
                first_id=first_id,
                second_id=second_id,
            )

            record = result.single()
            return record["path"] if record else []
