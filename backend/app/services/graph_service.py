import networkx as nx
import re
from neo4j import Session

def calculate_topological_metrics(nodes: list, edges: list) -> dict:
    """
    Builds an in-memory directed graph using NetworkX and calculates 
    centrality metrics for each entity node.
    """
    # 1. Initialize a Directed Graph
    G = nx.DiGraph()

    # 2. Add entity nodes to the graph
    for node in nodes:
        G.add_node(
            str(node["id"]), 
            name=node.get("name", ""), 
            type=node.get("type", "Entity")
        )

    # 3. Add directional edges between entities
    for edge in edges:
        G.add_edge(
            str(edge["source_id"]), 
            str(edge["target_id"]), 
            label=edge.get("relation_type", "")
        )

    # 4. Calculate Degree Centrality
    degree_cent = nx.degree_centrality(G) if len(G) > 0 else {}

    # 5. Calculate Betweenness Centrality
    betweenness_cent = nx.betweenness_centrality(G) if len(G) > 0 else {}

    # 6. Assemble node-by-node topological metrics dictionary
    metrics = {}
    for node_id in G.nodes():
        metrics[node_id] = {
            "degree_centrality": round(degree_cent.get(node_id, 0.0), 4),
            "betweenness_centrality": round(betweenness_cent.get(node_id, 0.0), 4),
            "in_degree": G.in_degree(node_id),      # Total incoming relationships
            "out_degree": G.out_degree(node_id)     # Total outgoing relationships
        }

    return metrics

def sanitize_relation_label(label: str) -> str:
    """
    Normalizes raw relationship strings into valid Cypher relationship formats.
    Example: 'depends on' -> 'DEPENDS_ON'
    """
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", label.strip())
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned.upper() if cleaned else "RELATED_TO"


def sync_entities_to_neo4j(session: Session, document_id: str, nodes: list, edges: list) -> dict:
    """
    Ingests entity nodes, relationships, and NetworkX topological metrics into Neo4j
    using idempotent Cypher UNWIND queries.
    """
    if not nodes:
        return {"status": "skipped", "message": "No nodes provided for synchronization."}

    # 1. Compute NetworkX topological metrics (from Step 2)
    metrics = calculate_topological_metrics(nodes, edges)

    # 2. Build structured node payloads combining entity attributes and computed metrics
    prepared_nodes = []
    for node in nodes:
        node_id = str(node["id"])
        node_metrics = metrics.get(node_id, {})
        prepared_nodes.append({
            "id": node_id,
            "name": node.get("name", ""),
            "type": node.get("type", "Entity").capitalize(),
            "document_id": str(document_id),
            "degree_centrality": node_metrics.get("degree_centrality", 0.0),
            "betweenness_centrality": node_metrics.get("betweenness_centrality", 0.0),
            "in_degree": node_metrics.get("in_degree", 0),
            "out_degree": node_metrics.get("out_degree", 0)
        })

    # 3. Enforce Uniqueness Constraint on Node ID in Neo4j
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;")

    # 4. Upsert Nodes in Batch via Cypher UNWIND
    node_cypher = """
    UNWIND $nodes AS row
    MERGE (e:Entity {id: row.id})
    ON CREATE SET 
        e.name = row.name,
        e.type = row.type,
        e.document_id = row.document_id,
        e.degree_centrality = row.degree_centrality,
        e.betweenness_centrality = row.betweenness_centrality,
        e.in_degree = row.in_degree,
        e.out_degree = row.out_degree,
        e.created_at = timestamp()
    ON MATCH SET 
        e.name = row.name,
        e.type = row.type,
        e.degree_centrality = row.degree_centrality,
        e.betweenness_centrality = row.betweenness_centrality,
        e.in_degree = row.in_degree,
        e.out_degree = row.out_degree,
        e.updated_at = timestamp()
    """
    session.run(node_cypher, nodes=prepared_nodes)

    # 5. Group relationships by label type
    edges_grouped = {}
    for edge in edges:
        rel_type = sanitize_relation_label(edge.get("relation_type", "RELATED_TO"))
        if rel_type not in edges_grouped:
            edges_grouped[rel_type] = []
        
        edges_grouped[rel_type].append({
            "id": str(edge.get("id", "")),
            "source": str(edge["source_id"]),
            "target": str(edge["target_id"]),
            "document_id": str(document_id)
        })

    # 6. Batch upsert relationships per label type
    for rel_type, rel_batch in edges_grouped.items():
        edge_cypher = f"""
        UNWIND $edges AS row
        MATCH (source:Entity {{id: row.source}})
        MATCH (target:Entity {{id: row.target}})
        MERGE (source)-[r:`{rel_type}`]->(target)
        ON CREATE SET r.id = row.id, r.document_id = row.document_id, r.created_at = timestamp()
        """
        session.run(edge_cypher, edges=rel_batch)

    return {
        "status": "success",
        "nodes_synced": len(prepared_nodes),
        "edges_synced": sum(len(batch) for batch in edges_grouped.values())
    }