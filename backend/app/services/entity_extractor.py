import re

from gliner import GLiNER


MODEL_NAME = "gliner-community/gliner_small-v2.5"


model = GLiNER.from_pretrained(MODEL_NAME)


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


def normalize_entity(entity_name: str):
    return entity_name.strip().lower()


def get_source_text(text: str, start: int, end: int):
    """
    Find the sentence containing the extracted entity.
    """

    # Find the beginning of the sentence
    sentence_start = max(
        text.rfind(".", 0, start),
        text.rfind("!", 0, start),
        text.rfind("?", 0, start),
        text.rfind("\n", 0, start)
    )

    # Move one character after the punctuation
    sentence_start += 1

    # Find the end of the sentence
    possible_ends = [
        text.find(".", end),
        text.find("!", end),
        text.find("?", end),
        text.find("\n", end)
    ]

    possible_ends = [
        position
        for position in possible_ends
        if position != -1
    ]

    if possible_ends:
        sentence_end = min(possible_ends) + 1
    else:
        sentence_end = len(text)

    return text[sentence_start:sentence_end].strip()


def extract_entities(text):

    results = model.predict_entities(
        text,
        ENTITY_LABELS,
        threshold=0.5
    )

    entities = []

    for entity in results:

        entity_name = entity["text"]

        entity_type = entity["label"]

        confidence_score = entity["score"]

        start = entity["start"]

        end = entity["end"]

        normalized_name = normalize_entity(
            entity_name
        )

        source_text = get_source_text(
            text,
            start,
            end
        )

        entities.append({
            "entity_name": entity_name,
            "normalized_name": normalized_name,
            "entity_type": entity_type,
            "confidence_score": confidence_score,
            "source_text": source_text,
            "start": start,
            "end": end
        })

    return entities