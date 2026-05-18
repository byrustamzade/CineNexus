from neo4j import GraphDatabase

from app.settings import (
    NEO4J_PASSWORD,
    NEO4J_URI,
    NEO4J_USERNAME,
)


class Neo4jConnection:
    """Thin wrapper around the Neo4j driver configuration and lifecycle."""

    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
        )

    def close(self):
        self.driver.close()

    def session(self):
        """Create a new Neo4j session for read/write operations."""
        return self.driver.session()
