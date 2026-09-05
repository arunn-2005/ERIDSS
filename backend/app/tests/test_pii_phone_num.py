from app.services.pii_detector import (
    detect_pii,
    mask_pii
)


text = """
Chief Information Security Officer Elena Rostova
Mobile: +44-7700-900821
Office: +1-415-555-0198
India: +91-98401-22394
"""


pii_results = detect_pii(text)

print("Detected PII:")
print(pii_results)

masked_text = mask_pii(
    text,
    pii_results
)

print("\nMasked Text:")
print(masked_text)