import os
from dotenv import load_dotenv
import logging
from neo4j import GraphDatabase, Driver

load_dotenv()
logger = logging.getLogger(__name__)

# Fetch environment configuration or fall back to local defaults
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

class Neo4jManager:
    """
    Singleton connection manager for Neo4j Graph Database driver.
    """
    def __init__(self):
        self._driver: Driver | None = None

    def connect(self):
        if not self._driver:
            try:
                self._driver = GraphDatabase.driver(
                    NEO4J_URI, 
                    auth=(NEO4J_USER, NEO4J_PASSWORD),
                    max_connection_lifetime=3600,
                    max_connection_pool_size=50
                )
                self._driver.verify_connectivity()
                logger.info("Connected to Neo4j instance successfully.")
            except Exception as e:
                logger.error(f"Failed to connect to Neo4j: {str(e)}")
                raise e

    def close(self):
        if self._driver:
            self._driver.close()
            logger.info("Neo4j connection closed.")

    def get_session(self):
        if not self._driver:
            self.connect()
        return self._driver.session()

# Global Singleton Instance
neo4j_client = Neo4jManager()

def get_neo4j_session():
    """
    FastAPI dependency that yields a database session and ensures it closes when done.
    """
    session = neo4j_client.get_session()
    try:
        yield session
    finally:
        session.close()