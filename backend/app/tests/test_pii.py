from app.services.pii_detector import detect_pii, mask_pii


text = """
Notice of Vendor Non-Compliance: On August 14, 2024, an audit of the Data Ingestion Pipeline managed by Apex Global Solutions revealed multiple critical policy violations. The primary project lead, Rajesh Sharma (Employee ID: EMP-8821), operating under the Enterprise Risk Management division, shared unencrypted authentication credentials via email to rajesh.sharma@apexsol.co.in and cc'd senior auditor Clara Vance at cvance.audits@securenet.org. Emergency technical escalations were routed directly to mobile contact +91 98450 23149, with a secondary international callback logged at +1 (555) 319-7740.

Financial clearance documents submitted for the Q3 Oracle Cloud Migration contract (valued at $1,450,000) contained exposed tax identifiers, specifically corporate PAN number AAACR1234K and individual Aadhaar reference 4532 8901 2345. Additionally, the billing terminal logged payments originating from credit card number 4111 2024 9871 0042 (Exp: 11/27, CVV: 481) linked to a billing address at Flat 4B, Green Valley Heights, MG Road, Bengaluru, Karnataka 560001. System telemetry logs confirmed direct SSH access into the production server at IP address 192.168.10.45, where database admin credentials using password hash $argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ... were stored in plain text. Immediate remediation requires re-evaluating SLA Tier-1 agreements under the Cyber Threat Governance policy before September 1, 2024.
"""


results = detect_pii(text)

print("===== DETECTED PII =====")

for result in results:
    print(
        result["pii_type"],
        "=>",
        text[result["start"]:result["end"]],
        "=>",
        result["score"]
    )


sanitized_text = mask_pii(
    text,
    results
)

print("\n===== ORIGINAL TEXT =====")

print(text)

print("\n===== SANITIZED TEXT =====")

print(sanitized_text)