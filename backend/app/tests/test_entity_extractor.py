import pytest
from app.services.entity_extractor import extract_entities

SAMPLE_TEXT = """
Apple signed a contract with Microsoft.
John Smith will manage Project Phoenix.
The Finance Department approved a budget of $500,000.
The project will start in Chennai on January 15, 2027.
"""

def test_extract_entities_returns_results():
    entities = extract_entities(SAMPLE_TEXT)

    # 1. Output must be a list and contain items
    assert isinstance(entities, list)
    assert len(entities) > 0

    # 2. Check exact keys produced by the extractor schema
    first_entity = entities[0]
    assert "entity_name" in first_entity
    assert "entity_type" in first_entity
    assert "confidence_score" in first_entity
    assert first_entity["entity_name"] is not None


def test_extract_entities_identifies_key_targets():
    entities = extract_entities(SAMPLE_TEXT)

    # Collect extracted entity names using the schema key
    found_names = [e["entity_name"].lower() for e in entities if "entity_name" in e]

    # Verify extraction targets
    expected_entities = ["apple", "microsoft", "john smith", "project phoenix", "chennai", "finance department"]
    assert any(any(exp in found for found in found_names) for exp in expected_entities)