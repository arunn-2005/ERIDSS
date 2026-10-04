from neo4j import Session

def generate_risk_mitigation_plan(session: Session, limit: int = 5) -> dict:
    """
    Analyzes top high-risk nodes, identifies structural vulnerabilities (SPOF, missing fallbacks),
    and generates actionable mitigation recommendations.
    """
    # 1. Fetch top highest composite risk entities with their degree counts
    cypher_query = """
    MATCH (e:Entity)
    OPTIONAL MATCH (in_e:Entity)-[r_in]->(e)
    OPTIONAL MATCH (e)-[r_out]->(out_e:Entity)
    WITH e, 
         COUNT(DISTINCT in_e) AS in_degree, 
         COUNT(DISTINCT out_e) AS out_degree
    RETURN e.id AS id,
           e.name AS name,
           e.type AS type,
           COALESCE(e.composite_risk_score, 0.0) AS composite_risk_score,
           COALESCE(e.betweenness_centrality, 0.0) AS betweenness_centrality,
           in_degree,
           out_degree
    ORDER BY composite_risk_score DESC, betweenness_centrality DESC
    LIMIT $limit
    """
    
    results = session.run(cypher_query, limit=limit)
    high_risk_nodes = [record.data() for record in results]

    mitigation_plans = []

    for node in high_risk_nodes:
        node_id = node["id"]
        risk_score = node["composite_risk_score"]
        in_deg = node["in_degree"]
        out_deg = node["out_degree"]

        vulnerabilities = []
        recommended_actions = []

        # Analyze structural risk criteria
        if risk_score >= 50.0:
            vulnerabilities.append("Critical Risk Bottleneck: Composite risk score exceeds threshold (>= 50).")
            recommended_actions.append("Implement high-availability (HA) clustering or multi-region redundancy.")

        if in_deg == 1:
            vulnerabilities.append("Single Inbound Dependency (SPOF): Only 1 upstream entity feeds into this node.")
            recommended_actions.append("Establish a secondary failover path or alternate upstream provider.")

        if out_deg == 1:
            vulnerabilities.append("Single Downstream Sink: Only 1 downstream consumer relies on this node.")
            recommended_actions.append("Decouple dependency using async queuing or load balancing.")

        if not vulnerabilities:
            vulnerabilities.append("Moderate Centrality Risk: High connectivity load across the network graph.")
            recommended_actions.append("Monitor operational health telemetry and establish rate limiting.")

        mitigation_plans.append({
            "entity": {
                "id": node_id,
                "name": node["name"] or node_id,
                "type": (node["type"] or "Entity").capitalize(),
                "composite_risk_score": risk_score,
                "betweenness_centrality": node["betweenness_centrality"]
            },
            "risk_level": "CRITICAL" if risk_score >= 70 else ("HIGH" if risk_score >= 40 else "MEDIUM"),
            "vulnerabilities": vulnerabilities,
            "recommended_actions": recommended_actions
        })

    return {
        "status": "success",
        "total_analyzed": len(mitigation_plans),
        "mitigation_plans": mitigation_plans
    }