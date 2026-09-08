import re

from presidio_analyzer import (
    AnalyzerEngine,
    Pattern,
    PatternRecognizer
)


# ---------------------------------
# Initialize Presidio Analyzer
# ---------------------------------

analyzer = AnalyzerEngine()

phone_pattern = Pattern(
    name="international_phone_pattern",
    regex=r"(?<![\w-])(?:\+\d{1,3}[-.\s]?)?(?:\(\d{2,4}\)[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}(?![\w-])",
    score=0.95
)

phone_recognizer = PatternRecognizer(
    supported_entity="PHONE_NUMBER",
    patterns=[phone_pattern]
)

analyzer.registry.add_recognizer(
    phone_recognizer
)

indian_phone_pattern = Pattern(
    name="indian_phone_pattern",
    regex=r"(?<!\w)\+91[\s.-]?[6-9]\d{9}(?!\w)",
    score=1.0
)

indian_phone_recognizer = PatternRecognizer(
    supported_entity="PHONE_NUMBER",
    patterns=[indian_phone_pattern]
)

analyzer.registry.add_recognizer(
    indian_phone_recognizer
)


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
# Custom sensitive identifier patterns
# ---------------------------------

CUSTOM_PII_PATTERNS = {
    "INDIAN_PAN": re.compile(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        re.IGNORECASE
    ),

    "TAX_FILE_NUMBER": re.compile(
        r"\bTFN-\d{3}-\d{3}-\d{3}\b",
        re.IGNORECASE
    ),

    "AADHAAR_NUMBER": re.compile(
        r"\b\d{4}\s\d{4}\s\d{4}\b"
    ),

    "US_SSN": re.compile(
        r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"
    ),
}

PII_PRIORITY = {
    "EMAIL_ADDRESS": 100,
    "CREDIT_CARD": 98,
    "PHONE_NUMBER": 95,
    "PASSPORT": 92,
    "US_DRIVER_LICENSE": 92,
    "US_BANK_NUMBER": 90,
    "INDIAN_PAN": 90,
    "AADHAAR_NUMBER": 90,
    "TAX_FILE_NUMBER": 90,
    "IP_ADDRESS": 85,
    "UK_NHS": 85,
    "URL": 50,
    "PERSON": 40,
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
    "INDIAN_PAN",
    "AADHAAR_NUMBER",
    "TAX_FILE_NUMBER",
}


# ---------------------------------
# Minimum confidence score
# ---------------------------------

MINIMUM_PII_SCORE = 0.5

def is_inside_email(
    text: str,
    start: int,
    end: int
) -> bool:

    email_pattern = re.compile(
        r"[A-Za-z0-9._%+-]+"
        r"@"
        r"[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}"
    )

    for match in email_pattern.finditer(text):

        email_start = match.start()
        email_end = match.end()

        if (
            start >= email_start
            and end <= email_end
        ):
            return True

    return False

def detect_custom_pii(text: str):
    custom_results = []

    for pii_type, pattern in CUSTOM_PII_PATTERNS.items():

        for match in pattern.finditer(text):

            custom_results.append({
                "pii_type": pii_type,
                "start": match.start(),
                "end": match.end(),
                "score": 1.0
            })

    return custom_results

def detect_email_pii(text: str):
    results = []

    email_pattern = re.compile(
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}\b"
    )

    for match in email_pattern.finditer(text):
        results.append({
            "pii_type": "EMAIL_ADDRESS",
            "start": match.start(),
            "end": match.end(),
            "score": 1.0
        })

    return results

def detect_phone_pii(text: str):
    results = []

    phone_pattern = re.compile(
        r"(?<![\w-])"
        r"(?:\+\d{1,3}[-.\s]?)?"
        r"\d{3}[-.\s]?\d{3}[-.\s]?\d{4}"
        r"(?![\w-])"
    )

    for match in phone_pattern.finditer(text):

        value = match.group()

        if not is_valid_phone_value(
            text,
            match.start(),
            match.end()
        ):
            continue

        results.append({
            "pii_type": "PHONE_NUMBER",
            "start": match.start(),
            "end": match.end(),
            "score": 1.0
        })

    return results

