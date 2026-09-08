import pytest
from app.services.pii_detector import detect_pii, mask_pii

SAMPLE_TEXT = """
Employee information:

PAN: AXZPS4410K

Tax File Number: TFN-492-118-091

Aadhaar Number: [Aadhaar Redacted]

Employee: K. Sundaram
"""

def test_detect_pii_identifies_custom_identifiers():
    results = detect_pii(SAMPLE_TEXT)
    assert isinstance(results, list)
    assert len(results) > 0

    pii_types = {item["pii_type"] for item in results}
    # Verify that custom or standard recognizers captured key identifiers
    assert any(t in pii_types for t in ["IN_PAN", "PAN", "AADHAAR", "IN_AADHAAR", "PERSON", "CUSTOM_IDENTIFIER"])

def test_mask_pii_redacts_custom_identifiers():
    results = detect_pii(SAMPLE_TEXT)
    masked_text = mask_pii(SAMPLE_TEXT, results)

    assert isinstance(masked_text, str)
    # Check that sensitive identifiers are masked
    assert "AXZPS4410K" not in masked_text
    assert "TFN-492-118-091" not in masked_text