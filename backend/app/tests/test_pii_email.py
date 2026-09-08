import pytest
from app.services.pii_detector import detect_pii, mask_pii

SAMPLE_TEXT = """
Lead Investigator Dr. Aris Thorne
Email: aris.thorne@internal.com
"""

def test_detect_pii_identifies_email():
    results = detect_pii(SAMPLE_TEXT)
    assert isinstance(results, list)
    assert len(results) > 0

    pii_types = {item["pii_type"] for item in results}
    assert "EMAIL_ADDRESS" in pii_types

def test_mask_pii_redacts_email():
    results = detect_pii(SAMPLE_TEXT)
    masked_text = mask_pii(SAMPLE_TEXT, results)

    assert isinstance(masked_text, str)
    assert "aris.thorne@internal.com" not in masked_text
    assert any(token in masked_text for token in ["[EMAIL_ADDRESS]", "<EMAIL_ADDRESS>", "[REDACTED]"])