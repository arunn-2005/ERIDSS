import pytest
from app.services.relation_extractor import align_char_to_tokens, rel_model, RELATION_LABELS
def test_char_to_token_alignment():
    text = "The Analytics Service depends_on the Database cluster."
    entities = [
        {"entity_name": "Analytics Service", "entity_type": "Service", "start": 4, "end": 21},
        {"entity_name": "Database cluster", "entity_type": "Infrastructure", "start": 37, "end": 53}
    ]
    
    tokens, ner_spans = align_char_to_tokens(text, entities)
    
    assert len(tokens) > 0
    assert len(ner_spans) == 2
    # Check that the token span text matches the entity names
    assert ner_spans[0][3] == "Analytics Service"
    assert ner_spans[1][3] == "Database cluster"

def test_glirel_relation_extraction():
    text = "The Analytics Service depends on the PostgreSQL cluster."
    # Token-level input for quick verification
    tokens = text.split()
    ner_spans = [
        [1, 3, "Service", "Analytics Service"],
        [5, 7, "Technology", "PostgreSQL cluster"]
    ]
    
    relations = rel_model.predict_relations(
        tokens=tokens,
        labels=["depends_on", "uses", "managed_by"],
        threshold=0.3,
        ner=ner_spans,
        top_k=1
    )
    
    assert isinstance(relations, list)
    if relations:
        assert relations[0]["label"] in ["depends_on", "uses"]
        assert relations[0]["score"] >= 0.3