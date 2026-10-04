"""
LLM-based slot extraction (GPT-4o mini, function-calling) — the
upgrade path from query_understanding/intent_extraction.py's regex
version, matching the "Query understanding layer" in the architecture
doc.

Needs an OPENAI_API_KEY environment variable and the `openai` package
(not in requirements.txt yet — add `pip install openai` when you wire
this in for real).

To switch the project over: change the one import in
backend/services/intent.py from
    from query_understanding.intent_extraction import extract_slots
to
    from query_understanding.llm_parser import extract_slots
Everything downstream (catalog search, ranking, comparison) keeps
working unchanged, because both functions return the same QuerySlots
shape.
"""

import json
import os
from backend.models.product import QuerySlots
from query_understanding.intent_extraction import extract_slots as rule_based_extract_slots

SLOT_FUNCTION_SCHEMA = {
    "name": "extract_shopping_slots",
    "description": "Extract structured shopping intent from a natural-language product query.",
    "parameters": {
        "type": "object",
        "properties": {
            "category": {"type": "string", "description": "Product category, e.g. Electronics, Mobiles, Appliances"},
            "budget_max": {"type": "number", "description": "Maximum budget mentioned, if any"},
            "brand": {"type": "string", "description": "Specific brand mentioned, if any"},
        },
        "required": ["category"],
    },
}

SYSTEM_PROMPT = (
    "You extract shopping search slots from a user's message. "
    "Only fill in values the user actually stated or clearly implied — "
    "never guess a budget or brand that wasn't mentioned."
)


def extract_slots(query: str, category_hint: str) -> QuerySlots:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        # No key configured — fall back to the rule-based extractor so
        # the pipeline still runs end-to-end during development.
        return rule_based_extract_slots(query, category_hint)

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        tools=[{"type": "function", "function": SLOT_FUNCTION_SCHEMA}],
        tool_choice={"type": "function", "function": {"name": "extract_shopping_slots"}},
    )

    args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
    return QuerySlots(
        category=args.get("category", category_hint),
        budget_max=args.get("budget_max"),
        raw_query=query,
    )
