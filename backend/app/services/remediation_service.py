from neo4j import Session

def build_node_recommendation(
    name: str,
    node_type: str,
    risk_score: float,
    betweenness: float,
    in_deg: int,
    out_deg: int,
    blast_radius: int = None
) -> tuple[list[str], list[str]]:
    """
    Generates tailored vulnerabilities and mitigation actions based on
    structural topology, entity classification, and cascade blast radius.
    """
    vulnerabilities = []
    recommended_actions = []
    clean_type = (node_type or "Technology").capitalize()

    # 1. Critical composite risk threshold
    if risk_score >= 50.0:
        vulnerabilities.append(f"Critical Resilience Fragility: Composite risk index ({round(risk_score, 1)}) indicates systemic vulnerability.")
        if clean_type == "Technology":
            recommended_actions.append("Deploy active-active multi-availability zone replication with automated health probes.")
        elif clean_type == "Business_unit":
            recommended_actions.append("Establish redundancy protocols and designate secondary operational leads.")
        elif clean_type == "Process":
            recommended_actions.append("Implement automated rollback pipelines and asynchronous retry dead-letter queues.")
        else:
            recommended_actions.append("Establish high-availability redundancy and failover routing.")

    # 2. Centrality / Bridge Bottleneck
    if betweenness >= 0.0008:
        vulnerabilities.append("Structural Intermediary: Node lies on critical shortest paths across disparate architectural zones.")
        recommended_actions.append("Introduce load-balanced intermediary proxies or dual-homed interconnects to decentralize path traffic.")

    # 3. High Ingress Fan-In (Many upstream callers depend on this)
    if in_deg >= 3:
        vulnerabilities.append(f"High Ingress Fan-In: {in_deg} upstream dependencies converge on this entity.")
        recommended_actions.append("Deploy rate limiting, token buckets, and circuit breakers to prevent concurrent cascading saturation.")
    elif in_deg == 1:
        vulnerabilities.append("Single Upstream Dependency: Relies on only 1 upstream provider (SPOF).")
        recommended_actions.append("Establish a secondary upstream fallback or dynamic provider switching.")

    # 4. High Egress Fan-Out (Failure propagates to many downstream assets)
    if out_deg >= 3:
        vulnerabilities.append(f"Extensive Egress Fan-Out: Outage directly jeopardizes {out_deg} downstream dependents.")
        recommended_actions.append("Configure graceful service degradation defaults and localized client-side fallback caches.")
    elif out_deg == 1:
        vulnerabilities.append("Single Downstream Sink: Bound to only 1 operational consumer.")
        recommended_actions.append("Decouple point-to-point coupling using event queues or pub-sub messaging.")

    # 5. Blast Radius Severity (If provided from simulation)
    if blast_radius is not None and blast_radius > 5:
        vulnerabilities.append(f"Severe Blast Radius: Disruption propagates across {blast_radius} downstream network entities.")
        recommended_actions.append("Partition network boundaries using zero-trust service mesh isolation to contain cascading outages.")

    # 6. Fallback if no specific thresholds triggered
    if not vulnerabilities:
        vulnerabilities.append(f"Standard Operational Dependency: Component maintains balanced connectivity ({in_deg} In, {out_deg} Out).")
        recommended_actions.append("Ensure regular continuous telemetry checks, anomaly alerting, and baseline SLA monitoring.")

    # Remove duplicates while preserving order
    unique_actions = list(dict.fromkeys(recommended_actions))
    unique_vulns = list(dict.fromkeys(vulnerabilities))

    return unique_vulns, unique_actions


def generate_risk_mitigation_plan(session: Session, limit: int = 5) -> dict:
    """
    Analyzes top high-risk nodes, identifies structural vulnerabilities,
    and generates actionable, entity-specific mitigation recommendations.
    """
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
        node_name = node["name"] or node_id
        node_type = (node["type"] or "Technology").capitalize()
        risk_score = float(node["composite_risk_score"])
        betweenness = float(node["betweenness_centrality"])
        in_deg = int(node["in_degree"])
        out_deg = int(node["out_degree"])

        vulnerabilities, recommended_actions = build_node_recommendation(
            name=node_name,
            node_type=node_type,
            risk_score=risk_score,
            betweenness=betweenness,
            in_deg=in_deg,
            out_deg=out_deg
        )

        mitigation_plans.append({
            "entity": {
                "id": node_id,
                "name": node_name,
                "type": node_type,
                "composite_risk_score": risk_score,
                "betweenness_centrality": betweenness,
                "in_degree": in_deg,
                "out_degree": out_deg
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