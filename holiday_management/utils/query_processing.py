import re
from typing import Dict

# Trip descriptions are free text, so allow common punctuation, currency and
# separators that show up in real requests ("5-day", "$2,000", "Paris/Rome").
ALLOWED_QUERY_PATTERN = re.compile(r"^[a-zA-Z0-9\s?@#\-_.,'\"()/:&%$€£!]+$")

STOP_WORDS = {
    "the", "is", "and", "or", "for", "a", "an", "to", "i", "want", "would",
    "like", "please", "can", "you", "help", "me", "with", "my", "we", "our",
}

# Normalise holiday vocabulary so equivalent requests share a signature.
SYNONYMS = {
    "holiday": "trip",
    "vacation": "trip",
    "getaway": "trip",
    "tour": "trip",
    "find": "search",
    "cheap": "budget",
    "affordable": "budget",
    "kids": "family",
    "children": "family",
    "luxurious": "luxury",
}


def validate_query(query: str) -> bool:
    """Validate a raw trip description. Raises ValueError on bad input."""
    if not query or len(query.strip()) < 5:
        raise ValueError("Trip description must be at least 5 characters long.")
    if not ALLOWED_QUERY_PATTERN.match(query):
        raise ValueError("Trip description contains invalid characters.")
    return True


def transform_query(query: str) -> Dict[str, str]:
    """Normalise a trip description and derive a stable signature for it."""
    normalized = re.sub(r"\s+", " ", query.strip().lower())

    tokens = normalized.split()
    tokens = [SYNONYMS.get(token, token) for token in tokens if token not in STOP_WORDS]
    cleaned_query = " ".join(tokens)

    return {
        "original": query,
        "normalized": normalized,
        "cleaned": cleaned_query,
        "signature": cleaned_query.replace(" ", "_"),
    }


def handle_query(query: str) -> Dict[str, str]:
    """Validate then transform a trip description in one call."""
    validate_query(query)
    return transform_query(query)
