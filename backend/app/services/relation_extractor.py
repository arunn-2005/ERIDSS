import uuid
import re
import spacy
from sqlalchemy.orm import Session
from app.models.relationship import Relationship, KnowledgeGraph

try:
    from app.models.relationship import RelationshipEvidence
except ImportError:
    class RelationshipEvidence:
        def __init__(self, **kwargs): pass

# Load spaCy parser once at startup
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


def extract_verb_predicate(doc, start_char_1, end_char_1, start_char_2, end_char_2):
    """
    Extracts the syntactic linking verb/predicate between two entity spans.
    Enforces strict Subject -> Object dependency roles and subordinate clause
    boundaries to prevent matrix verb bleed.
    """
    span1 = doc.char_span(start_char_1, end_char_1, alignment_mode="expand")
    span2 = doc.char_span(start_char_2, end_char_2, alignment_mode="expand")

    if not span1 or not span2:
        return None, None, 0.0

    root1 = span1.root
    root2 = span2.root

    # 1. Prefer immediate verbal head
    verb = None
    if root1.head.pos_ == "VERB":
        verb = root1.head
    elif root2.head.pos_ == "VERB":
        verb = root2.head
    else:
        # 2. Check closest common verbal ancestor within 3 tree hops
        ancestors1 = [a for a in list(root1.ancestors)[:3] if a.pos_ == "VERB"]
        ancestors2 = set(a for a in list(root2.ancestors)[:3] if a.pos_ == "VERB")
        for a in ancestors1:
            if a in ancestors2:
                verb = a
                break

    if not verb:
        return None, None, 0.0

    # 3. Subordinate clause boundary protection:
    # If either token has a closer intermediate verb ancestor, do not bind to the outer matrix verb
    for r in [root1, root2]:
        for anc in r.ancestors:
            if anc == verb:
                break
            if anc.pos_ == "VERB" and anc != verb:
                return None, None, 0.0

    # Grammatical dependency roles
    subj_deps = {"nsubj", "nsubjpass", "agent"}
    obj_deps = {"dobj", "pobj", "dative", "attr", "oprd", "appos"}

    dep1 = root1.dep_
    dep2 = root2.dep_
    head_dep1 = root1.head.dep_
    head_dep2 = root2.head.dep_

    is_head_subj = dep1 in subj_deps or head_dep1 in subj_deps
    is_tail_obj = dep2 in obj_deps or head_dep2 in obj_deps

    is_tail_subj = dep2 in subj_deps or head_dep2 in subj_deps
    is_head_obj = dep1 in obj_deps or head_dep1 in obj_deps

    # Enforce strict subject-predicate-object directionality
    if is_head_subj and is_tail_obj:
        direction = "forward"
    elif is_tail_subj and is_head_obj:
        direction = "reverse"
    else:
        return None, None, 0.0

    # Expand verb with attached particles/prepositions (e.g., "headquarter_in", "send_to")
    phrase = [verb.lemma_.lower()]
    for child in verb.children:
        if child.dep_ in ["prt", "prep"] and child.i > verb.i:
            phrase.append(child.lemma_.lower())
            for subchild in child.children:
                if subchild.dep_ == "prep":
                    phrase.append(subchild.lemma_.lower())
            break

    label = "_".join(phrase)
    label = re.sub(r"[^\w]+", "_", label).strip("_")

    return (label, direction, 0.90) if len(label) > 1 else (None, None, 0.0)


def extract_and_persist_relations(
    db: Session,
    document_id: str,
    text: str,
    persisted_entities: list,
    threshold: float = 0.5
):
    if len(persisted_entities) < 2:
        return {"nodes": [], "edges": []}

    doc = nlp(text)
    db_relationships = []
    db_evidence = []
    graph_edges = []
    seen_pairs = set()

    # Deduplicate entities by normalized name
    unique_entities = {}
    for ent in persisted_entities:
        name = ent.get("entity_name", "").strip()
        if not name:
            continue
        key = name.lower()
        if key not in unique_entities:
            unique_entities[key] = ent

    # Map entities to character spans in text
    entity_spans = []
    for ent in unique_entities.values():
        name = ent.get("entity_name", "").strip()
        matches = [m.start() for m in re.finditer(re.escape(name), text, re.IGNORECASE)]
        for start_idx in matches:
            entity_spans.append({
                "id": str(ent["id"]),
                "name": name,
                "type": ent.get("entity_type", "ENTITY"),
                "start": start_idx,
                "end": start_idx + len(name)
            })

    # Process relationships strictly sentence by sentence
    for sent in doc.sents:
        sent_entities = [
            e for e in entity_spans 
            if e["start"] >= sent.start_char and e["end"] <= sent.end_char
        ]

        if len(sent_entities) < 2:
            continue

        for i in range(len(sent_entities)):
            for j in range(i + 1, len(sent_entities)):
                head = sent_entities[i]
                tail = sent_entities[j]

                if head["id"] == tail["id"]:
                    continue

                pair_key = (head["id"], tail["id"]) if head["id"] < tail["id"] else (tail["id"], head["id"])
                if pair_key in seen_pairs:
                    continue

                predicate_label, direction, confidence = extract_verb_predicate(
                    doc, head["start"], head["end"], tail["start"], tail["end"]
                )

                if predicate_label and confidence >= threshold:
                    seen_pairs.add(pair_key)
                    rel_id = str(uuid.uuid4())

                    src_id = head["id"] if direction == "forward" else tail["id"]
                    tgt_id = tail["id"] if direction == "forward" else head["id"]

                    rel_entry = Relationship(
                        id=rel_id,
                        document_id=document_id,
                        source_entity_id=src_id,
                        target_entity_id=tgt_id,
                        relation_type=predicate_label,
                        confidence_score=confidence
                    )
                    db_relationships.append(rel_entry)

                    evidence_entry = RelationshipEvidence(
                        id=str(uuid.uuid4()),
                        relationship_id=rel_id,
                        sentence_text=sent.text.strip()[:500]
                    )
                    db_evidence.append(evidence_entry)

                    graph_edges.append({
                        "id": rel_id,
                        "source": src_id,
                        "target": tgt_id,
                        "label": predicate_label,
                        "weight": confidence
                    })

    # Nodes
    nodes = [
        {"id": str(e["id"]), "label": e.get("entity_name", ""), "type": e.get("entity_type", "")}
        for e in unique_entities.values()
    ]

    graph_payload = {"nodes": nodes, "edges": graph_edges}

    # Upsert knowledge graph
    existing_kg = db.query(KnowledgeGraph).filter(KnowledgeGraph.document_id == document_id).first()
    if existing_kg:
        existing_kg.graph_data = graph_payload
    else:
        db.add(KnowledgeGraph(
            id=str(uuid.uuid4()),
            document_id=document_id,
            graph_data=graph_payload
        ))

    # Commit transactions
    try:
        db.query(Relationship).filter(Relationship.document_id == document_id).delete()
        db.bulk_save_objects(db_relationships)
        db.bulk_save_objects(db_evidence)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

    return graph_payload