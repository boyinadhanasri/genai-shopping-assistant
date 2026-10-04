"""
Thin wrapper so the API layer has one stable import regardless of
which extractor is active. Right now this delegates to the rule-based
extractor in query_understanding/intent_extraction.py. To switch to
the GPT-4o mini version, change the import below to
query_understanding.llm_parser — nothing else needs to change.
"""

from backend.models.product import QuerySlots
from query_understanding.intent_extraction import extract_slots as _extract_slots


def extract_slots(query: str, category: str) -> QuerySlots:
    return _extract_slots(query, category)
