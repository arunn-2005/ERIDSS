from presidio_analyzer import AnalyzerEngine


# ---------------------------------
# Initialize Presidio Analyzer
# ---------------------------------

analyzer = AnalyzerEngine()


# ---------------------------------
# Supported PII types
# ---------------------------------

ALLOWED_PII_ENTITIES = {
    "PERSON",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "IP_ADDRESS",
    "CREDIT_CARD",
    "US_SSN",
    "US_BANK_NUMBER",
    "US_DRIVER_LICENSE",
    "PASSPORT",
    "URL",
    "UK_NHS",
}


# ---------------------------------
# PII types that should be masked
# ---------------------------------

MASKED_PII_TYPES = {
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "IP_ADDRESS",
    "CREDIT_CARD",
    "US_SSN",
    "US_BANK_NUMBER",
    "US_DRIVER_LICENSE",
    "PASSPORT",
    "URL",
    "UK_NHS",
}


# ---------------------------------
# Minimum confidence score
# ---------------------------------

MINIMUM_PII_SCORE = 0.5


# ---------------------------------
# Detect PII
# ---------------------------------

def detect_pii(text: str):

    results = analyzer.analyze(
        text=text,
        language="en"
    )

    pii_results = []

    for result in results:

        # ---------------------------------
        # Ignore unsupported PII types
        # ---------------------------------

        if result.entity_type not in ALLOWED_PII_ENTITIES:
            continue


        # ---------------------------------
        # Ignore low-confidence results
        # ---------------------------------

        if result.score < MINIMUM_PII_SCORE:
            continue


        # Extract the detected value
        detected_value = text[
            result.start:result.end
        ]


        # ---------------------------------
        # Validate PERSON detection
        # ---------------------------------

        if result.entity_type == "PERSON":

            if not is_valid_person_value(
                detected_value
            ):
                continue


        # Store clean PII result

        pii_results.append({
            "pii_type": result.entity_type,
            "start": result.start,
            "end": result.end,
            "score": result.score
        })


    # ---------------------------------
    # Remove overlapping detections
    # ---------------------------------

    pii_results = remove_overlapping_results(
        pii_results
    )


    return pii_results


# ---------------------------------
# Mask sensitive PII
# ---------------------------------

def mask_pii(
    text: str,
    pii_results: list
):

    masked_text = text


    # ---------------------------------
    # Process from right to left
    #
    # This prevents index positions from
    # changing after text replacement.
    # ---------------------------------

    for result in sorted(
        pii_results,
        key=lambda x: x["start"],
        reverse=True
    ):

        pii_type = result["pii_type"]


        # ---------------------------------
        # Keep PERSON information
        #
        # PERSON entities are useful for
        # enterprise entity extraction.
        # ---------------------------------

        if pii_type == "PERSON":
            continue


        # ---------------------------------
        # Only mask configured PII types
        # ---------------------------------

        if pii_type not in MASKED_PII_TYPES:
            continue


        start = result["start"]
        end = result["end"]


        # Original detected PII value

        original_value = text[start:end]


        # Get replacement value

        replacement = get_pii_replacement(
            pii_type=pii_type,
            original_value=original_value
        )


        # Replace PII

        masked_text = (
            masked_text[:start]
            + replacement
            + masked_text[end:]
        )


    return masked_text


# ---------------------------------
# Remove overlapping PII detections
# ---------------------------------

def remove_overlapping_results(
    pii_results: list
):

    # ---------------------------------
    # Sort by:
    #
    # 1. Start position
    # 2. Longer detection first
    # 3. Higher confidence first
    # ---------------------------------

    sorted_results = sorted(
        pii_results,
        key=lambda x: (
            x["start"],
            -(x["end"] - x["start"]),
            -x["score"]
        )
    )


    selected_results = []


    for result in sorted_results:

        overlap = False


        for selected in selected_results:

            # ---------------------------------
            # Check whether two ranges overlap
            # ---------------------------------

            if (
                result["start"] < selected["end"]
                and result["end"] > selected["start"]
            ):

                overlap = True
                break


        # ---------------------------------
        # Keep only non-overlapping result
        # ---------------------------------

        if not overlap:

            selected_results.append(
                result
            )


    return selected_results


# ---------------------------------
# Get replacement for detected PII
# ---------------------------------

def get_pii_replacement(
    pii_type: str,
    original_value: str
):

    replacements = {

        "EMAIL_ADDRESS":
            "[EMAIL_ADDRESS]",

        "PHONE_NUMBER":
            "[PHONE_NUMBER]",

        "IP_ADDRESS":
            "[IP_ADDRESS]",

        "URL":
            "[URL]",

        "CREDIT_CARD":
            "[CREDIT_CARD]",

        "US_SSN":
            "[SSN]",

        "US_BANK_NUMBER":
            "[ACCOUNT_NUMBER]",

        "US_DRIVER_LICENSE":
            "[GOVERNMENT_ID]",

        "PASSPORT":
            "[PASSPORT]",

        "UK_NHS":
            "[GOVERNMENT_ID]",
    }


    # ---------------------------------
    # Return predefined replacement
    # ---------------------------------

    if pii_type in replacements:

        return replacements[pii_type]


    # ---------------------------------
    # Default replacement
    # ---------------------------------

    return f"[{pii_type}]"


# ---------------------------------
# Validate PERSON detections
# ---------------------------------

def is_valid_person_value(
    value: str
) -> bool:

    # Remove extra spaces

    value = " ".join(
        value.split()
    )


    # Empty value

    if not value:
        return False


    # ---------------------------------
    # Invalid words
    #
    # These commonly appear when the
    # PERSON recognizer incorrectly
    # detects phrases as a person's name.
    # ---------------------------------

    invalid_words = {

        "email",
        "phone",
        "number",
        "address",
        "department",
        "project",
        "company",
        "organization",
        "employee",
        "manager",
        "vendor",
        "customer",
        "system",
        "software",
        "technology",
        "infrastructure",
        "account",
        "password",
        "server",
        "database",
        "api",
    }


    words = value.lower().split()


    # ---------------------------------
    # Reject invalid words
    # ---------------------------------

    for word in words:

        cleaned_word = (
            word
            .strip()
            .strip(".,:;()[]{}")
        )


        if cleaned_word in invalid_words:

            return False


    # ---------------------------------
    # PERSON should normally contain
    # alphabetic characters
    # ---------------------------------

    if not any(
        char.isalpha()
        for char in value
    ):

        return False


    return True