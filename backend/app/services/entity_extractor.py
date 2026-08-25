import re

from gliner import GLiNER

from app.services.entity_resolver import resolve_entities


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

PII_PLACEHOLDERS = {
    "PERSON",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "IP_ADDRESS",
    "URL",
    "LOCATION",
    "ACCOUNT_NUMBER",
    "GOVERNMENT_ID",
    "CREDIT_CARD"
}

GENERIC_ENTITIES = {
    "api",
    "database",
    "server",
    "system",
    "application",
    "software",
    "technology",
    "platform",
    "network"
}

def normalize_entity(entity_name: str):

    # Replace multiple spaces, tabs,
    # and newline characters with one space
    entity_name = re.sub(
        r"\s+",
        " ",
        entity_name
    )

    return entity_name.strip().lower()

def remove_repeated_words(entity_name: str):

    words = entity_name.split()

    cleaned_words = []

    for word in words:

        if not cleaned_words:
            cleaned_words.append(word)
            continue

        previous_word = cleaned_words[-1]

        if word.lower() == previous_word.lower():
            continue

        cleaned_words.append(word)

    return " ".join(cleaned_words)

def is_valid_entity(
    entity_name: str,
    entity_type: str,
    confidence_score: float
):

    # ---------------------------------
    # 1. Minimum confidence
    # ---------------------------------

    if confidence_score < 0.60:
        return False


    # ---------------------------------
    # 2. Normalize whitespace
    # ---------------------------------

    cleaned_name = re.sub(
        r"\s+",
        " ",
        entity_name
    ).strip()


    # ---------------------------------
    # 3. Remove empty entities
    # ---------------------------------

    if not cleaned_name:
        return False


    # ---------------------------------
    # 4. Remove PII placeholders
    # ---------------------------------

    placeholder_name = cleaned_name.strip(
        "[]"
    ).upper()

    if placeholder_name in PII_PLACEHOLDERS:
        return False


    # ---------------------------------
    # 5. Remove numeric-only entities
    # ---------------------------------

    if cleaned_name.isdigit():
        return False


    # ---------------------------------
    # 6. Remove generic entity names
    # ---------------------------------

    if cleaned_name.lower() in GENERIC_ENTITIES:
        return False


    return True

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

    # Keeps track of entities already seen
    seen_entities = set()

    for entity in results:

        entity_name = entity["text"]

        entity_type = entity["label"]

        confidence_score = entity["score"]

        start = entity["start"]

        end = entity["end"]


        # ---------------------------------
        # 1. Clean whitespace
        # ---------------------------------

        cleaned_entity_name = re.sub(
            r"\s+",
            " ",
            entity_name
        ).strip()


        # ---------------------------------
        # 2. Remove repeated words
        # ---------------------------------

        cleaned_entity_name = remove_repeated_words(
            cleaned_entity_name
        )


        # ---------------------------------
        # 3. Validate cleaned entity
        # ---------------------------------

        if not is_valid_entity(
            cleaned_entity_name,
            entity_type,
            confidence_score
        ):
            continue


        # ---------------------------------
        # 4. Normalize entity
        # ---------------------------------

        normalized_name = normalize_entity(
            cleaned_entity_name
        )


        # ---------------------------------
        # 5. Remove duplicates
        # ---------------------------------

        entity_key = (
            normalized_name,
            entity_type
        )

        if entity_key in seen_entities:
            continue

        seen_entities.add(entity_key)


        # ---------------------------------
        # 6. Get entity evidence
        # ---------------------------------

        source_text = get_source_text(
            text,
            start,
            end
        )


        # ---------------------------------
        # 7. Store entity
        # ---------------------------------

        entities.append({
            "entity_name": cleaned_entity_name,
            "normalized_name": normalized_name,
            "entity_type": entity_type,
            "confidence_score": confidence_score,
            "source_text": source_text,
            "start": start,
            "end": end
        })

    resolved_entities = resolve_entities(
        entities
    )

    return resolved_entities