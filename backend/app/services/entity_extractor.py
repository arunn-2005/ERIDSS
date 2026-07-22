import spacy


nlp = spacy.load("en_core_web_sm")


ENTITY_TYPE_MAPPING = {
    "PERSON": "Person",
    "ORG": "Organization",
    "GPE": "Location",
    "LOC": "Location",
    "PRODUCT": "Product",
    "DATE": "Date",
    "MONEY": "Money",
    "EVENT": "Event",
    "LAW": "Law"
}


def normalize_entity(entity_name: str):
    return entity_name.strip().lower()


def extract_entities(text: str):

    doc = nlp(text)

    entities = []

    for ent in doc.ents:

        entity_type = ENTITY_TYPE_MAPPING.get(
            ent.label_,
            "Other"
        )

        normalized_name = normalize_entity(
            ent.text
        )

        source_text = ent.sent.text.strip()

        entities.append({
            "entity_name": ent.text,
            "normalized_name": normalized_name,
            "entity_type": entity_type,
            "source_text": source_text
        })

    return entities