import uuid
import re
from sqlalchemy.orm import Session
from app.models.relationship import Relationship, KnowledgeGraph

try:
    from app.models.relationship import RelationshipEvidence
except ImportError:
    class RelationshipEvidence:
        def __init__(self, **kwargs): pass

# Predicate patterns mapping to canonical edge types
RELATION_PATTERNS = [
    ("located_in", re.compile(r"\b(in|at|based in|located in|from)\b", re.IGNORECASE)),
    ("uses", re.compile(r"\b(using|uses|utilizing|utilizes|built with|developed with|in)\b", re.IGNORECASE)),
    ("developed", re.compile(r"\b(developed|built|architected|engineered|created|designed)\b", re.IGNORECASE)),
    ("managed_by", re.compile(r"\b(head|lead|secretary|member|managed by|supervised by)\b", re.IGNORECASE)),
    ("affiliated_with", re.compile(r"\b(at|of|chapter|college|university|organization)\b", re.IGNORECASE)),
    ("awarded_by", re.compile(r"\b(by|at|from|specialization|certificate)\b", re.IGNORECASE)),
]

def find_entity_spans(text: str, entities: list):
    """Find character offsets for entities if missing."""
    spans = []
    for ent in entities:
        name = ent.get("entity_name", "").strip()
        if not name:
            continue
        start = ent.get("start", 0)
        end = ent.get("end", 0)
        if start == 0 and end == 0:
            match = re.search(re.escape(name), text, re.IGNORECASE)
            if match:
                start, end = match.start(), match.end()
        spans.append({
            "id": ent["id"],
            "name": name,
            "type": ent.get("entity_type", "ENTITY").lower(),
            "start": start,
            "end": end
        })
    return sorted(spans, key=lambda x: x["start"])

def determine_relation(head, tail, context_window: str):
    """Derive semantic relation from entity types and inter-entity context text."""
    h_type = head["type"]
    t_type = tail["type"]
    
    # 1. Regex context cues
    for rel_type, pattern in RELATION_PATTERNS:
        if pattern.search(context_window):
            return rel_type, 0.90

    # 2. Type-driven fallbacks
    if h_type in ["organization", "vendor"] and t_type == "location":
        return "located_in", 0.85
    if h_type in ["project", "software"] and t_type in ["software", "technology"]:
        return "uses", 0.80
    if h_type in ["person", "role"] and t_type in ["organization", "vendor"]:
        return "affiliated_with", 0.80
    if h_type == "certificate" and t_type in ["vendor", "organization"]:
        return "awarded_by", 0.85

    return None, 0.0

def extract_and_persist_relations(
    db: Session,
    document_id: str,
    text: str,
    persisted_entities: list,
    threshold: float = 0.5
):
    if len(persisted_entities) < 2:
        return {"nodes": [], "edges": []}

    spans = find_entity_spans(text, persisted_entities)
    db_relationships = []
    db_evidence = []
    graph_edges = []
    seen_pairs = set()

    # Split into sentences or lines for localized relational context
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    for line in lines:
        # Get entities present in this line
        line_entities = [e for e in spans if e["name"].lower() in line.lower()]
        
        # Connect only co-occurring entities in the same sentence/line
        for i in range(len(line_entities)):
            for j in range(i + 1, len(line_entities)):
                head = line_entities[i]
                tail = line_entities[j]

                pair_key = (head["id"], tail["id"])
                if pair_key in seen_pairs:
                    continue

                # Context snippet between the two entities
                idx_h = line.lower().find(head["name"].lower())
                idx_t = line.lower().find(tail["name"].lower())
                
                if idx_h < idx_t:
                    snippet = line[idx_h:idx_t + len(tail["name"])]
                else:
                    snippet = line[idx_t:idx_h + len(head["name"])]

                relation_type, confidence = determine_relation(head, tail, snippet)

                if relation_type and confidence >= threshold:
                    seen_pairs.add(pair_key)
                    rel_id = str(uuid.uuid4())

                    # Database models
                    rel_entry = Relationship(
                        id=rel_id,
                        document_id=document_id,
                        source_entity_id=head["id"],
                        target_entity_id=tail["id"],
                        relation_type=relation_type,
                        confidence_score=confidence
                    )
                    db_relationships.append(rel_entry)

                    evidence_entry = RelationshipEvidence(
                        id=str(uuid.uuid4()),
                        relationship_id=rel_id,
                        sentence_text=line[:300]
                    )
                    db_evidence.append(evidence_entry)

                    graph_edges.append({
                        "id": rel_id,
                        "source": str(head["id"]),
                        "target": str(tail["id"]),
                        "label": relation_type,
                        "weight": confidence
                    })

    # Nodes
    nodes = [
        {"id": str(e["id"]), "label": e.get("entity_name", ""), "type": e.get("entity_type", "")}
        for e in persisted_entities
    ]

    graph_payload = {"nodes": nodes, "edges": graph_edges}

    # Clean previous graph entries for idempotent processing
    existing_kg = db.query(KnowledgeGraph).filter(KnowledgeGraph.document_id == document_id).first()
    if existing_kg:
        existing_kg.graph_data = graph_payload
    else:
        db.add(KnowledgeGraph(
            id=str(uuid.uuid4()),
            document_id=document_id,
            graph_data=graph_payload
        ))

    try:
        db.query(Relationship).filter(Relationship.document_id == document_id).delete()
        db.bulk_save_objects(db_relationships)
        db.bulk_save_objects(db_evidence)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

    return graph_payload