def detect_credit_card_pii(text: str):
    results = []

    credit_card_pattern = re.compile(
        r"(?<!\d)"
        r"(?:\d{4}[-\s]?){3}\d{4}"
        r"(?!\d)"
    )

    for match in credit_card_pattern.finditer(text):

        value = match.group()

        digits = re.sub(r"\D", "", value)

        if len(digits) not in {13, 14, 15, 16, 19}:
            continue

        results.append({
            "pii_type": "CREDIT_CARD",
            "start": match.start(),
            "end": match.end(),
            "score": 1.0
        })

    return results

def detect_contextual_pii(text: str):
    results = []

    # ---------------------------------
    # Passport Number
    # ---------------------------------

    passport_pattern = re.compile(
        r"(?i)\bPassport\s+Number\s*:\s*([A-Z]\d{7})\b"
    )

    for match in passport_pattern.finditer(text):

        number_start = match.start(1)
        number_end = match.end(1)

        results.append({
            "pii_type": "PASSPORT",
            "start": number_start,
            "end": number_end,
            "score": 1.0
        })

    # ---------------------------------
    # Corporate account numbers
    # ---------------------------------

    account_pattern = re.compile(
        r"(?i)\b(?:account\s+number|account\s+no\.?|a/c)"
        r"\s*[:#-]?\s*(\d{8,20})\b"
    )

    for match in account_pattern.finditer(text):

        number_start = match.start(1)
        number_end = match.end(1)

        results.append({
            "pii_type": "US_BANK_NUMBER",
            "start": number_start,
            "end": number_end,
            "score": 1.0
        })

    # ---------------------------------
    # Explicit US Bank Number
    # ---------------------------------

    bank_pattern = re.compile(
        r"(?i)\bUS\s+Bank\s+Number\s*:\s*(\d{8,20})\b"
    )

    for match in bank_pattern.finditer(text):

        number_start = match.start(1)
        number_end = match.end(1)

        results.append({
            "pii_type": "US_BANK_NUMBER",
            "start": number_start,
            "end": number_end,
            "score": 1.0
        })

    return results

def is_valid_phone_value(text: str, start: int, end: int) -> bool:
    value = text[start:end].strip()

    # Remove formatting characters to count digits
    digits = re.sub(r"\D", "", value)

    # A normal phone number should contain at least 10 digits
    if len(digits) < 10:
        return False

    # Reject date/document-ID-like patterns such as:
    # 2026-001
    if re.fullmatch(r"\d{4}-\d{3}", value):
        return False

    # Reject obvious numeric identifiers that are too short
    if len(digits) < 10:
        return False

    return True

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
        # Confidence filtering
        # ---------------------------------

        if result.score < MINIMUM_PII_SCORE:
            continue


        # ---------------------------------
        # Keep only allowed PII types
        # ---------------------------------

        if (
            result.entity_type
            not in ALLOWED_PII_ENTITIES
            and result.entity_type != "URL"
        ):
            continue


        # ---------------------------------
        # Prevent URL fragments inside email
        # ---------------------------------

        if result.entity_type == "URL":

            if is_inside_email(
                text,
                result.start,
                result.end
            ):
                continue


        # ---------------------------------
        # Validate PHONE_NUMBER
        # ---------------------------------

        if result.entity_type == "PHONE_NUMBER":

            if not is_valid_phone_value(
                text,
                result.start,
                result.end
            ):
                continue

        # ---------------------------------
        # Validate PERSON
        # ---------------------------------

        if result.entity_type == "PERSON":

            person_value = text[
                result.start:result.end
            ]

            if not is_valid_person_value(
                person_value
            ):
                continue


        # ---------------------------------
        # Store detected PII
        # ---------------------------------

        pii_results.append({
            "pii_type": result.entity_type,
            "start": result.start,
            "end": result.end,
            "score": result.score
        })

    # ---------------------------------
    # Add custom regex-based PII
    # ---------------------------------

    # ---------------------------------
    # Add explicit email detection
    # ---------------------------------

    email_pii_results = detect_email_pii(text)

    pii_results.extend(email_pii_results)


    # ---------------------------------
    # Add explicit phone detection
    # ---------------------------------

    phone_pii_results = detect_phone_pii(text)

    pii_results.extend(phone_pii_results)


    # ---------------------------------
    # Add explicit credit card detection
    # ---------------------------------

    credit_card_pii_results = detect_credit_card_pii(text)

    pii_results.extend(credit_card_pii_results)


    # ---------------------------------
    # Add custom regex-based PII
    # ---------------------------------

    custom_pii_results = detect_custom_pii(text)

    pii_results.extend(custom_pii_results)


    # ---------------------------------
    # Add contextual PII
    # ---------------------------------

    contextual_pii_results = detect_contextual_pii(text)

    pii_results.extend(contextual_pii_results)


    # ---------------------------------
    # Remove overlapping PII
    # ---------------------------------

    pii_results = remove_overlapping_results(
        pii_results
    )

    pii_results = remove_duplicate_results(
        pii_results
    )

    return pii_results


