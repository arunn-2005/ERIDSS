# app/services/entity_type_normalizer.py


ENTITY_TYPE_MAP = {
    # People
    "person": "person",
    "employee": "employee",

    # Organizations / business
    "organization": "organization",
    "vendor": "vendor",
    "customer": "customer",
    "department": "department",
    "business unit": "business_unit",

    # Business objects
    "project": "project",
    "product": "product",
    "service": "service",
    "contract": "contract",
    "policy": "policy",
    "process": "process",

    # Technology
    "system": "system",
    "software": "technology",
    "technology": "technology",
}


def normalize_entity_type(entity_type: str) -> str:
    """
    Convert a raw GLiNER entity type into
    the controlled ERIDSS entity type.
    """

    if not entity_type:
        return "unknown"

    normalized_type = entity_type.strip().lower()

    return ENTITY_TYPE_MAP.get(
        normalized_type,
        normalized_type
    )