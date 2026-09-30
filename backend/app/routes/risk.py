from fastapi import APIRouter, HTTPException, Query, Depends
from neo4j import Session
from app.services.graph_service import (
    get_critical_risk_nodes,
    recalculate_graph_centrality
)

# TODO: Adjust this import path to match where your Neo4j session/driver dependency is defined in your project
from app.core.neo4j import get_neo4j_session  

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