# ---------------------------------
# Mask sensitive PII
# ---------------------------------

def mask_pii(text: str, pii_results: list):
    masked_text = text

    for result in sorted(
        pii_results,
        key=lambda x: x["start"],
        reverse=True
    ):
        pii_type = result["pii_type"]

        if pii_type not in MASKED_PII_TYPES:
            continue

        if result.get("score", 0.0) < MINIMUM_PII_SCORE:
            continue

        start = result["start"]
        end = result["end"]

        replacement = get_pii_replacement(
            pii_type,
            text[start:end]
        )

        masked_text = (
            masked_text[:start]
            + replacement
            + masked_text[end:]
        )

    return masked_text

# ---------------------------------
# Remove overlapping PII detections
# ---------------------------------

def remove_overlapping_results(pii_results: list):
    """
    Remove overlapping PII detections.

    When multiple PII recognizers detect overlapping text,
    the detection with the higher priority wins.

    If priorities are equal, the longer detection wins.
    """

    sorted_results = sorted(
        pii_results,
        key=lambda result: (
            PII_PRIORITY.get(result["pii_type"], 0),
            result["end"] - result["start"]
        ),
        reverse=True
    )

    selected_results = []

    for result in sorted_results:
        start = result["start"]
        end = result["end"]

        overlaps = False

        for selected in selected_results:
            selected_start = selected["start"]
            selected_end = selected["end"]

            if start < selected_end and end > selected_start:
                overlaps = True
                break

        if not overlaps:
            selected_results.append(result)

    return sorted(
        selected_results,
        key=lambda result: result["start"]
    )

def remove_duplicate_results(pii_results: list):
    """
    Remove exact duplicate PII detections.

    Detections are considered duplicates only when
    they have the same PII type and exactly the same
    start/end positions.

    Separate occurrences of the same value are preserved.
    """

    unique_results = []
    seen = set()

    for result in pii_results:

        key = (
            result["pii_type"],
            result["start"],
            result["end"]
        )

        if key in seen:
            continue

        seen.add(key)
        unique_results.append(result)

    return unique_results

# ---------------------------------
# Get replacement for detected PII
# ---------------------------------

def get_pii_replacement(
    pii_type: str,
    original_value: str
):

    replacements = {
        "EMAIL_ADDRESS": "[EMAIL_ADDRESS]",
        "PHONE_NUMBER": "[PHONE_NUMBER]",
        "IP_ADDRESS": "[IP_ADDRESS]",
        "URL": "[URL]",
        "CREDIT_CARD": "[CREDIT_CARD]",
        "US_SSN": "[SSN]",
        "US_BANK_NUMBER": "[ACCOUNT_NUMBER]",
        "US_DRIVER_LICENSE": "[GOVERNMENT_ID]",
        "PASSPORT": "[PASSPORT]",
        "UK_NHS": "[GOVERNMENT_ID]",
        "INDIAN_PAN": "[INDIAN_PAN]",
        "AADHAAR_NUMBER": "[AADHAAR_NUMBER]",
        "TAX_FILE_NUMBER": "[TAX_FILE_NUMBER]",
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