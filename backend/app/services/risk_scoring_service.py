from neo4j import Session

def calculate_composite_risk_scores(session: Session) -> dict:
    """
    Computes a multi-factor composite risk score (0-100) for each entity
    combining topological centrality and entity criticality tiers.
    """
    # 1. Fetch all nodes with their topological metrics
    cypher_query = """
    MATCH (e:Entity)
    RETURN e.id AS id, 
           e.name AS name, 
           e.type AS type, 
           COALESCE(e.betweenness_centrality, 0.0) AS betweenness,
           COALESCE(e.degree_centrality, 0.0) AS degree,
           COALESCE(e.criticality_tier, 'MEDIUM') AS tier
    """
    results = session.run(cypher_query)
    nodes = [record.data() for record in results]

    if not nodes:
        return {"status": "success", "message": "No nodes to score.", "updated_count": 0}

    # Weight multipliers
    TIER_WEIGHTS = {"CRITICAL": 40, "HIGH": 30, "MEDIUM": 15, "LOW": 5}
    BETWEENNESS_WEIGHT = 40
    DEGREE_WEIGHT = 20

    max_betweenness = max([n["betweenness"] for n in nodes] or [1.0])
    max_degree = max([n["degree"] for n in nodes] or [1.0])

    # Avoid division by zero
    max_betweenness = max_betweenness if max_betweenness > 0 else 1.0
    max_degree = max_degree if max_degree > 0 else 1.0

    scored_updates = []
    for node in nodes:
        # Normalize centralities to 0..1 scale
        norm_betweenness = node["betweenness"] / max_betweenness
        norm_degree = node["degree"] / max_degree
        tier_score = TIER_WEIGHTS.get(str(node["tier"]).upper(), 15)

        # Composite formula (0 to 100)
        raw_score = (norm_betweenness * BETWEENNESS_WEIGHT) + (norm_degree * DEGREE_WEIGHT) + tier_score
        final_score = round(min(max(raw_score, 0.0), 100.0), 2)

        scored_updates.append({
            "id": node["id"],
            "composite_risk_score": final_score
        })

    # 2. Write scores back into Neo4j
    update_cypher = """
    UNWIND $updates AS row
    MATCH (e:Entity {id: row.id})
    SET e.composite_risk_score = row.composite_risk_score,
        e.risk_last_updated = timestamp()
    """
    session.run(update_cypher, updates=scored_updates)

    return {
        "status": "success",
        "scored_nodes_count": len(scored_updates),
        "sample_top_scores": sorted(scored_updates, key=lambda x: x["composite_risk_score"], reverse=True)[:5]
    }