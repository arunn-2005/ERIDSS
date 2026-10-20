import re
from fastapi import APIRouter, HTTPException, Query, Depends
from neo4j import Session
from pydantic import BaseModel, Field

from app.core.neo4j import get_neo4j_session  
from app.services.graph_service import (
    get_critical_risk_nodes,
    recalculate_graph_centrality
)
from app.services.impact_service import simulate_entity_failure, simulate_multi_entity_failure
from app.services.risk_scoring_service import calculate_composite_risk_scores
from app.services.remediation_service import (
    generate_risk_mitigation_plan,
    build_node_recommendation
)

router = APIRouter(prefix="/risk-analysis", tags=["Risk Analysis"])


@router.get("/critical-nodes")
def fetch_critical_nodes(
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_neo4j_session)
):
    try:
        nodes = get_critical_risk_nodes(session, limit=limit)
        return {
            "status": "success",
            "critical_nodes": nodes,
            "total": len(nodes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch critical nodes: {str(e)}")


@router.post("/recalculate")
def trigger_recalculate_risk(session: Session = Depends(get_neo4j_session)):
    try:
        result = recalculate_graph_centrality(session)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to recalculate risk centrality: {str(e)}")


@router.post("/simulate-failure")
def simulate_failure(
    node_id: str = Query(..., description="ID of the entity to simulate failure for"),
    max_depth: int = Query(4, ge=1, le=10),
    session: Session = Depends(get_neo4j_session)
):
    try:
        result = simulate_entity_failure(session, node_id=node_id, max_depth=max_depth)
        if result.get("status") == "error":
            raise HTTPException(status_code=404, detail=result.get("message"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run impact simulation: {str(e)}")


@router.post("/calculate-composite-scores")
def trigger_composite_scoring(session: Session = Depends(get_neo4j_session)):
    try:
        result = calculate_composite_risk_scores(session)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate composite risk scores: {str(e)}")


class MultiFailureScenarioRequest(BaseModel):
    node_ids: list[str] = Field(..., example=["b241d291-a481-48b1-8729-154ac5bd4cca"])
    max_depth: int = Field(4, ge=1, le=10)


@router.post("/simulate-multi-failure")
def simulate_multi_failure(
    payload: MultiFailureScenarioRequest,
    session: Session = Depends(get_neo4j_session)
):
    try:
        result = simulate_multi_entity_failure(
            session=session, 
            node_ids=payload.node_ids, 
            max_depth=payload.max_depth
        )
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute multi-node simulation: {str(e)}")


@router.get("/recommendations")
def get_risk_mitigation_recommendations(
    limit: int = Query(5, ge=1, le=20),
    session: Session = Depends(get_neo4j_session)
):
    try:
        result = generate_risk_mitigation_plan(session, limit=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate mitigation recommendations: {str(e)}")


# -------------------------------------------------------------
# NLP Risk & Impact Query System
# -------------------------------------------------------------
class NLPQueryRequest(BaseModel):
    query: str = Field(..., example="What is the blast radius if Sales fails?")
    max_depth: int = Field(4, ge=1, le=10)


@router.post("/nlp-query")
def process_nlp_risk_query(
    payload: NLPQueryRequest,
    session: Session = Depends(get_neo4j_session)
):
    """
    Extracts the target entity from a natural language query, computes its real-time 
    topological metrics, executes failure cascade simulation, and generates customized mitigations.
    """
    raw_query = payload.query.strip()
    if not raw_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # 1. Fetch all candidate entity names and IDs from Neo4j
    entities_query = """
    MATCH (e:Entity)
    OPTIONAL MATCH (in_e:Entity)-[r_in]->(e)
    OPTIONAL MATCH (e)-[r_out]->(out_e:Entity)
    WITH e, COUNT(DISTINCT in_e) AS in_degree, COUNT(DISTINCT out_e) AS out_degree
    RETURN e.id AS id,
           e.name AS name,
           e.type AS type,
           COALESCE(e.composite_risk_score, 0.0) AS composite_risk_score,
           COALESCE(e.betweenness_centrality, 0.0) AS betweenness_centrality,
           in_degree,
           out_degree
    """
    records = [r.data() for r in session.run(entities_query)]
    if not records:
        raise HTTPException(status_code=404, detail="No entities found in the graph.")

    # 2. Extract matched entity using case-insensitive token boundary matching
    matched_node = None
    # Sort entities by length descending to match multi-word names first (e.g. 'Delta Lake' before 'Lake')
    records_sorted = sorted(records, key=lambda x: len(x["name"] or ""), reverse=True)

    for node in records_sorted:
        node_name = (node["name"] or "").strip()
        if not node_name:
            continue
        # Check boundary match or containment in prompt
        pattern = r'\b' + re.escape(node_name.lower()) + r'\b'
        if re.search(pattern, raw_query.lower()):
            matched_node = node
            break

    # Fallback substring match if punctuation interferes
    if not matched_node:
        for node in records_sorted:
            node_name = (node["name"] or "").strip()
            if node_name and node_name.lower() in raw_query.lower():
                matched_node = node
                break

    if not matched_node:
        available_names = [n["name"] for n in records[:8] if n["name"]]
        raise HTTPException(
            status_code=404,
            detail=f"Could not identify a recognized entity from query. Try mentioning entities like: {', '.join(available_names)}"
        )

    # 3. Simulate failure cascade for the matched entity
    cascade_result = simulate_entity_failure(
        session, 
        node_id=matched_node["id"], 
        max_depth=payload.max_depth
    )

    blast_radius_count = 0
    if cascade_result.get("status") == "success":
        # Extract total affected count
            blast_radius_count = cascade_result.get("blast_radius_count", len(cascade_result.get("affected_nodes", [])))
    # 4. Generate custom mitigation
    node_name = matched_node["name"] or matched_node["id"]
    node_type = (matched_node["type"] or "Technology").capitalize()
    risk_score = float(matched_node["composite_risk_score"])
    betweenness = float(matched_node["betweenness_centrality"])
    in_deg = int(matched_node["in_degree"])
    out_deg = int(matched_node["out_degree"])

    vulns, actions = build_node_recommendation(
        name=node_name,
        node_type=node_type,
        risk_score=risk_score,
        betweenness=betweenness,
        in_deg=in_deg,
        out_deg=out_deg,
        blast_radius=blast_radius_count
    )

    return {
        "status": "success",
        "query": raw_query,
        "matched_entity": {
            "id": matched_node["id"],
            "name": node_name,
            "type": node_type,
            "composite_risk_score": risk_score,
            "betweenness_centrality": betweenness,
            "in_degree": in_deg,
            "out_degree": out_deg
        },
        "cascade_simulation": cascade_result,
        "mitigation_plan": {
            "risk_level": "CRITICAL" if risk_score >= 70 else ("HIGH" if risk_score >= 40 else "MEDIUM"),
            "vulnerabilities": vulns,
            "recommended_actions": actions
        }
    }