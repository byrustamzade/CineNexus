from app.neo4j_connection import Neo4jConnection


class ConnectionFinder:
    def __init__(self):
        self.connection = Neo4jConnection()

    def close(self):
        self.connection.close()

    def find_between_movies(self, first_tmdb_id: int, second_tmdb_id: int) -> dict:
        with self.connection.session() as session:
            # Use a managed read transaction so Neo4j can safely retry transient read failures.
            return session.execute_read(
                self._find_between_movies,
                first_tmdb_id,
                second_tmdb_id,
            )

    @staticmethod
    def _find_between_movies(tx, first_tmdb_id: int, second_tmdb_id: int) -> dict:
        # Each OPTIONAL MATCH is followed by WITH to isolate aggregates and avoid
        # row multiplication across independent match branches.
        result = tx.run(
            """
            MATCH (m1:Movie {tmdb_id: $first_id})
            MATCH (m2:Movie {tmdb_id: $second_id})

            OPTIONAL MATCH (m1)-[:DIRECTED_BY]->(director:Person)<-[:DIRECTED_BY]-(m2)
            WITH m1, m2, collect(DISTINCT director.name) AS shared_directors

            OPTIONAL MATCH (actor:Person)-[:ACTED_IN]->(m1)
            MATCH (actor)-[:ACTED_IN]->(m2)
            WITH m1, m2, shared_directors, collect(DISTINCT actor.name) AS shared_actors

            OPTIONAL MATCH (m1)-[:HAS_GENRE]->(genre:Genre)<-[:HAS_GENRE]-(m2)
            WITH m1, m2, shared_directors, shared_actors, collect(DISTINCT genre.name) AS shared_genres

            OPTIONAL MATCH (m1)-[:HAS_KEYWORD]->(keyword:Keyword)<-[:HAS_KEYWORD]-(m2)
            WITH m1, m2, shared_directors, shared_actors, shared_genres, collect(DISTINCT keyword.name) AS shared_keywords

            OPTIONAL MATCH (m1)-[:RELEASED_IN]->(year:Year)<-[:RELEASED_IN]-(m2)
            WITH
                m1,
                m2,
                shared_directors,
                shared_actors,
                shared_genres,
                shared_keywords,
                collect(DISTINCT year.value) AS shared_years

            // Bound shortestPath expansion to keep interactive queries predictable.
            OPTIONAL MATCH path = shortestPath((m1)-[*..4]-(m2))

            RETURN
                m1.title AS first_title,
                m2.title AS second_title,
                shared_directors,
                shared_actors,
                shared_genres,
                shared_keywords,
                shared_years,
                // Normalize heterogeneous node labels into a single printable path format.
                [node IN nodes(path) |
                    labels(node)[0] + ':' + coalesce(node.name, node.title, toString(node.value))
                ] AS shortest_path
            """,
            first_id=first_tmdb_id,
            second_id=second_tmdb_id,
        )

        record = result.single()

        if not record:
            return {}

        return {
            "first_title": record["first_title"],
            "second_title": record["second_title"],
            "shared_directors": record["shared_directors"],
            "shared_actors": record["shared_actors"],
            "shared_genres": record["shared_genres"],
            "shared_keywords": record["shared_keywords"],
            "shared_years": record["shared_years"],
            "shortest_path": record["shortest_path"],
        }
