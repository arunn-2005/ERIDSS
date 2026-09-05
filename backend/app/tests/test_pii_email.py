from app.services.pii_detector import (
    detect_pii,
    mask_pii
)


text = """
Lead Investigator Dr. Aris Thorne
Email: aris.thorne@internal.com
"""


results = detect_pii(text)

print(results)

masked_text = mask_pii(
    text,
    results
)

print(masked_text)