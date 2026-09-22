import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession

from app.database.db import get_db
from app.models.user import User
from app.models.document import Document
from app.models.extracted_text import ExtractedText
from app.models.entity import Entity
# Import your Relationship model (adjust model name if different, e.g., EntityRelationship)
from app.models.relationship import Relationship 

from app.dependencies.auth import get_current_user
from app.services.relation_extractor import extract_and_persist_relations
from app.core.neo4j import get_neo4j_session
from app.services.graph_service import sync_entities_to_neo4j

router = APIRouter(
    prefix="/documents",
    tags=["Relation Extraction and Knowledge Graph"]
)


@router.post(
    "/{document_id}/extract-relations",
    status_code=status.HTTP_200_OK
)
def extract_document_relations(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    extracted_text_obj = (
        db.query(ExtractedText)
        .filter(ExtractedText.document_id == document_id)
        .first()
    )

    if not extracted_text_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No extracted text found for this document. Run text processing first."
        )

    saved_entities = (
        db.query(Entity)
        .filter(Entity.document_id == document_id)
        .all()
    )

    if not saved_entities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No entities found for this document. Run extract-entities first."
        )

    persisted_entities_payload = [
        {
            "id": str(e.id),
            "entity_name": getattr(e, "name", getattr(e, "entity_name", "")),
            "entity_type": getattr(e, "entity_type", "ENTITY"),
            "start": getattr(e, "start_char", 0),
            "end": getattr(e, "end_char", 0)
        }
        for e in saved_entities
    ]

    graph_payload = extract_and_persist_relations(
        db=db,
        document_id=str(document_id),
        text=extracted_text_obj.extracted_text,
        persisted_entities=persisted_entities_payload
    )

    return {
        "message": "Relationships extracted successfully.",
        "graph": graph_payload
    }


@router.post("/{document_id}/sync")
def sync_document_to_graph(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    neo4j_session: Neo4jSession = Depends(get_neo4j_session)
):
    """
    Fetches entities and relationships for a given document from PostgreSQL,
    computes topological risk metrics, and syncs them into Neo4j.
    """
    # 1. Verify document ownership
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    # 2. Fetch extracted entities from PostgreSQL
    entities = db.query(Entity).filter(Entity.document_id == document_id).all()
    if not entities:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No extracted entities found for this document."
        )

    # 3. Fetch extracted relationships from PostgreSQL
    relationships = db.query(Relationship).filter(Relationship.document_id == document_id).all()

    # 4. Map SQL models to dictionary payloads
    nodes = [
        {
            "id": str(e.id),
            "name": getattr(e, "name", getattr(e, "entity_name", "")),
            "type": getattr(e, "entity_type", "Entity")
        }
        for e in entities
    ]

    edges = [
        {
            "id": str(r.id),
            "source_id": str(r.source_entity_id),
            "target_id": str(r.target_entity_id),
            "relation_type": getattr(r, "relation_type", "RELATED_TO")
        }
        for r in relationships
    ]

    # 5. Synchronize to Neo4j
    result = sync_entities_to_neo4j(
        session=neo4j_session,
        document_id=str(document_id),
        nodes=nodes,
        edges=edges
    )

    return {"message": "Graph synchronized successfully", "data": result}


@router.get("/risk-analysis/critical-nodes")
def get_critical_risk_nodes(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    neo4j_session: Neo4jSession = Depends(get_neo4j_session)
):
    """
    Queries Neo4j directly for entities sorted by highest betweenness centrality 
    (Single Points of Failure).
    """
    cypher_query = """
    MATCH (e:Entity)
    RETURN 
        e.id AS id,
        e.name AS name,
        e.type AS type,
        e.betweenness_centrality AS betweenness_centrality,
        e.degree_centrality AS degree_centrality,
        e.in_degree AS in_degree,
        e.out_degree AS out_degree
    ORDER BY e.betweenness_centrality DESC
    LIMIT $limit
    """
    result = neo4j_session.run(cypher_query, limit=limit)
    records = [record.data() for record in result]
    
    return {"critical_nodes": records}