from neo4j import Session

def simulate_entity_failure(session: Session, node_id: str, max_depth: int = 4) -> dict:
    """
    Simulates a failure of a specific entity node and calculates the downstream blast radius 
    by traversing outgoing dependency relationships up to max_depth hops.
    """
    # 1. Check if target entity exists
    target_check = session.run(
        "MATCH (e:Entity {id: $id}) RETURN e.id AS id, e.name AS name, e.type AS type",
        id=node_id
    ).single()

    if not target_check:
        return {
            "status": "error",
            "message": f"Entity with id '{node_id}' not found."
        }

    target_info = {
        "id": target_check["id"],
        "name": target_check["name"] or target_check["id"],
        "type": target_check["type"] or "Entity"
    }

    # 2. Traverse paths linked to the target node, excluding the target node itself
    cypher_traversal = """
    MATCH (failed:Entity {id: $node_id})
    MATCH path = (affected:Entity)-[*1..4]->(failed)
    WHERE affected.id <> $node_id
    WITH DISTINCT affected, min(length(path)) AS depth
    RETURN affected.id AS id, 
           affected.name AS name, 
           affected.type AS type, 
           COALESCE(affected.betweenness_centrality, 0.0) AS betweenness_centrality,
           depth
    ORDER BY depth ASC, betweenness_centrality DESC
    """

    results = session.run(cypher_traversal, node_id=node_id)

    affected_nodes = []
    categorized_impact = {}

    for record in results:
        node_type = (record["type"] or "Entity").capitalize()
        node_data = {
            "id": record["id"],
            "name": record["name"] or record["id"],
            "type": node_type,
            "betweenness_centrality": record["betweenness_centrality"],
            "depth": record["depth"]
        }
        
        affected_nodes.append(node_data)

        if node_type not in categorized_impact:
            categorized_impact[node_type] = []
        categorized_impact[node_type].append(node_data)

    return {
        "status": "success",
        "target_node": target_info,
        "blast_radius_count": len(affected_nodes),
        "affected_nodes": affected_nodes,
        "categorized_impact": categorized_impact
    }

def simulate_multi_entity_failure(session: Session, node_ids: list[str], max_depth: int = 4) -> dict:
    """
    Simulates simultaneous failures across multiple entities and computes 
    the deduplicated combined downstream blast radius.
    """
    if not node_ids:
        return {"status": "error", "message": "No node IDs provided for simulation."}

    # 1. Verify target entities exist
    target_check = session.run(
        "MATCH (e:Entity) WHERE e.id IN $ids RETURN e.id AS id, e.name AS name, e.type AS type",
        ids=node_ids
    )
    targets = [record.data() for record in target_check]
    found_ids = {t["id"] for t in targets}

    if not found_ids:
        return {"status": "error", "message": "None of the specified node IDs were found."}

    # 2. Query combined downstream impact across all target nodes
    cypher_traversal = """
    MATCH (failed:Entity) WHERE failed.id IN $node_ids
    MATCH path = (affected:Entity)-[*1..4]->(failed)
    WHERE NOT affected.id IN $node_ids
    WITH DISTINCT affected, min(length(path)) AS depth
    RETURN affected.id AS id, 
           affected.name AS name, 
           affected.type AS type, 
           COALESCE(affected.composite_risk_score, 0.0) AS composite_risk_score,
           COALESCE(affected.betweenness_centrality, 0.0) AS betweenness_centrality,
           depth
    ORDER BY depth ASC, composite_risk_score DESC
    """

    results = session.run(cypher_traversal, node_ids=list(found_ids))

    affected_nodes = []
    categorized_impact = {}

    for record in results:
        node_type = (record["type"] or "Entity").capitalize()
        node_data = {
            "id": record["id"],
            "name": record["name"] or record["id"],
            "type": node_type,
            "composite_risk_score": record["composite_risk_score"],
            "betweenness_centrality": record["betweenness_centrality"],
            "depth": record["depth"]
        }
        
        affected_nodes.append(node_data)

        if node_type not in categorized_impact:
            categorized_impact[node_type] = []
        categorized_impact[node_type].append(node_data)

    return {
        "status": "success",
        "failed_targets": targets,
        "combined_blast_radius_count": len(affected_nodes),
        "affected_nodes": affected_nodes,
        "categorized_impact": categorized_impact
    }