from app.neo4j_connection import Neo4jConnection


class GraphStore:
    """Persist normalized TMDB movie profiles into Neo4j."""

    def __init__(self):
        self.connection = Neo4jConnection()

    def close(self):
        self.connection.close()

    def save_movie_profile(self, movie: dict):
        """Write a full movie profile in a single managed write transaction."""
        with self.connection.session() as session:
            session.execute_write(self._save_movie_profile, movie)

    @staticmethod
    def _save_movie_profile(tx, movie: dict):
        # Use tmdb_id as the stable identity key for idempotent upserts.
        tx.run(
            """
            MERGE (m:Movie {tmdb_id: $tmdb_id})
            SET
                m.title = $title,
                m.original_title = $original_title,
                m.overview = $overview,
                m.release_date = $release_date,
                m.runtime = $runtime
            """,
            tmdb_id=movie["tmdb_id"],
            title=movie["title"],
            original_title=movie["original_title"],
            overview=movie["overview"],
            release_date=movie["release_date"],
            runtime=movie["runtime"],
        )

        if movie.get("year"):
            # Model release year as a shared node for temporal traversals.
            tx.run(
                """
                MATCH (m:Movie {tmdb_id: $tmdb_id})
                MERGE (y:Year {value: $year})
                MERGE (m)-[:RELEASED_IN]->(y)
                """,
                tmdb_id=movie["tmdb_id"],
                year=movie["year"],
            )

        # Direction is intentional to keep role-based traversals explicit.
        for director in movie.get("directors", []):
            tx.run(
                """
                MATCH (m:Movie {tmdb_id: $tmdb_id})
                MERGE (p:Person {tmdb_id: $person_id})
                SET p.name = $name
                MERGE (m)-[:DIRECTED_BY]->(p)
                """,
                tmdb_id=movie["tmdb_id"],
                person_id=director["id"],
                name=director["name"],
            )

        # Persist cast order on the relationship so billing rank remains queryable.
        for cast in movie.get("cast", []):
            tx.run(
                """
                MATCH (m:Movie {tmdb_id: $tmdb_id})
                MERGE (p:Person {tmdb_id: $person_id})
                SET p.name = $name
                MERGE (p)-[r:ACTED_IN]->(m)
                SET r.character = $character,
                    r.cast_order = $cast_order
                """,
                tmdb_id=movie["tmdb_id"],
                person_id=cast["id"],
                name=cast["name"],
                character=cast["character"],
                cast_order=cast["order"],
            )

        for genre in movie.get("genres", []):
            tx.run(
                """
                MATCH (m:Movie {tmdb_id: $tmdb_id})
                MERGE (g:Genre {tmdb_id: $genre_id})
                SET g.name = $name
                MERGE (m)-[:HAS_GENRE]->(g)
                """,
                tmdb_id=movie["tmdb_id"],
                genre_id=genre["id"],
                name=genre["name"],
            )

        for keyword in movie.get("keywords", []):
            tx.run(
                """
                MATCH (m:Movie {tmdb_id: $tmdb_id})
                MERGE (k:Keyword {tmdb_id: $keyword_id})
                SET k.name = $name
                MERGE (m)-[:HAS_KEYWORD]->(k)
                """,
                tmdb_id=movie["tmdb_id"],
                keyword_id=keyword["id"],
                name=keyword["name"],
            )
