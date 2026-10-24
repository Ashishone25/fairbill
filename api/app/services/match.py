"""Code matching service stub.

Matches extracted medical procedure and supply descriptions to standardized
CPT, HCPCS, and DRG billing codes using embedding similarity and
scikit-learn classifiers.
"""

import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from rapidfuzz import fuzz, process

from app.services.reference import ReferencePriceRecord


class MatchResult(BaseModel):
    best_match: Optional[ReferencePriceRecord] = None
    score: float
    reason: str


def normalise_item_name(name: str) -> str:
    """
    Normalize item name by lowercasing, stripping strengths, pack words,
    and handling common abbreviations.
    """
    name = name.lower().strip()

    # Common abbreviations
    abbrevs = {
        "inj": "injection",
        "syr": "syrup",
        "tab": "tablet",
        "cap": "capsule",
        "oint": "ointment",
        "susp": "suspension",
        "sol": "solution",
        "pck": "pack",
        "pkt": "packet",
    }

    # Strip strengths like 500mg, 10ml, 500 mg, 10 ml
    name = re.sub(r"\b\d+(\.\d+)?\s*(mg|ml|g|mcg|iu|u)\b", "", name)

    # Split into words to handle replacements and pack words
    words = name.split()

    pack_words = {
        "tablet",
        "capsule",
        "injection",
        "syrup",
        "ointment",
        "suspension",
        "solution",
        "pack",
        "packet",
        "tab",
        "cap",
        "inj",
        "syr",
    }

    normalized_words = []
    for w in words:
        # Strip non-alphanumeric at the ends just in case
        w = re.sub(r"^[^a-z0-9]+|[^a-z0-9]+$", "", w)
        if not w:
            continue
        # Replace abbreviations
        w = abbrevs.get(w, w)
        # Drop pack words
        if w not in pack_words:
            normalized_words.append(w)

    return " ".join(normalized_words).strip()


def match_item(
    name: str, reference_items: Dict[str, ReferencePriceRecord], threshold: float = 80.0
) -> MatchResult:
    """
    Matches the item name to reference items using rapidfuzz
    with a configurable threshold.
    Returns the best match, score and the reason.
    """
    if not reference_items:
        return MatchResult(
            best_match=None, score=0.0, reason="No reference items provided"
        )

    normalized_input = normalise_item_name(name)
    if not normalized_input:
        return MatchResult(
            best_match=None, score=0.0, reason="Normalized name is empty"
        )

    choices = {
        key: normalise_item_name(record.display_name)
        for key, record in reference_items.items()
    }

    # Process choices keeping the keys
    # process.extractOne returns (match_string, score, choice_key)
    # for dicts in newer rapidfuzz
    result = process.extractOne(normalized_input, choices, scorer=fuzz.token_sort_ratio)

    if result:
        match_str, score, match_key = result
        if score >= threshold:
            best_match = reference_items[match_key]
            reason = (
                f"Matched based on normalized names with score {score:.2f} "
                f"(threshold: {threshold})"
            )
            return MatchResult(best_match=best_match, score=score, reason=reason)
        else:
            reason = f"Best match score {score:.2f} is below threshold {threshold}"
            return MatchResult(best_match=None, score=score, reason=reason)

    return MatchResult(best_match=None, score=0.0, reason="No match found")


def match_cpt_codes(
    items: List[Dict[str, Any]],
) -> List[Dict[str, Optional[str]]]:
    """Match line item descriptions to standard billing procedure codes.

    Args:
        items: List of line items with descriptions.

    Returns:
        List of matching billing codes and confidence scores.
    """
    # Stub implementation - to be implemented with scikit-learn and pandas
    return []
