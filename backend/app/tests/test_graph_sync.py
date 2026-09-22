from app.core.neo4j import neo4j_client
from app.services.graph_service import sync_entities_to_neo4j

# 1. Mock entity nodes extracted from a document
mock_nodes = [
    {"id": "node_1", "name": "API Gateway", "type": "Service"},
    {"id": "node_2", "name": "Auth Service", "type": "Microservice"},
    {"id": "node_3", "name": "User DB", "type": "Database"}
]

# 2. Mock relationships (Gateway -> Auth Service -> User DB)
mock_edges = [
    {"id": "edge_101", "source_id": "node_1", "target_id": "node_2", "relation_type": "ROUTES_TO"},
    {"id": "edge_102", "source_id": "node_2", "target_id": "node_3", "relation_type": "READS_FROM"}
]

def run_test():
    print("Connecting to Neo4j...")
    session = neo4j_client.get_session()
    try:
        print("Running sync_entities_to_neo4j...")
        result = sync_entities_to_neo4j(
            session=session,
            document_id="doc_test_123",
            nodes=mock_nodes,
            edges=mock_edges
        )
        print("Sync Result:", result)
    finally:
        session.close()

if __name__ == "__main__":
    run_test()