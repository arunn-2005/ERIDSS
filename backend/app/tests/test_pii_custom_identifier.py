from app.services.pii_detector import (
    detect_pii,
    mask_pii
)


text = """
Employee information:

PAN: AXZPS4410K

Tax File Number: TFN-492-118-091

Aadhaar Number: 1234 5678 9012

Employee: K. Sundaram
"""


pii_results = detect_pii(text)

print("Detected PII:")
print(pii_results)


masked_text = mask_pii(
    text,
    pii_results
)

print("\nMasked Text:\n")
print(masked_text)