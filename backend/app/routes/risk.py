from fastapi import APIRouter, HTTPException, Query, Depends
from neo4j import Session
from pydantic import BaseModel, Field
from app.services.graph_service import (
    get_critical_risk_nodes,
    recalculate_graph_centrality
)

# TODO: Adjust this import path to match where your Neo4j session/driver dependency is defined in your project
from app.core.neo4j import get_neo4j_session  
from app.services.impact_service import simulate_entity_failure, simulate_multi_entity_failure
from app.services.risk_scoring_service import calculate_composite_risk_scores
from app.services.remediation_service import generate_risk_mitigation_plan

router = APIRouter(prefix="/risk-analysis", tags=["Risk Analysis"])


@router.get("/critical-nodes")
def fetch_critical_nodes(
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_neo4j_session)
):
    """
    Fetches top bottleneck/critical entities ordered by betweenness centrality descending.
    """
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
    """
    Reads existing graph from Neo4j, recomputes NetworkX centrality metrics, 
    and updates node properties in Neo4j.
    """
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
    """
    Simulates a failure cascade starting from target entity and calculates downstream blast radius.
    """
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
    """
    Calculates multi-factor composite risk scores (0-100) blending topology and criticality attributes.
    """
    try:
        result = calculate_composite_risk_scores(session)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate composite risk scores: {str(e)}")

# Request model for multi-node simulation
class MultiFailureScenarioRequest(BaseModel):
    node_ids: list[str] = Field(..., example=["b241d291-a481-48b1-8729-154ac5bd4cca", "cd51fb79-7046-483d-bda4-a73754258e25"])
    max_depth: int = Field(4, ge=1, le=10)


@router.post("/simulate-multi-failure")
def simulate_multi_failure(
    payload: MultiFailureScenarioRequest,
    session: Session = Depends(get_neo4j_session)
):
    """
    Simulates a simultaneous multi-node failure scenario and returns the aggregated blast radius.
    """
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
    """
    Analyzes high-risk entities and returns actionable mitigation/remediation strategies.
    """
    try:
        result = generate_risk_mitigation_plan(session, limit=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate mitigation recommendations: {str(e)}")