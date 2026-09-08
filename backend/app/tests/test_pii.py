import pytest
from app.services.pii_detector import detect_pii, mask_pii


text = """
ENTERPRISE TECHNOLOGY MIGRATION AND RISK ASSESSMENT REPORT

Document ID: ERIDSS-TEST-2026-001
Classification: Confidential

Project Hyperion is an enterprise modernization initiative led by the Global Clearing & Enterprise Modernization Division.

The project is managed by Sophia Chen, Senior Technology Program Manager. Sophia Chen coordinates with Nexus Cloud Solutions LLC and CloudScale Systems GmbH for infrastructure and application modernization activities.

The current architecture uses Apache Kafka for event streaming, Kubernetes for container orchestration, and PostgreSQL for transactional data storage. The Core Settlement Pipeline depends on Apache Kafka and PostgreSQL for processing settlement transactions.

Nexus Cloud Solutions LLC is responsible for the API gateway modernization work. CloudScale Systems GmbH provides Kubernetes infrastructure support.

The project team is also evaluating PostgreSQL Core as part of the database modernization program. The Enterprise Data Division is responsible for reviewing the migration strategy and approving the final architecture.

For project communications, Sophia Chen can be contacted at sophia.chen@example.com or +91 9876543210.

The infrastructure administrator reported the following server information:
Server IP address: 192.168.1.25
Backup server IP address: 10.20.30.40
Monitoring portal: https://monitoring.example.com/project-hyperion

The procurement team recorded the following sensitive identifiers for the vendor onboarding process:
Indian PAN: ABCDE1234F
Aadhaar Number: 1234 5678 9012
Tax File Number: TFN-123-456-789
Passport Number: A1234567

The finance team also recorded a test corporate account number: 1234567890123456.

The compliance team maintains the following records:
US SSN: 123-45-6789
US Bank Number: 123456789
US Driver License: D1234567
UK NHS Number: 943 476 5919
Credit Card Number: 4111 1111 1111 1111

During the migration review, the team identified the following risks:

1. Dependency on Apache Kafka availability may affect the Core Settlement Pipeline.
2. Kubernetes configuration errors may interrupt application services.
3. PostgreSQL migration failures may affect transaction processing.
4. Vendor service outages could delay Project Hyperion.
5. Inadequate access controls could expose confidential enterprise information.

The Global Clearing & Enterprise Modernization Division will conduct a final architecture review before production deployment.

The review will involve Sophia Chen, Nexus Cloud Solutions LLC, CloudScale Systems GmbH, the Enterprise Data Division, and the infrastructure operations team.

Additional contact information:
Email: security-team@example.org
Phone: +1 555-234-5678
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