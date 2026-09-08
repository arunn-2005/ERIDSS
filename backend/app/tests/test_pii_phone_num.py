import pytest
from app.services.pii_detector import detect_pii, mask_pii

SAMPLE_TEXT = """
Chief Information Security Officer Elena Rostova
Office: +1 415-555-0198
India: +91 9876543210
"""

def test_detect_pii_identifies_phone_numbers():
    results = detect_pii(SAMPLE_TEXT)
    assert isinstance(results, list)
    assert len(results) > 0

    pii_types = {item["pii_type"] for item in results}
    assert "PHONE_NUMBER" in pii_types

def test_mask_pii_redacts_phone_numbers():
    results = detect_pii(SAMPLE_TEXT)
    masked_text = mask_pii(SAMPLE_TEXT, results)

    assert isinstance(masked_text, str)
    assert "+91 9876543210" not in masked_text
    assert "[PHONE_NUMBER]" in masked_text