import re

from gliner import GLiNER

from app.services.entity_resolver import resolve_entities
from app.services.entity_type_normalizer import normalize_entity_type

MODEL_NAME = "gliner-community/gliner_medium-v2.5"
model = GLiNER.from_pretrained(MODEL_NAME)

# ---------------------------------
# Text chunking configuration
# ---------------------------------

CHUNK_SIZE = 250
CHUNK_OVERLAP = 50

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
    "CREDIT_CARD",
    "INDIAN_PAN",
    "TAX_FILE_NUMBER",
    "AADHAAR_NUMBER",
    "US_SSN",
    "US_BANK_NUMBER",
    "US_DRIVER_LICENSE",
    "PASSPORT",
    "UK_NHS",
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
    # 5. Reject entities containing
    # PII placeholder patterns
    # ---------------------------------

    for placeholder in PII_PLACEHOLDERS:

        placeholder_pattern = f"[{placeholder}]"

        if placeholder_pattern.lower() in cleaned_name.lower():
            return False


    # ---------------------------------
    # 6. Remove numeric-only entities
    # ---------------------------------

    if cleaned_name.isdigit():
        return False


    # ---------------------------------
    # 7. Remove generic entity names
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

def chunk_text(text: str):
    """
    Split text into overlapping word-based chunks.

    Each chunk contains up to CHUNK_SIZE words.
    Consecutive chunks overlap by CHUNK_OVERLAP words.

    The character position of each chunk in the
    original document is also stored.
    """

    words = list(
        re.finditer(r"\S+", text)
    )

    if not words:
        return []

    chunks = []

    start_word = 0

    step = CHUNK_SIZE - CHUNK_OVERLAP

    while start_word < len(words):

        end_word = min(
            start_word + CHUNK_SIZE,
            len(words)
        )

        chunk_start = words[start_word].start()
        chunk_end = words[end_word - 1].end()

        chunk = text[chunk_start:chunk_end]

        chunks.append({
            "text": chunk,
            "start_char": chunk_start,
            "end_char": chunk_end
        })

        start_word += step

# --- Outdent these lines outside the while loop ---
    print(f"\n--- GLiNER Chunking Debug ---")
    print(f"Total words: {len(words)}")
    print(f"Total chunks created: {len(chunks)}")

    for index, chunk_info in enumerate(chunks, start=1):
        print(
            f"Chunk {index}: "
            f"chars {chunk_info['start_char']} → {chunk_info['end_char']} "
            f"({len(chunk_info['text'].split())} words)"
        )
    print(f"------------------------------\n")

    return chunks

def extract_entities(text):

    chunks = chunk_text(text)

    results = []

    for chunk in chunks:

        chunk_results = model.predict_entities(
            chunk["text"],
            ENTITY_LABELS,
            threshold=0.5,
            max_len = 512
        )

        for entity in chunk_results:

            entity["start"] = (
                entity["start"]
                + chunk["start_char"]
            )

            entity["end"] = (
                entity["end"]
                + chunk["start_char"]
            )

            results.append(entity)

    entities = []

    for entity in results:

        entity_name = entity["text"]

        raw_entity_type = entity["label"]

        entity_type = normalize_entity_type(
            raw_entity_type
        )

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
        # 5. Merge duplicate entities
        # Keep the highest-confidence result
        # ---------------------------------

        entity_key = (
            normalized_name,
            entity_type
        )

        existing_entity = next(
            (
                existing
                for existing in entities
                if (
                    existing["normalized_name"],
                    existing["entity_type"]
                ) == entity_key
            ),
            None
        )

        if existing_entity:

            if confidence_score > existing_entity["confidence_score"]:
                existing_entity.update({
                    "entity_name": cleaned_entity_name,
                    "raw_entity_type": raw_entity_type,
                    "confidence_score": confidence_score,
                    "source_text": get_source_text(
                        text,
                        start,
                        end
                    ),
                    "start": start,
                    "end": end
                })

            continue


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
            "raw_entity_type": raw_entity_type,
            "confidence_score": confidence_score,
            "source_text": source_text,
            "start": start,
            "end": end
        })

    resolved_entities = resolve_entities(
        entities
    )

    return resolved_entities