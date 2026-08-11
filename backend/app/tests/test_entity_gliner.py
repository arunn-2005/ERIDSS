from gliner import GLiNER


model = GLiNER.from_pretrained(
    "gliner-community/gliner_small-v2.5"
)


ENTITY_LABELS = [
    "person",
    "employee",
    "organization",
    "vendor",
    "customer",
    "department",
    "business unit",
    "project",
    "product",
    "service",
    "system",
    "software",
    "technology",
    "location",
    "contract",
    "policy",
    "process",
]


text = """
CONTRACT AGREEMENT

This Vendor Services Agreement is entered into between ABC Technologies Pvt. Ltd., headquartered in Chennai, and XYZ Corporation, headquartered in Bangalore.

ABC Technologies Pvt. Ltd. will provide cloud infrastructure and cybersecurity services for the Phoenix ERP Migration Project.

The contract is managed by Ravi Kumar, Senior Procurement Manager in the Finance and Procurement Department of XYZ Corporation.

The agreement begins on January 1, 2026, and remains valid until December 31, 2028.

Under this agreement, ABC Technologies will provide AWS cloud infrastructure, database management, security monitoring, and technical support.

The total contract value is INR 2.5 crore.

ABC Technologies must comply with the organization's information security policies and applicable data protection regulations.

The vendor must notify XYZ Corporation within 24 hours of discovering a security incident or unauthorized access to enterprise systems.

The contract also requires quarterly security audits and annual compliance assessments.

Failure to meet the agreed service levels may result in financial penalties of up to INR 10 lakh per incident.

The Finance Department is responsible for approving all vendor payments, while the IT Security Department is responsible for monitoring cybersecurity compliance.

The Phoenix ERP Migration Project depends on AWS infrastructure and Oracle Database services.

If ABC Technologies fails to provide the required services for more than 48 hours, XYZ Corporation may terminate the agreement.

All confidential business information, customer information, and employee information must be protected from unauthorized disclosure.

Any dispute arising from this agreement will be subject to the jurisdiction of the courts in Chennai.
"""


entities = model.predict_entities(
    text,
    ENTITY_LABELS,
    threshold=0.5
)


for entity in entities:

    print(
        entity["text"],
        "=>",
        entity["label"],
        "=>",
        entity["score"]
    )