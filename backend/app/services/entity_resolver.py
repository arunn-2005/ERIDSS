import re


# ---------------------------------
# Organization suffixes
# ---------------------------------

ORGANIZATION_SUFFIXES = {
    "llc",
    "ltd",
    "limited",
    "inc",
    "inc.",
    "corp",
    "corp.",
    "corporation",
    "company",
    "co",
    "co.",
    "pvt",
    "private"
}


# ---------------------------------
# Create comparison name
# ---------------------------------

def get_comparison_name(
    entity_name: str,
    entity_type: str
):

    comparison_name = entity_name.lower().strip()

    comparison_name = re.sub(
        r"\s+",
        " ",
        comparison_name
    )


    # Remove organization suffixes
    # only for organization-like entities

    if entity_type in {
        "organization",
        "vendor",
        "customer"
    }:

        words = comparison_name.split()

        while (
            words
            and words[-1].strip(".")
            in ORGANIZATION_SUFFIXES
        ):
            words.pop()

        comparison_name = " ".join(words)


    return comparison_name


# ---------------------------------
# Check whether two entities match
# ---------------------------------

def are_same_entity(
    entity_one: dict,
    entity_two: dict
):

    # Don't merge different entity types

    if (
        entity_one["entity_type"]
        != entity_two["entity_type"]
    ):
        return False


    name_one = get_comparison_name(
        entity_one["entity_name"],
        entity_one["entity_type"]
    )

    name_two = get_comparison_name(
        entity_two["entity_name"],
        entity_two["entity_type"]
    )


    # Exact match

    if name_one == name_two:
        return True


    # Containment match

    if (
        name_one in name_two
        or name_two in name_one
    ):
        return True


    return False


# ---------------------------------
# Create evidence object
# ---------------------------------

def create_evidence(entity: dict):

    return {
        "source_text": entity["source_text"],
        "start": entity["start"],
        "end": entity["end"]
    }


# ---------------------------------
# Create resolved entity
# ---------------------------------

def create_resolved_entity(entity: dict):

    return {
        "entity_name": entity["entity_name"],
        "normalized_name": entity["normalized_name"],
        "entity_type": entity["entity_type"],
        "confidence_score": entity["confidence_score"],

        "evidence": [
            create_evidence(entity)
        ]
    }


# ---------------------------------
# Select canonical entity
# ---------------------------------

def select_canonical_entity(
    existing_entity: dict,
    new_entity: dict
):

    # Prefer longer entity name

    if (
        len(new_entity["entity_name"])
        >
        len(existing_entity["entity_name"])
    ):

        return new_entity

    return existing_entity


# ---------------------------------
# Resolve entities and preserve evidence
# ---------------------------------

def resolve_entities(entities: list):

    resolved_entities = []

    for entity in entities:

        matched_entity = None


        # ---------------------------------
        # Search existing resolved entities
        # ---------------------------------

        for resolved_entity in resolved_entities:

            if are_same_entity(
                entity,
                resolved_entity
            ):

                matched_entity = resolved_entity

                break


        # ---------------------------------
        # No match found
        # ---------------------------------

        if not matched_entity:

            resolved_entities.append(
                create_resolved_entity(entity)
            )

            continue


        # ---------------------------------
        # Match found
        # ---------------------------------

        canonical_entity = select_canonical_entity(
            matched_entity,
            entity
        )


        # Preserve new evidence

        matched_entity["evidence"].append(
            create_evidence(entity)
        )


        # Update canonical information if needed

        matched_entity["entity_name"] = (
            canonical_entity["entity_name"]
        )

        matched_entity["normalized_name"] = (
            canonical_entity["normalized_name"]
        )

        matched_entity["confidence_score"] = max(
            matched_entity["confidence_score"],
            entity["confidence_score"]
        )


    return resolved_entities